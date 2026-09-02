# -*- coding: utf-8 -*-
"""
Busca pósters alternativos en TMDB por idioma, sin API key.

Para qué: la regla de marca pide que, si el póster tiene texto, ese texto esté en
español (LATAM). El póster que trae el catálogo suele ser el default de TMDB, casi
siempre en inglés. Este script lista los pósters que TMDB tiene en un idioma dado
y, si se le pide, baja el mejor (el primero de la grilla, que es el más votado).

Uso:
    python tmdb_posters.py --id 158015 --tipo movie
    python tmdb_posters.py --id 158015 --tipo movie --descargar POST/assets/posters/la-purga.jpg
    python tmdb_posters.py --id 1413 --tipo tv --temporada 2 --indice 1

Idioma: por default 'es' (español), que es lo que pide la regla de marca.

Si TMDB no tiene ningún póster en ese idioma, el script sale con **código 2** y no
baja nada. En ese caso se usa el **póster default del catálogo** (columna Póster,
casi siempre en inglés) y se le avisa al usuario. No se busca reemplazo en otro
idioma ni se inventa: mejor el default conocido que un póster raro.

Otros idiomas útiles si hiciera falta a mano: 'en' (inglés), 'xx' (sin texto).
"""
import argparse
import json
import os
import re
import sys
import urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
BASE = "https://www.themoviedb.org"
CDN = "https://image.tmdb.org/t/p/original"
# la grilla de pósters usa estos dos tamaños; el resto de la página usa otros,
# así que filtrar por acá evita traerse el póster default de la barra lateral.
PATRON_GRILLA = re.compile(r"/t/p/(?:w220_and_h330_face|w440_and_h660_face)/([A-Za-z0-9]{20,})\.jpg")


def bajar_html(url):
    pedido = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "es-419,es;q=0.9"})
    with urllib.request.urlopen(pedido, timeout=30) as resp:
        return resp.read().decode("utf-8", "replace")


def listar(tmdb_id, tipo, idioma, temporada=None):
    ruta = "%s/%s/%s" % (BASE, tipo, tmdb_id)
    if temporada is not None:
        ruta += "/season/%d" % temporada
    url = "%s/images/posters?image_language=%s" % (ruta, idioma)
    html = bajar_html(url)
    vistos, hashes = set(), []
    for h in PATRON_GRILLA.findall(html):
        if h not in vistos:
            vistos.add(h)
            hashes.append(h)
    return url, hashes


def descargar(url_img, destino):
    carpeta = os.path.dirname(os.path.abspath(destino))
    if carpeta and not os.path.isdir(carpeta):
        os.makedirs(carpeta)
    pedido = urllib.request.Request(url_img, headers={"User-Agent": UA})
    with urllib.request.urlopen(pedido, timeout=60) as resp, open(destino, "wb") as fh:
        fh.write(resp.read())
    return os.path.getsize(destino)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", required=True)
    ap.add_argument("--tipo", default="movie", choices=["movie", "tv"])
    ap.add_argument("--idioma", default="es")
    ap.add_argument("--temporada", type=int, help="solo para tipo=tv: pósters de esa temporada")
    ap.add_argument("--descargar", help="ruta destino; baja el primer póster de la lista")
    ap.add_argument("--indice", type=int, default=0, help="cuál de los candidatos bajar (0 = el primero)")
    args = ap.parse_args()

    url, hashes = listar(args.id, args.tipo, args.idioma, args.temporada)
    salida = {
        "consulta": url,
        "idioma": args.idioma,
        "encontrados": len(hashes),
        "candidatos": ["%s/%s.jpg" % (CDN, h) for h in hashes],
    }

    if not hashes:
        print(json.dumps(salida, ensure_ascii=False, indent=1))
        sys.exit(2)

    if args.descargar:
        elegido = salida["candidatos"][min(args.indice, len(hashes) - 1)]
        salida["descargado"] = {"url": elegido, "archivo": args.descargar,
                                "bytes": descargar(elegido, args.descargar)}
    print(json.dumps(salida, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
