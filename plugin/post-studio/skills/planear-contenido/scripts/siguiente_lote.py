# -*- coding: utf-8 -*-
"""
Agrupa el catálogo entero en piezas (según las reglas de planear-contenido:
series nunca se agrupan entre sí, películas de una colección van juntas en un
carrusel, películas sueltas van solas) y devuelve las siguientes N piezas
pendientes, en orden de catálogo, con todos los datos ya resueltos.

Pensado para producir el catálogo completo en lotes sin tener que re-derivar
a mano, cada vez, qué agrupa con qué y qué ya está hecho.

Uso:
    python siguiente_lote.py --catalogo POST/catalogo.json --content-root POST --limite 12
    python siguiente_lote.py --catalogo POST/catalogo.json --content-root POST --resumen
"""
import argparse
import glob
import io
import json
import os
import re
import unicodedata


def normalizar_slug(texto):
    t = unicodedata.normalize("NFD", texto)
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    t = re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()
    return t or "sin-titulo"


def cargar(ruta):
    with io.open(ruta, encoding="utf-8") as fh:
        return json.load(fh)


def vtx_num(vtx):
    m = re.search(r"(\d+)", vtx or "")
    return int(m.group(1)) if m else 0


def item_resumen(t):
    return {
        "vtxId": t["vtxId"], "titulo": t.get("tituloEs"), "tituloEn": t.get("tituloEn"),
        "anio": t.get("anio"), "tmdbId": t.get("tmdbId"),
        "tmdbTipo": "tv" if (t.get("tipo") or "").lower().startswith("serie") else "movie",
        "audioDual": bool(t.get("audioDual")), "esAnime": bool(t.get("esAnime")),
        # catalogoCategoria (NO confundir con la "categoria" series/peliculas que arma este
        # mismo script mas abajo): seccion del catalogo (Doramas/Anime/Series/etc). Junto con
        # tercerAudio, es la senal para elegir la fila de audio-idioma-original -- ver
        # CLAUDE.md "Filas de audio/subtitulos", corregido 2026-09-05 porque audioDual solo
        # nunca alcanza para saber SI hay un idioma original no-ingles ni CUAL es.
        "catalogoCategoria": t.get("categoria"), "tercerAudio": t.get("tercerAudio"),
        "calificacion": t.get("calificacion"), "clasificacion": t.get("clasificacion"),
        "temporadas": t.get("temporadas"), "episodios": t.get("episodios"),
        "duracionMin": t.get("duracionMin"), "generos": t.get("generos") or [],
        "estado": t.get("estado"), "notas": t.get("notas"),
        "posterUrl": t.get("posterUrl"),
    }


def calcular_grupos(catalogo):
    titulos = catalogo["titulos"]
    series = [t for t in titulos if (t.get("tipo") or "").lower().startswith("serie")]
    pelis = [t for t in titulos if (t.get("tipo") or "").lower().startswith("pel")]

    grupos = []

    for t in series:
        grupos.append({
            "tipoPieza": "imagen", "claveGrupo": "serie:" + t["vtxId"],
            "tituloGrupo": t.get("tituloEs"), "items": [t], "categoria": "series",
        })

    colecciones = {}
    sueltas = []
    for t in pelis:
        col = t.get("coleccion")
        if col:
            colecciones.setdefault(col, []).append(t)
        else:
            sueltas.append(t)

    for nombre, items in colecciones.items():
        items = sorted(items, key=lambda t: (t.get("anio") or 9999, t["vtxId"]))
        grupos.append({
            "tipoPieza": "carrusel", "claveGrupo": "coleccion:" + nombre,
            "tituloGrupo": nombre, "items": items, "categoria": "peliculas",
        })

    for t in sueltas:
        grupos.append({
            "tipoPieza": "imagen", "claveGrupo": "pelicula:" + t["vtxId"],
            "tituloGrupo": t.get("tituloEs"), "items": [t], "categoria": "peliculas",
        })

    for g in grupos:
        g["ordenCatalogo"] = min(vtx_num(t["vtxId"]) for t in g["items"])
    grupos.sort(key=lambda g: g["ordenCatalogo"])
    return grupos


