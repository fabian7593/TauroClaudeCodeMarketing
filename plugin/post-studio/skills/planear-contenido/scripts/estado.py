# -*- coding: utf-8 -*-
"""
Estado de producción: qué títulos del catálogo ya tienen contenido hecho.

Modelo (a prueba de desincronización):
  - cada pieza guarda su propia ficha en  <contentRoot>/social/<categoria>/<slug>/pieza.json
    (categoria = "series" | "peliculas", ver planear-contenido/SKILL.md)
  - el índice global  <contentRoot>/estado-catalogo.json  NO se escribe a mano:
    se REGENERA leyendo esas fichas del disco y cruzándolas con el catálogo.
Si un pieza.json dice algo que no está en el disco, el regenerado lo marca como
faltante en vez de mentir.

Uso:
    python estado.py regenerar [--content-root POST] [--catalogo POST/catalogo.json]
    python estado.py estado <VTX-id | texto | slug>
    python estado.py resumen
"""
import argparse
import datetime
import glob
import io
import json
import os
import sys
import unicodedata


def normalizar(texto):
    if not texto:
        return ""
    texto = unicodedata.normalize("NFD", str(texto))
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return " ".join(texto.lower().split())


def cargar_json(ruta, default=None):
    if not os.path.isfile(ruta):
        return default
    with io.open(ruta, encoding="utf-8") as fh:
        return json.load(fh)


def guardar_json(ruta, datos):
    carpeta = os.path.dirname(os.path.abspath(ruta))
    if carpeta and not os.path.isdir(carpeta):
        os.makedirs(carpeta)
    with io.open(ruta, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(datos, ensure_ascii=False, indent=2) + "\n")


def leer_piezas(content_root):
    piezas = []
    patron = os.path.join(content_root, "social", "*", "*", "pieza.json")
    for ruta in sorted(glob.glob(patron)):
        ficha = cargar_json(ruta, {})
        carpeta = os.path.dirname(ruta)
        ficha["carpeta"] = carpeta.replace("\\", "/")
        ficha.setdefault("slug", os.path.basename(carpeta))
        ficha.setdefault("categoria", os.path.basename(os.path.dirname(carpeta)))

        # verificación contra el disco: los archivos declarados existen?
        faltantes = []
        for img in ficha.get("imagenes", []):
            archivo = img.get("archivo")
            if archivo and not os.path.isfile(archivo):
                faltantes.append(archivo)
        texto = (ficha.get("texto") or {}).get("archivo")
        if texto and not os.path.isfile(texto):
            faltantes.append(texto)

        # archivos en disco que la ficha no declara
        en_disco = sorted(
            p.replace("\\", "/")
            for p in glob.glob(os.path.join(carpeta, "images", "*.png"))
        )
        declarados = {img.get("archivo") for img in ficha.get("imagenes", [])}
        huerfanos = [p for p in en_disco if p not in declarados]

        ficha["imagenesEnDisco"] = len(en_disco)
        if faltantes:
            ficha["archivosFaltantes"] = faltantes
        if huerfanos:
            ficha["archivosNoDeclarados"] = huerfanos
        piezas.append(ficha)
    return piezas


