# -*- coding: utf-8 -*-
"""
producir_lote.py — motor de producción de un lote de piezas, de punta a punta.

Por qué existe: hasta el lote 21 este pipeline se reescribía a mano en una carpeta
temporal en cada lote (build.py + render_all.py + instalar.py, con los datos del
lote incrustados en el propio .py). Eso significaba volver a emitir ~250 líneas de
lógica cada vez, perder los scripts cuando se limpiaba Temp, y arrastrar todo ese
texto en el contexto de la conversación. Acá la lógica vive en el repo y es fija;
lo único que cambia por lote es un `lote.json` de DATOS PUROS.

El diseño no cambia: se usan los mismos templates de `POST/_template/`, el mismo
CONFIG, el mismo Chrome headless a 1080x1350. Este script es un refactor de
fontanería, no un rediseño. Los PNG que produce son byte-idénticos a los del
pipeline viejo (verificado contra lote-21 con --verificar).

Uso típico (un lote entero):

    python producir_lote.py lote.json --todo

Por etapas (para depurar o rehacer solo una parte):

    python producir_lote.py lote.json --validar     # chequea el JSON, no renderiza
    python producir_lote.py lote.json --build       # arma los work.html
    python producir_lote.py lote.json --render      # Chrome headless -> salida/*.png
    python producir_lote.py lote.json --qc          # contact sheet + copias reducidas
    python producir_lote.py lote.json --instalar    # copia al proyecto + post.txt + pieza.json

`--verificar <dir>` compara los PNG recién renderizados contra los de otra corrida
(o contra los ya instalados en el proyecto) y reporta diferencias byte a byte.

IMPORTANTE sobre resolución: el render SIEMPRE sale a 1080x1350, que es el archivo
que se publica. Las imágenes reducidas de `--qc` son copias aparte, para revisión
visual barata; nunca reemplazan al PNG final ni se instalan en el proyecto.
"""
import argparse
import functools
import hashlib
import http.server
import json
import os
import re
import shutil
import socketserver
import subprocess
import sys
import threading

# ---------------------------------------------------------------------------
# Rutas del proyecto. Se resuelven subiendo desde este script:
#   plugin/post-studio/skills/crear-imagen/scripts/producir_lote.py
#   -> raíz del proyecto son 5 niveles arriba.
# ---------------------------------------------------------------------------
AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", "..", "..", "..", ".."))

# La consola de Windows abre en codepage ANSI y rompe tildes/emoji al imprimir.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

CHROME_CANDIDATOS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "/usr/bin/google-chrome",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
]

# Etiquetas de las filas de audio/subtítulo. El lote.json solo trae los códigos
# (["MX","JP","ES"]) y acá se resuelven los labels — así no se pueden escribir mal
# ni quedar inconsistentes entre piezas. Los códigos válidos son los que la
# plantilla sabe dibujar (FLAG_COLORS en post-template.html): si aparece un idioma
# nuevo hay que agregar el gradiente ahí ANTES de usarlo acá.
ROW_LABELS = {
    "MX": "Audio Esp. Latino",
    "US": "Audio Inglés",
    "JP": "Audio Japonés",
    "KR": "Audio Coreano",
    "BR": "Audio Portugués",
    "IT": "Audio Italiano",
    "DE": "Audio Alemán",
    "IN": "Audio Hindi",
    "CN": "Audio Chino",
    "ES": "Subtítulo Español",
}

# Nombre del idioma como se escribe en la línea del caption, con su conjunción.
# "e" antes de sonido /i/ (inglés, italiano, hindi), "y" en el resto — verificado
# contra las 202 piezas ya publicadas.
IDIOMA_CAPTION = {
    "US": ("e", "inglés"),
    "JP": ("y", "japonés"),
    "KR": ("y", "coreano"),
    "BR": ("y", "portugués"),
    "IT": ("e", "italiano"),
    "DE": ("y", "alemán"),
    "IN": ("e", "hindi"),
    "CN": ("y", "chino"),
}

FORMATOS = {
    "feed_portrait": (1080, 1350),
    "feed_square": (1080, 1080),
    "reel_story": (1080, 1920),
}


# ---------------------------------------------------------------------------
# utilidades
# ---------------------------------------------------------------------------
def leer_texto(ruta):
    with open(ruta, encoding="utf-8") as fh:
        return fh.read()