def vtxIds_hechos(content_root):
    hechos = set()
    for ruta in glob.glob(os.path.join(content_root, "social", "*", "*", "pieza.json")):
        d = cargar(ruta)
        hechos.update(d.get("vtxIds", []))
    return hechos


def slug_unico(base, usados):
    slug = normalizar_slug(base)
    if slug not in usados:
        usados.add(slug)
        return slug
    i = 2
    while ("%s-%d" % (slug, i)) in usados:
        i += 1
    slug = "%s-%d" % (slug, i)
    usados.add(slug)
    return slug


def elegir_sinopsis_vtxids(items, max_n=4, min_n=2):
    """Para un grupo con más items de los que entran en la tira, elige los
    mejor calificados (regla acordada) — siempre incluye al menos min_n."""
    if len(items) <= max_n:
        return [t["vtxId"] for t in items]
    orden = sorted(items, key=lambda t: (t.get("calificacion") or 0), reverse=True)
    elegidos = orden[:max_n]
    # mantiene el orden cronológico al mostrarlos, no el de calificación
    ids = {t["vtxId"] for t in elegidos}
    return [t["vtxId"] for t in items if t["vtxId"] in ids]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalogo", default="POST/catalogo.json")
    ap.add_argument("--content-root", default="POST")
    ap.add_argument("--limite", type=int, default=12)
    ap.add_argument("--offset", type=int, default=0, help="saltar las primeras N piezas pendientes (para paginar)")
    ap.add_argument("--resumen", action="store_true", help="solo contar, no listar detalle")
    ap.add_argument("--filtro-tipo", choices=["imagen", "carrusel"], help="listar solo piezas de este tipo")
    args = ap.parse_args()

    catalogo = cargar(args.catalogo)
    grupos = calcular_grupos(catalogo)
    hechos = vtxIds_hechos(args.content_root)

    # carpetas de piezas ya usadas, para no colisionar slugs nuevos con las existentes
    # (un slug es unico cruzando series/ y peliculas/, aunque vivan en categorias distintas)
    usados = set(
        os.path.basename(os.path.dirname(p))
        for p in glob.glob(os.path.join(args.content_root, "social", "*", "*", "pieza.json"))
    )

    pendientes = []
    parciales = []
    for g in grupos:
        ids = {t["vtxId"] for t in g["items"]}
        si_hechos = ids & hechos
        if not si_hechos:
            pendientes.append(g)
        elif si_hechos != ids:
            parciales.append(g)

    if args.resumen:
        print(json.dumps({
            "totalGrupos": len(grupos),
            "pendientes": len(pendientes),
            "parciales": len(parciales),
            "hechosCompletos": len(grupos) - len(pendientes) - len(parciales),
        }, ensure_ascii=False, indent=1))
        if parciales:
            print("\nGRUPOS PARCIALMENTE HECHOS (revisar a mano):")
            for g in parciales[:20]:
                print("  -", g["tituloGrupo"], "|", [t["vtxId"] for t in g["items"]])
        return

    if args.filtro_tipo:
        pendientes = [g for g in pendientes if g["tipoPieza"] == args.filtro_tipo]

    lote = pendientes[args.offset:args.offset + args.limite]
    salida = []
    for g in lote:
        slug = slug_unico(g["tituloGrupo"], usados)
        items = [item_resumen(t) for t in g["items"]]
        salida.append({
            "slug": slug,
            "categoria": g["categoria"],
            "tipoPieza": g["tipoPieza"],
            "tituloGrupo": g["tituloGrupo"],
            "claveGrupo": g["claveGrupo"],
            "items": items,
            "sinopsisVtxIds": elegir_sinopsis_vtxids(items),
        })

    print(json.dumps({
        "totalPendientes": len(pendientes),
        "totalParciales": len(parciales),
        "enEsteLote": len(salida),
        "restantesDespuesDeEsteLote": len(pendientes) - args.offset - len(salida),
        "piezas": salida,
    }, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
