# -*- coding: utf-8 -*-
"""
Consultas puntuales al espejo local del catálogo (POST/catalogo.json).

Existe para NO cargar el catálogo entero en contexto: son 1.000+ títulos. Cada
comando devuelve JSON chico, listo para leer.

Uso:
    python consultar_catalogo.py ver <VTX-id | texto>
    python consultar_catalogo.py buscar <texto> [--limite N]
    python consultar_catalogo.py coleccion <nombre>
    python consultar_catalogo.py colecciones [--min N]
    python consultar_catalogo.py grupo <VTX-id | texto>
    python consultar_catalogo.py pendientes [--limite N] [--solo-en-app]

`grupo` es el comando que usa planear-contenido: devuelve el título pedido junto
con TODA su colección, ya separada en series y películas.
"""
import argparse
import io
import json
import os
import re
import sys
import unicodedata

CAMPOS_RESUMEN = [
    "vtxId", "categoria", "tipo", "tituloEs", "tituloEn", "anio", "temporadas",
    "episodios", "duracionMin", "generos", "calificacion", "clasificacion",
    "estado", "audioDual", "tercerAudio", "tmdbId", "tmdbUrl", "posterUrl",
    "notas", "agregadoAlaApp", "anadidoARedes", "coleccion", "esAnime",
]


def normalizar(texto):
    if not texto:
        return ""
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return texto.lower().strip()


def cargar(ruta):
    if not os.path.isfile(ruta):
        raise SystemExit(
            "No existe %s. Corré primero el skill sincronizar-catalogo." % ruta)
    with io.open(ruta, encoding="utf-8") as fh:
        return json.load(fh)


def resumir(t):
    return {k: t.get(k) for k in CAMPOS_RESUMEN if t.get(k) not in (None, [], "")}


def buscar(titulos, texto):
    q = normalizar(texto)
    exactos = [t for t in titulos if normalizar(t.get("vtxId")) == q]
    if exactos:
        return exactos
    campos = ("tituloEs", "tituloEn", "coleccion")
    return [t for t in titulos if any(q in normalizar(t.get(c)) for c in campos)]


def ordenar_grupo(items):
    return sorted(items, key=lambda t: (t.get("anio") or 9999, t.get("vtxId") or ""))


def cmd_ver(datos, args):
    res = buscar(datos["titulos"], args.texto)
    if not res:
        return {"encontrados": 0, "titulos": []}
    return {"encontrados": len(res), "titulos": [resumir(t) for t in res[:args.limite]]}


def cmd_buscar(datos, args):
    return cmd_ver(datos, args)


def cmd_coleccion(datos, args):
    q = normalizar(args.texto)
    items = [t for t in datos["titulos"] if normalizar(t.get("coleccion")) == q]
    if not items:
        items = [t for t in datos["titulos"] if q and q in normalizar(t.get("coleccion"))]
    items = ordenar_grupo(items)
    return {
        "coleccion": items[0]["coleccion"] if items else None,
        "cantidad": len(items),
        "titulos": [resumir(t) for t in items],
    }


def cmd_colecciones(datos, args):
    cols = datos.get("colecciones", {})
    filas = [{"coleccion": k, "cantidad": len(v)} for k, v in cols.items() if len(v) >= args.min]
    filas.sort(key=lambda f: (-f["cantidad"], f["coleccion"]))
    return {"total": len(filas), "colecciones": filas}


def cmd_grupo(datos, args):
    res = buscar(datos["titulos"], args.texto)
    if not res:
        return {"error": "sin coincidencias para %r" % args.texto}
    base = res[0]
    coleccion = base.get("coleccion")
    if coleccion:
        items = [t for t in datos["titulos"] if t.get("coleccion") == coleccion]
    else:
        items = [base]
    items = ordenar_grupo(items)
    series = [resumir(t) for t in items if (t.get("tipo") or "").lower().startswith("serie")]
    pelis = [resumir(t) for t in items if (t.get("tipo") or "").lower().startswith("pel")]
    return {
        "consulta": args.texto,
        "tituloBase": resumir(base),
        "coleccion": coleccion,
        "enColeccion": len(items),
        "otrasCoincidencias": [t["vtxId"] for t in res[1:6]],
        "series": series,
        "peliculas": pelis,
        "esAnime": any(t.get("esAnime") for t in items),
    }


def cmd_pendientes(datos, args):
    items = [t for t in datos["titulos"] if not t.get("anadidoARedes")]
    if args.solo_en_app:
        items = [t for t in items if t.get("agregadoAlaApp")]
    return {
        "pendientes": len(items),
        "titulos": [resumir(t) for t in items[:args.limite]],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalogo", default="POST/catalogo.json")
    sub = ap.add_subparsers(dest="cmd", required=True)

    for nombre in ("ver", "buscar"):
        p = sub.add_parser(nombre)
        p.add_argument("texto")
        p.add_argument("--limite", type=int, default=10)

    p = sub.add_parser("coleccion")
    p.add_argument("texto")

    p = sub.add_parser("colecciones")
    p.add_argument("--min", type=int, default=2)

    p = sub.add_parser("grupo")
    p.add_argument("texto")

    p = sub.add_parser("pendientes")
    p.add_argument("--limite", type=int, default=20)
    p.add_argument("--solo-en-app", action="store_true")

    args = ap.parse_args()
    datos = cargar(args.catalogo)
    salida = {
        "ver": cmd_ver, "buscar": cmd_buscar, "coleccion": cmd_coleccion,
        "colecciones": cmd_colecciones, "grupo": cmd_grupo, "pendientes": cmd_pendientes,
    }[args.cmd](datos, args)

    texto = json.dumps(salida, ensure_ascii=False, indent=1)
    sys.stdout.write(texto + "\n")


if __name__ == "__main__":
    main()