def escribir_texto(ruta, contenido):
    # UTF-8 sin BOM, siempre — el template rompe tildes/emoji con cualquier otra cosa.
    with open(ruta, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(contenido)


def cargar_marca():
    cfg = json.loads(leer_texto(os.path.join(RAIZ, "brand.config.json")))
    cfg["_contentRoot"] = os.path.join(RAIZ, cfg.get("contentRoot", "POST"))
    cfg["_logo"] = os.path.join(RAIZ, cfg["logoFolder"].replace("/", os.sep), cfg["logoFile"])
    return cfg


def buscar_chrome():
    for c in CHROME_CANDIDATOS:
        if os.path.isfile(c):
            return c
    ruta = shutil.which("chrome") or shutil.which("google-chrome")
    if ruta:
        return ruta
    raise SystemExit("No se encontró Chrome. Pasalo con --chrome <ruta>.")


def md5(ruta):
    h = hashlib.md5()
    with open(ruta, "rb") as fh:
        for bloque in iter(lambda: fh.read(65536), b""):
            h.update(bloque)
    return h.hexdigest()


def js(valor):
    """Serializa a literal JS. json.dumps sirve: JSON es subconjunto de JS."""
    return json.dumps(valor, ensure_ascii=False)


def reemplazar_config(html, config_js):
    patron = re.compile(r"const CONFIG = \{.*?\n\};\n", re.S)
    nuevo, n = patron.subn("const CONFIG = " + config_js + ";\n", html, count=1)
    if n != 1:
        raise SystemExit("No se pudo reemplazar el bloque CONFIG del template.")
    return nuevo


def filas(codigos):
    return [{"code": c, "label": ROW_LABELS[c]} for c in codigos]


def linea_audio(codigos):
    """La línea '🎧 Audio ... | 📺 Subtítulos ...' del caption, derivada de las
    mismas filas que van en la imagen. Así imagen y texto no pueden discrepar."""
    extras = [c for c in codigos if c in IDIOMA_CAPTION]
    if not extras:
        # original en español: solo audio latino, sin subtítulo (regla de CLAUDE.md)
        return "🎧 Audio español latino"
    conj, nombre = IDIOMA_CAPTION[extras[0]]
    return "🎧 Audio español latino %s %s | 📺 Subtítulos en español" % (conj, nombre)


def tipo_pieza(p):
    return p.get("tipoPieza") or ("carrusel" if len(p["arte"]) > 1 else "imagen")


def carpeta_posters(marca, p):
    return os.path.join(marca["_contentRoot"], "assets", "posters", p.get("posterDir", p["slug"]))


# ---------------------------------------------------------------------------
# 1. validar — atrapa errores ANTES de renderizar
# ---------------------------------------------------------------------------
def validar(lote, marca, estricto=True):
    """Cada error que se atrapa acá es un ciclo completo de render+revisión+arreglo
    que no hay que pagar después. Las reglas son las de CLAUDE.md."""
    errores, avisos = [], []
    prohibidas = [m.lower() for m in marca.get("forbiddenMentions", [])]
    slugs = set()

    for i, p in enumerate(lote["piezas"]):
        eti = "pieza[%d] %s" % (i, p.get("slug", "?"))

        for campo in ("slug", "categoria", "titulo", "vtxIds", "rows", "arte", "sinopsis", "post"):
            if campo not in p:
                errores.append("%s: falta el campo '%s'" % (eti, campo))
        if errores and campo not in p:
            continue

        if p["slug"] in slugs:
            errores.append("%s: slug duplicado en el lote" % eti)
        slugs.add(p["slug"])

        if p["categoria"] not in ("series", "peliculas"):
            errores.append("%s: categoria debe ser 'series' o 'peliculas', vino '%s'" % (eti, p["categoria"]))

        # --- filas de audio/subtítulo ---
        codigos = p["rows"]
        for c in codigos:
            if c not in ROW_LABELS:
                errores.append("%s: código de fila '%s' desconocido. Si es un idioma nuevo, "
                               "agregá su gradiente en FLAG_COLORS de post-template.html primero." % (eti, c))
        if "MX" not in codigos:
            errores.append("%s: toda pieza lleva la fila MX (Audio Esp. Latino)" % eti)
        extranjero = [c for c in codigos if c in IDIOMA_CAPTION and c != "US"]
        if extranjero and "ES" not in codigos:
            errores.append("%s: idioma original no angloparlante (%s) exige SIEMPRE las 3 filas "
                           "(MX + original + ES), sin importar audioDual — regla de CLAUDE.md"
                           % (eti, ",".join(extranjero)))
        if len([c for c in codigos if c in IDIOMA_CAPTION]) > 1:
            avisos.append("%s: más de un idioma de audio además del latino (%s); la línea del "
                          "caption solo nombra el primero" % (eti, codigos))

        # --- pósters del arte ---
        pdir = carpeta_posters(marca, p)
        for it in p["arte"]:
            for campo in ("id", "titulo", "poster"):
                if campo not in it:
                    errores.append("%s: item de arte sin '%s'" % (eti, campo))
            ruta = os.path.join(pdir, it.get("poster", ""))
            if not os.path.isfile(ruta):
                errores.append("%s: no existe el póster %s" % (eti, ruta))

        # --- tira de la ficha de sinopsis ---
        sin = p["sinopsis"]
        tira = sin.get("tira", [])
        if len(tira) < 2:
            errores.append("%s: la tira de la ficha necesita MÍNIMO 2 cuadros (vino %d). Con 1 solo "
                           "la tira queda corta y rompe el diseño — usá otra variante del mismo "
                           "póster antes que bajar a 1." % (eti, len(tira)))
        if len(tira) > 4:
            avisos.append("%s: la tira trae %d cuadros; el diseño está pensado para 2 a 4" % (eti, len(tira)))
        if len(set(tira)) != len(tira):
            errores.append("%s: la tira repite la misma imagen en dos cuadros" % eti)
        for f in tira:
            if not os.path.isfile(os.path.join(pdir, f)):
                errores.append("%s: no existe la imagen de tira %s" % (eti, os.path.join(pdir, f)))
        if sin.get("score") is not None and not isinstance(sin["score"], int):
            errores.append("%s: score debe ser entero (78) o null, vino %r" % (eti, sin["score"]))
        for campo in ("tagline", "body", "meta"):
            if not sin.get(campo):
                errores.append("%s: sinopsis sin '%s'" % (eti, campo))
        if sin.get("body") and len(sin["body"]) > 900:
            avisos.append("%s: el body de la ficha tiene %d caracteres; arriba de ~750 suele "
                          "no entrar y el template lo achica" % (eti, len(sin["body"])))

        # --- texto del post ---
        post = p["post"]
        for campo in ("hook", "desc", "clasif", "invit", "engage"):
            if not post.get(campo):
                errores.append("%s: post sin '%s'" % (eti, campo))

        texto_junto = " ".join([p["titulo"], sin.get("tagline", ""), sin.get("body", "")] +
                               [str(post.get(c, "")) for c in ("hook", "desc", "clasif", "invit", "engage")])
        for m in prohibidas:
            if m in texto_junto.lower():
                errores.append("%s: menciona una plataforma prohibida ('%s') en el texto" % (eti, m))
        if "#" in texto_junto:
            errores.append("%s: el texto trae hashtags — desde 2026-09-12 los posts no llevan "
                           "línea de hashtags ni menciones de Costa Rica" % eti)
        if post.get("engage") and not post["engage"].rstrip().endswith("👇"):
            avisos.append("%s: el post no cierra con la pregunta de engagement + 👇" % eti)

    if avisos:
        print("AVISOS:")
        for a in avisos:
            print("  ! " + a)
    if errores:
        print("ERRORES:")
        for e in errores:
            print("  x " + e)
        if estricto:
            raise SystemExit("\n%d error(es). No se renderiza nada hasta corregirlos." % len(errores))
    if not errores and not avisos:
        print("validación OK — %d piezas, %d imágenes a renderizar"
              % (len(lote["piezas"]), sum(len(p["arte"]) + 1 for p in lote["piezas"])))
    return not errores


# ---------------------------------------------------------------------------
# 1b. validar contra TMDB — el chequeo que atrapa el incidente "Anna"
# ---------------------------------------------------------------------------
def cargar_catalogo(marca):
    ruta = os.path.join(marca["_contentRoot"], "catalogo.json")
    d = json.loads(leer_texto(ruta))
    return {t["vtxId"]: t for t in d.get("titulos", []) if t.get("vtxId")}


def _anios_de_meta(meta):
    """Extrae los años que declara la ficha: ['2017-2021'] -> (2017, 2021)."""
    años = []
    for chip in meta:
        años += [int(x) for x in re.findall(r"\b(19\d{2}|20\d{2})\b", str(chip))]
    return (min(años), max(años)) if años else (None, None)


def validar_contra_tmdb(lote, marca, estricto=True):
    """Compara lo que el lote.json DICE contra lo que TMDB dice de ese tmdbId.

    Existe por el incidente "Anna" (2026-09-12): el tmdbId y el póster eran los
    correctos, pero el texto describía otro show que solo compartía el nombre.
    Ninguna regla mecánica lo atrapaba porque nadie cruzaba el texto contra la
    ficha real. Dos cruces que sí son mecánicos:

      - el AÑO que declara la ficha vs el año real del tmdbId;
      - el IDIOMA ORIGINAL de TMDB vs las filas de audio declaradas, que es la
        regla que se violó en 17 piezas ya publicadas.
    """
    sys.path.insert(0, AQUI)
    import ficha_tmdb

    catalogo = cargar_catalogo(marca)
    errores, avisos = [], []
    cache = {}

    for p in lote["piezas"]:
        eti = "%s" % p["slug"]
        codigos_audio = [c for c in p["rows"] if c in IDIOMA_CAPTION]
        lo_meta, hi_meta = _anios_de_meta(p["sinopsis"].get("meta", []))
        idiomas_vistos = []

        for it in p["arte"]:
            vtx = it.get("vtxId")
            if not vtx:
                continue
            cat = catalogo.get(vtx)
            if not cat:
                errores.append("%s: el vtxId %s no está en el catálogo" % (eti, vtx))
                continue
            tmdb_id = cat.get("tmdbId")
            if not tmdb_id:
                avisos.append("%s: %s no trae tmdbId en el catálogo, no se puede verificar" % (eti, vtx))
                continue
            tipo = "tv" if str(cat.get("tipo", "")).lower().startswith("serie") else "movie"

            clave = (str(tmdb_id), tipo)
            if clave not in cache:
                cache[clave] = ficha_tmdb.ficha(tmdb_id, tipo)
            f = cache[clave]

            if f.get("error"):
                avisos.append("%s: no se pudo leer TMDB para %s (%s) — %s"
                              % (eti, vtx, tmdb_id, f["error"]))
                continue

            # --- año: el cruce que atrapa "se describió otro show" ---
            if f.get("anio"):
                if cat.get("anio") and int(cat["anio"]) != f["anio"]:
                    avisos.append("%s: el catálogo dice año %s para %s pero TMDB %s dice %d "
                                  "(dato del catálogo, revisar)"
                                  % (eti, cat["anio"], vtx, tmdb_id, f["anio"]))
                if lo_meta is not None and not (lo_meta <= f["anio"] <= hi_meta):
                    errores.append(
                        "%s: la ficha declara %s pero TMDB %s (%s) es de %d. O el texto "
                        "describe OTRO título que comparte el nombre (incidente Anna), o el "
                        "año de la ficha está mal. Verificá %s antes de seguir."
                        % (eti, p["sinopsis"]["meta"], tmdb_id, f.get("titulo"), f["anio"], f["url"]))

            # --- idioma original: determina las filas de audio, sin adivinar ---
            idioma = f.get("idiomaOriginal")
            if not idioma:
                avisos.append("%s: TMDB no expuso el idioma original de %s" % (eti, vtx))
                continue
            idiomas_vistos.append((vtx, idioma))
            codigo, conocido = ficha_tmdb.codigo_de_idioma(idioma)
            if not conocido:
                errores.append("%s: idioma original '%s' (TMDB %s) no está mapeado. Agregá su "
                               "gradiente en FLAG_COLORS de post-template.html y el mapeo en "
                               "ficha_tmdb.py antes de usarlo — nunca aproximes con otra bandera."
                               % (eti, idioma, tmdb_id))
                continue
            if codigo is None:
                # original en español: solo Audio Esp. Latino
                if codigos_audio:
                    errores.append("%s: TMDB dice idioma original %s (español) pero las filas "
                                   "declaran audio %s. Un título en español solo lleva MX."
                                   % (eti, idioma, codigos_audio))
            elif codigo == "US":
                if codigos_audio and codigos_audio != ["US"]:
                    errores.append("%s: TMDB dice idioma original inglés pero las filas declaran %s"
                                   % (eti, codigos_audio))
            else:
                if codigo not in codigos_audio:
                    errores.append(
                        "%s: TMDB dice idioma original %s (código %s) pero las filas declaran %s. "
                        "Un título no angloparlante lleva SIEMPRE las 3 filas: MX + %s + ES, "
                        "sin importar audioDual." % (eti, idioma, codigo, p["rows"], codigo))
                elif "ES" not in p["rows"]:
                    errores.append("%s: idioma original %s exige también la fila ES (subtítulo)"
                                   % (eti, idioma))

        if len({i for _, i in idiomas_vistos}) > 1:
            avisos.append("%s: los títulos de la pieza no comparten idioma original (%s); "
                          "revisá que las filas sirvan para todos" % (eti, idiomas_vistos))

    if avisos:
        print("AVISOS (TMDB):")
        for a in avisos:
            print("  ! " + a)
    if errores:
        print("ERRORES (TMDB):")
        for e in errores:
            print("  x " + e)
        if estricto:
            raise SystemExit("\n%d error(es) de verificación contra TMDB." % len(errores))
    if not errores:
        print("verificación TMDB OK — %d fichas consultadas" % len(cache))
    return not errores


# ---------------------------------------------------------------------------
# 2. build — arma los work.html en el directorio de trabajo
# ---------------------------------------------------------------------------
CONFIG_ARTE = """{
  format: %(format)s,
  layout: 'full_bleed',
  posterImage: './poster.jpg',
  title: %(title)s,
  titleFont: 'font-sans',
  titleCase: 'case-upper',
  rows: %(rows)s,
  badges: ['1080p'],
  logo: './logo.png',
  site: %(site)s
}"""

CONFIG_SINOPSIS = """{
  format: %(format)s,
  title: %(title)s,
  tagline: %(tagline)s,
  body: %(body)s,
  meta: %(meta)s,
  score: %(score)s,
  scoreLabel: 'de aprobación',
  images: %(images)s,
  accent: 'auto',
  logo: './logo.png',
  site: %(site)s
}"""


def build(lote, marca, work):
    tpl_arte = leer_texto(os.path.join(marca["_contentRoot"], "_template", "post-template.html"))
    tpl_sin = leer_texto(os.path.join(marca["_contentRoot"], "_template", "sinopsis-template.html"))
    render_dir = os.path.join(work, "render")
    if os.path.isdir(render_dir):
        shutil.rmtree(render_dir)
    os.makedirs(render_dir)

    formato = lote.get("format", "feed_portrait")
    site = marca["website"]
    destinos = []

    # Las carpetas de render se numeran (r000, r001...) en vez de usar el slug:
    # Windows corta en 260 caracteres de ruta y "<slug>--<slug>-arte" dentro de un
    # scratchpad de sesión ya se pasa. El nombre real viaja en renders.txt.
    def nueva_carpeta():
        d = os.path.join(render_dir, "r%03d" % len(destinos))
        os.makedirs(d)
        return d

    for p in lote["piezas"]:
        pdir = carpeta_posters(marca, p)

        for it in p["arte"]:
            nombre = "%s--%s-arte" % (p["slug"], it["id"])
            d = nueva_carpeta()
            shutil.copy(marca["_logo"], os.path.join(d, "logo.png"))
            shutil.copy(os.path.join(pdir, it["poster"]), os.path.join(d, "poster.jpg"))
            cfg = CONFIG_ARTE % dict(format=js(formato), title=js(it["titulo"]),
                                     rows=js(filas(p["rows"])), site=js(site))
            escribir_texto(os.path.join(d, "work.html"), reemplazar_config(tpl_arte, cfg))
            destinos.append((os.path.basename(d), nombre))

        sin = p["sinopsis"]
        nombre = "%s--sinopsis" % p["slug"]
        d = nueva_carpeta()
        shutil.copy(marca["_logo"], os.path.join(d, "logo.png"))
        rutas_img = []
        for i, f in enumerate(sin["tira"], start=1):
            dst = "img%d.jpg" % i
            shutil.copy(os.path.join(pdir, f), os.path.join(d, dst))
            rutas_img.append("./" + dst)
        cfg = CONFIG_SINOPSIS % dict(format=js(formato), title=js(p["titulo"]),
                                     tagline=js(sin["tagline"]), body=js(sin["body"]),
                                     meta=js(sin["meta"]),
                                     score=("null" if sin.get("score") is None else str(sin["score"])),
                                     images=js(rutas_img), site=js(site))
        escribir_texto(os.path.join(d, "work.html"), reemplazar_config(tpl_sin, cfg))
        destinos.append((os.path.basename(d), nombre))

    # mapa.json traduce el nombre lógico de cada render ("bad-boys--bb1-arte") al
    # id corto de carpeta/archivo ("r012"). Todo lo que toca el disco usa el id
    # corto; los nombres largos solo viven acá. Sin esto, un slug largo repetido
    # ("los-chicos-...--los-chicos-...-arte.png") revienta el límite de 260
    # caracteres de Windows y Chrome falla en silencio, sin escribir el PNG.
    escribir_texto(os.path.join(work, "mapa.json"),
                   json.dumps({n: c for c, n in destinos}, ensure_ascii=False, indent=1) + "\n")
    escribir_texto(os.path.join(work, "renders.txt"),
                   "".join("%s\t%s\n" % (c, n) for c, n in destinos))
    print("build OK — %d render(s) preparados en %s" % (len(destinos), render_dir))
    return destinos


def cargar_mapa(work):
    return json.loads(leer_texto(os.path.join(work, "mapa.json")))


# ---------------------------------------------------------------------------
# 3. render — Chrome headless contra un servidor local efímero
# ---------------------------------------------------------------------------
class _ServidorSilencioso(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


class _HandlerSilencioso(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def render(lote, marca, work, chrome=None, puerto=0):
    """El servidor corre EN ESTE PROCESO, en un hilo daemon, y se apaga al terminar.
    Así se evita el problema clásico de dejar un `python -m http.server` vivo
    bloqueando la carpeta scratch en Windows."""
    render_dir = os.path.join(work, "render")
    salida_dir = os.path.join(work, "salida")
    os.makedirs(salida_dir, exist_ok=True)
    destinos = [tuple(l.split("\t"))
                for l in leer_texto(os.path.join(work, "renders.txt")).splitlines() if l.strip()]

    chrome = chrome or buscar_chrome()
    w, h = FORMATOS[lote.get("format", "feed_portrait")]

    handler = functools.partial(_HandlerSilencioso, directory=render_dir)
    srv = _ServidorSilencioso(("127.0.0.1", puerto), handler)
    puerto_real = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()

    # --user-data-dir tiene que ser una ruta CORTA: las largas de AppData\Local\Temp
    # fallan con "Access is denied" por longitud/permisos.
    perfil = os.environ.get("CHROME_PROFILE_DIR", "C:/ct-lote/profile" if os.name == "nt" else "/tmp/ct-lote")
    fallidos = []
    try:
        for carpeta, nombre in destinos:
            # --screenshot exige ruta ABSOLUTA y con "/" — con ruta relativa Chrome
            # sale con código 0, no avisa nada y no escribe el archivo.
            out = os.path.join(salida_dir, carpeta + ".png").replace("\\", "/")
            cmd = [chrome, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
                   "--user-data-dir=" + perfil,
                   "--screenshot=" + out,
                   "--window-size=%d,%d" % (w, h),
                   "--force-device-scale-factor=1",
                   # obligatorio: el color dominante y el ajuste del texto se calculan
                   # de forma asíncrona; sin esto la captura sale en blanco o a medias.
                   "--virtual-time-budget=4000",
                   "http://127.0.0.1:%d/%s/work.html" % (puerto_real, carpeta)]
            subprocess.run(cmd, capture_output=True)
            tam = os.path.getsize(out) if os.path.isfile(out) else 0
            if tam < 10000:
                fallidos.append(nombre)
            print("  %-60s %8d bytes" % (nombre, tam))
    finally:
        srv.shutdown()
        srv.server_close()

    if fallidos:
        raise SystemExit("Renders fallidos o vacíos: %s" % ", ".join(fallidos))
    print("render OK — %d PNG a %dx%d en %s" % (len(destinos), w, h, salida_dir))


# ---------------------------------------------------------------------------
# 4. qc — contact sheet + copias reducidas (SOLO para revisión, nunca se instalan)
# ---------------------------------------------------------------------------
def qc(lote, work, ancho_celda=270, columnas=6, ancho_individual=600):
    from PIL import Image

    salida_dir = os.path.join(work, "salida")
    qc_dir = os.path.join(work, "qc")
    os.makedirs(qc_dir, exist_ok=True)
    mapa = cargar_mapa(work)
    # orden de render (r000, r001...), que es el orden del lote.json
    orden = sorted(mapa.items(), key=lambda kv: kv[1])
    orden = [(n, c) for n, c in orden if os.path.isfile(os.path.join(salida_dir, c + ".png"))]
    if not orden:
        raise SystemExit("No hay PNG en salida/ — corré --render primero.")

    # Copias individuales reducidas: para confirmar que el texto entró y que las
    # filas no se cortan alcanza con 600px de ancho, a un tercio del costo de leer
    # el PNG de 1080. El PNG de 1080 queda intacto — es el que se publica.
    for nombre, c in orden:
        im = Image.open(os.path.join(salida_dir, c + ".png")).convert("RGB")
        prop = ancho_individual / im.width
        im = im.resize((ancho_individual, int(im.height * prop)), Image.LANCZOS)
        im.save(os.path.join(qc_dir, c + ".jpg"), quality=88)

    # Contact sheet del lote entero, para revisar todo de una sola lectura.
    filas_n = (len(orden) + columnas - 1) // columnas
    muestra = Image.open(os.path.join(salida_dir, orden[0][1] + ".png"))
    alto_celda = int(ancho_celda * muestra.height / muestra.width)
    hoja = Image.new("RGB", (columnas * ancho_celda, filas_n * alto_celda), (20, 20, 24))
    for i, (nombre, c) in enumerate(orden):
        im = Image.open(os.path.join(salida_dir, c + ".png")).convert("RGB").resize(
            (ancho_celda, alto_celda), Image.LANCZOS)
        hoja.paste(im, ((i % columnas) * ancho_celda, (i // columnas) * alto_celda))
    hoja_path = os.path.join(qc_dir, "contact_sheet.jpg")
    hoja.save(hoja_path, quality=86)

    print("qc OK")
    print("  contact sheet : %s  (%dx%d, %d celdas, %d por fila)"
          % (hoja_path, hoja.width, hoja.height, len(orden), columnas))
    print("  individuales  : %s%s<id>.jpg  (%dpx de ancho)" % (qc_dir, os.sep, ancho_individual))
    print("  ORDEN del contact sheet (izq->der, arriba->abajo):")
    for i, (nombre, c) in enumerate(orden):
        print("    celda %2d = %s  (%s)" % (i + 1, nombre, c))


# ---------------------------------------------------------------------------
# 5. instalar — copia al proyecto y escribe post.txt + pieza.json
# ---------------------------------------------------------------------------
def instalar(lote, marca, work):
    salida_dir = os.path.join(work, "salida")
    mapa = cargar_mapa(work)
    cta = marca["cta"]
    fecha = lote["fecha"]
    instaladas = []

    for p in lote["piezas"]:
        destino = os.path.join(marca["_contentRoot"], "social", p["categoria"], p["slug"])
        img_dir = os.path.join(destino, "images")
        os.makedirs(img_dir, exist_ok=True)

        imagenes = []
        for idx, it in enumerate(p["arte"], start=1):
            src = os.path.join(salida_dir, mapa["%s--%s-arte" % (p["slug"], it["id"])] + ".png")
            nombre = "%02d-%s.png" % (idx, it["id"])
            shutil.copy(src, os.path.join(img_dir, nombre))
            entrada = {"archivo": "%s/social/%s/%s/images/%s"
                                  % (marca.get("contentRoot", "POST"), p["categoria"], p["slug"], nombre),
                       "tipo": "arte"}
            if it.get("vtxId"):
                entrada["vtxId"] = it["vtxId"]
            imagenes.append(entrada)

        n_sin = len(p["arte"]) + 1
        nombre_sin = "%02d-sinopsis-%s.png" % (n_sin, p["slug"])
        shutil.copy(os.path.join(salida_dir, mapa["%s--sinopsis" % p["slug"]] + ".png"),
                    os.path.join(img_dir, nombre_sin))
        ruta_sin = "%s/social/%s/%s/images/%s" % (marca.get("contentRoot", "POST"),
                                                  p["categoria"], p["slug"], nombre_sin)
        imagenes.append({"archivo": ruta_sin, "tipo": "sinopsis"})

        # post.txt — estructura fija de CLAUDE.md: título, hook, CTA, info técnica,
        # descripción, clasificación, invitación, pregunta de engagement. Sin hashtags.
        post = p["post"]
        escribir_texto(os.path.join(destino, "post.txt"), "\n".join([
            p["titulo"].upper(), "",
            post["hook"], "",
            cta, "",
            linea_audio(p["rows"]), "",
            post["desc"], "",
            post["clasif"].rstrip(".") + ".", "",
            post["invit"], "",
            post["engage"],
        ]))

        tp = tipo_pieza(p)
        pieza = {
            "slug": p["slug"],
            "tipo": tp,
            "titulo": p["titulo"],
            "grupo": ({"clase": "coleccion", "valor": p["titulo"]} if tp == "carrusel"
                      else {"clase": "titulo", "valor": p["vtxIds"][0]}),
            "vtxIds": p["vtxIds"],
            "creada": fecha,
            "imagenes": imagenes,
            "posters": {"origen": "tmdb",
                        "carpeta": "%s/assets/posters/%s" % (marca.get("contentRoot", "POST"),
                                                             p.get("posterDir", p["slug"]))},
            "sinopsis": {"creada": True, "archivo": ruta_sin},
            "texto": {"creado": True,
                      "archivo": "%s/social/%s/%s/post.txt" % (marca.get("contentRoot", "POST"),
                                                              p["categoria"], p["slug"])},
            "publicado": {"hecho": False, "fecha": None, "plataformas": []},
        }
        if p.get("nota"):
            pieza["nota"] = p["nota"]
        escribir_texto(os.path.join(destino, "pieza.json"),
                       json.dumps(pieza, ensure_ascii=False, indent=2) + "\n")
        instaladas.append(p["slug"])
        print("  instalada: %-45s (%d imágenes)" % (p["slug"], len(imagenes)))

    print("instalar OK — %d piezas" % len(instaladas))


# ---------------------------------------------------------------------------
# 6. verificar — regresión contra otra corrida o contra lo ya instalado
# ---------------------------------------------------------------------------
def verificar(lote, marca, work, referencia):
    """Compara los PNG recién renderizados contra una referencia. Sirve para probar
    que un cambio en el pipeline NO alteró el diseño."""
    salida_dir = os.path.join(work, "salida")
    mapa = cargar_mapa(work)
    iguales = distintos = faltantes = 0

    for p in lote["piezas"]:
        pares = [("%s--%s-arte" % (p["slug"], it["id"]), "%02d-%s.png" % (i, it["id"]))
                 for i, it in enumerate(p["arte"], start=1)]
        pares.append(("%s--sinopsis" % p["slug"],
                      "%02d-sinopsis-%s.png" % (len(p["arte"]) + 1, p["slug"])))
        for nuevo, instalado in pares:
            a = os.path.join(salida_dir, mapa[nuevo] + ".png")
            # La referencia puede ser otra carpeta salida/ (corrida anterior, con el
            # nombre largo del pipeline viejo) o el proyecto ya instalado.
            b = os.path.join(referencia, nuevo + ".png")
            if not os.path.isfile(b):
                b = os.path.join(marca["_contentRoot"], "social", p["categoria"], p["slug"],
                                 "images", instalado)
            if not os.path.isfile(a) or not os.path.isfile(b):
                print("  ? falta  %s" % nuevo)
                faltantes += 1
                continue
            if md5(a) == md5(b):
                iguales += 1
            else:
                distintos += 1
                print("  X DIFIERE %-55s (%d vs %d bytes)"
                      % (nuevo, os.path.getsize(a), os.path.getsize(b)))

    print("verificar: %d idénticos, %d distintos, %d faltantes" % (iguales, distintos, faltantes))
    return distintos == 0 and faltantes == 0


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("lote", help="ruta al lote.json con los datos del lote")
    ap.add_argument("--work", help="directorio de trabajo (default: la carpeta del lote.json)")
    ap.add_argument("--validar", action="store_true")
    ap.add_argument("--verificar-tmdb", action="store_true", dest="vtmdb",
                    help="cruza año e idioma original de cada tmdbId contra el lote.json")
    ap.add_argument("--sin-tmdb", action="store_true",
                    help="con --todo, saltea la verificación contra TMDB (no recomendado)")
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--render", action="store_true")
    ap.add_argument("--qc", action="store_true")
    ap.add_argument("--instalar", action="store_true")
    ap.add_argument("--todo", action="store_true", help="validar + build + render + qc + instalar")
    ap.add_argument("--verificar", metavar="DIR", help="compara salida/ contra DIR (o contra lo instalado)")
    ap.add_argument("--chrome", help="ruta a chrome.exe si no está en los lugares habituales")
    ap.add_argument("--sin-instalar", action="store_true", help="con --todo, no copia al proyecto")
    args = ap.parse_args()

    ruta_lote = os.path.abspath(args.lote)
    lote = json.loads(leer_texto(ruta_lote))
    work = os.path.abspath(args.work) if args.work else os.path.dirname(ruta_lote)
    marca = cargar_marca()
    lote.setdefault("fecha", "")

    etapas = dict(validar=args.validar, vtmdb=args.vtmdb, build=args.build,
                  render=args.render, qc=args.qc, instalar=args.instalar)
    if args.todo:
        etapas = dict(validar=True, vtmdb=not args.sin_tmdb, build=True, render=True,
                      qc=True, instalar=not args.sin_instalar)
    if not any(etapas.values()) and not args.verificar:
        etapas["validar"] = True

    if etapas.get("validar"):
        validar(lote, marca)
    if etapas.get("vtmdb"):
        validar_contra_tmdb(lote, marca)
    if etapas.get("build"):
        build(lote, marca, work)
    if etapas.get("render"):
        render(lote, marca, work, chrome=args.chrome)
    if args.verificar:
        ok = verificar(lote, marca, work, os.path.abspath(args.verificar))
        if not ok:
            sys.exit(1)
    if etapas.get("qc"):
        qc(lote, work)
    if etapas.get("instalar"):
        if not lote.get("fecha"):
            raise SystemExit("El lote.json necesita 'fecha' (YYYY-MM-DD) para instalar.")
        instalar(lote, marca, work)


if __name__ == "__main__":
    main()