def cmd_regenerar(args):
    piezas = leer_piezas(args.content_root)
    catalogo = cargar_json(args.catalogo, {}) or {}
    por_id = {t["vtxId"]: t for t in catalogo.get("titulos", [])}

    hechos = {}
    for p in piezas:
        for vtx in p.get("vtxIds", []):
            hechos.setdefault(vtx, []).append(p["slug"])

    titulos = []
    for vtx, slugs in sorted(hechos.items()):
        t = por_id.get(vtx, {})
        titulos.append({
            "vtxId": vtx,
            "titulo": t.get("tituloEs"),
            "coleccion": t.get("coleccion"),
            "piezas": slugs,
        })

    problemas = []
    for p in piezas:
        if p.get("archivosFaltantes"):
            problemas.append({"slug": p["slug"], "faltan": p["archivosFaltantes"]})
        if p.get("archivosNoDeclarados"):
            problemas.append({"slug": p["slug"], "noDeclarados": p["archivosNoDeclarados"]})
        if not p.get("sinopsis", {}).get("creada"):
            problemas.append({"slug": p["slug"], "sinSinopsis": True})

    datos = {
        "_comment": (
            "Índice de producción GENERADO — no editar a mano. Se regenera con "
            "`estado.py regenerar`, leyendo los pieza.json de cada carpeta de "
            "<contentRoot>/social/. La fuente de verdad de cada pieza es su pieza.json; "
            "la fuente de verdad del catálogo es catalogo.json."
        ),
        "generado": datetime.date.today().isoformat(),
        "totalPiezas": len(piezas),
        "titulosConContenido": len(hechos),
        "titulosEnCatalogo": catalogo.get("totalTitulos"),
        "problemas": problemas,
        "piezas": [{
            "slug": p.get("slug"),
            "categoria": p.get("categoria"),
            "tipo": p.get("tipo"),
            "titulo": p.get("titulo"),
            "grupo": p.get("grupo"),
            "vtxIds": p.get("vtxIds", []),
            "carpeta": p.get("carpeta"),
            "imagenes": p.get("imagenes", []),
            "sinopsis": p.get("sinopsis"),
            "texto": p.get("texto"),
            "publicado": p.get("publicado"),
            "creada": p.get("creada"),
            "nota": p.get("nota"),
        } for p in piezas],
        "titulos": titulos,
    }
    salida = args.salida or os.path.join(args.content_root, "estado-catalogo.json").replace("\\", "/")
    guardar_json(salida, datos)
    print("%s: %d piezas, %d titulos con contenido, %d problemas"
          % (salida, len(piezas), len(hechos), len(problemas)))
    for pr in problemas:
        print("  problema: %s" % json.dumps(pr, ensure_ascii=False))


def cmd_estado(args):
    piezas = leer_piezas(args.content_root)
    catalogo = cargar_json(args.catalogo, {}) or {}
    q = normalizar(args.texto)

    coincidencias = []
    for t in catalogo.get("titulos", []):
        if q in (normalizar(t.get("vtxId")), ) or q in normalizar(t.get("tituloEs")) \
           or q in normalizar(t.get("tituloEn")) or (t.get("coleccion") and q in normalizar(t.get("coleccion"))):
            coincidencias.append(t)

    ids = {t["vtxId"] for t in coincidencias}
    relacionadas = [p for p in piezas
                    if set(p.get("vtxIds", [])) & ids or q in normalizar(p.get("slug"))]

    salida = {
        "consulta": args.texto,
        "titulosEnCatalogo": [
            {"vtxId": t["vtxId"], "titulo": t.get("tituloEs"), "tipo": t.get("tipo"),
             "coleccion": t.get("coleccion"), "anio": t.get("anio")}
            for t in coincidencias[:20]
        ],
        "piezasExistentes": [
            {"slug": p.get("slug"), "categoria": p.get("categoria"), "tipo": p.get("tipo"), "vtxIds": p.get("vtxIds", []),
             "imagenes": len(p.get("imagenes", [])),
             "sinopsis": bool((p.get("sinopsis") or {}).get("creada")),
             "texto": bool((p.get("texto") or {}).get("creado")),
             "publicado": bool((p.get("publicado") or {}).get("hecho"))}
            for p in relacionadas
        ],
        "yaHecho": bool(relacionadas),
    }
    sys.stdout.write(json.dumps(salida, ensure_ascii=False, indent=1) + "\n")


def cmd_resumen(args):
    piezas = leer_piezas(args.content_root)
    catalogo = cargar_json(args.catalogo, {}) or {}
    hechos = {v for p in piezas for v in p.get("vtxIds", [])}
    total = catalogo.get("totalTitulos") or 0
    salida = {
        "piezas": len(piezas),
        "titulosConContenido": len(hechos),
        "titulosEnCatalogo": total,
        "porcentaje": round(len(hechos) * 100.0 / total, 1) if total else None,
        "publicadas": sum(1 for p in piezas if (p.get("publicado") or {}).get("hecho")),
        "sinTexto": [p["slug"] for p in piezas if not (p.get("texto") or {}).get("creado")],
        "sinSinopsis": [p["slug"] for p in piezas if not (p.get("sinopsis") or {}).get("creada")],
    }
    sys.stdout.write(json.dumps(salida, ensure_ascii=False, indent=1) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--content-root", default="POST")
    ap.add_argument("--catalogo", default="POST/catalogo.json")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("regenerar")
    p.add_argument("--salida")

    p = sub.add_parser("estado")
    p.add_argument("texto")

    sub.add_parser("resumen")

    args = ap.parse_args()
    {"regenerar": cmd_regenerar, "estado": cmd_estado, "resumen": cmd_resumen}[args.cmd](args)


if __name__ == "__main__":
    main()
