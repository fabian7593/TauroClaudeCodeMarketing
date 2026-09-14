# -*- coding: utf-8 -*-
"""
ficha_tmdb.py — trae los datos duros de una ficha de TMDB por su id, sin API key.

Para qué: el incidente "Anna" (2026-09-12) fue escribir la sinopsis y el caption de
un show distinto que solo compartía el nombre — el `tmdbId` y el póster eran los
correctos, el texto no. Ninguna regla mecánica lo atrapaba porque nadie comparaba
lo que se estaba escribiendo contra lo que TMDB dice realmente de esa ficha.

Este script trae tres datos que sí se pueden comparar contra el texto:

  - **año**: si el lote describe un show de 2021 y la ficha dice 2022, están
    hablando de shows distintos. Es exactamente el caso Anna (coreana 2022 vs
    miniserie española 2021).
  - **idioma original**: determina qué filas de audio corresponden, sin depender
    de `audioDual` ni de adivinar por `categoria`. Es la regla que se violó en 17
    piezas ya publicadas.
  - **título original**: señal cruzada extra — si el título original está en
    hangul/kanji y el texto describe una producción europea, algo no cierra.

Uso:
    python ficha_tmdb.py --id 196268 --tipo tv
    python ficha_tmdb.py --id 158015 --tipo movie

Salida: JSON con {id, tipo, titulo, anio, idiomaOriginal, tituloOriginal, url}.
Sale con código 2 si la ficha no existe o no se pudo leer.
"""
import argparse
import json
import re
import sys
import urllib.error
import urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
BASE = "https://www.themoviedb.org"

# La página se pide en inglés a propósito: los nombres de idioma vienen en inglés
# ("Korean", "Japanese") y así el mapeo de abajo es estable. Pedirla en español
# los traduciría y habría que mantener dos tablas.
ACCEPT_LANG = "en-US,en;q=0.9"

# Idioma original de TMDB -> código de fila del template (FLAG_COLORS en
# post-template.html). Si aparece un idioma que no está acá, el validador avisa
# en vez de aproximar con la bandera de otro idioma.
IDIOMA_A_CODIGO = {
    "english": "US",
    "spanish": None,          # original en español: solo lleva Audio Esp. Latino
    "castilian": None,
    "korean": "KR",
    "japanese": "JP",
    "portuguese": "BR",
    "italian": "IT",
    "german": "DE",
    "hindi": "IN",
    "mandarin": "CN",
    "chinese": "CN",
    "cantonese": "CN",
}

RE_TITLE = re.compile(r"<title>\s*(.*?)\s*</title>", re.S)
RE_ANIO = re.compile(r"\((?:TV Series\s*)?(\d{4})")
RE_IDIOMA = re.compile(r"Original Language</bdi>\s*</strong>\s*([^<]+?)\s*</p>", re.S)
RE_ORIGINAL = re.compile(r"Original (?:Name|Title)</bdi>\s*</strong>\s*([^<]+?)\s*</p>", re.S)


def bajar(url):
    pedido = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": ACCEPT_LANG})
    with urllib.request.urlopen(pedido, timeout=30) as resp:
        return resp.read().decode("utf-8", "replace")


def limpiar(txt):
    if txt is None:
        return None
    txt = re.sub(r"&#(\d+);", lambda m: chr(int(m.group(1))), txt)
    txt = (txt.replace("&amp;", "&").replace("&quot;", '"')
              .replace("&lt;", "<").replace("&gt;", ">").replace("&#39;", "'"))
    return re.sub(r"\s+", " ", txt).strip()


def ficha(tmdb_id, tipo):
    url = "%s/%s/%s" % (BASE, tipo, tmdb_id)
    try:
        html = bajar(url)
    except urllib.error.HTTPError as e:
        return {"error": "HTTP %s al pedir %s" % (e.code, url), "url": url}
    except Exception as e:
        return {"error": "%s al pedir %s" % (e.__class__.__name__, url), "url": url}

    bruto = limpiar((RE_TITLE.search(html) or [None, None])[1] if RE_TITLE.search(html) else None)
    titulo = anio = None
    if bruto:
        # "Anna (TV Series 2022) — The Movie Database (TMDB)"
        bruto = bruto.split("—")[0].split(" - The Movie")[0].strip()
        m = RE_ANIO.search(bruto)
        if m:
            anio = int(m.group(1))
        titulo = re.sub(r"\s*\((?:TV Series\s*)?\d{4}.*?\)\s*$", "", bruto).strip()

    m = RE_IDIOMA.search(html)
    idioma = limpiar(m.group(1)) if m else None
    m = RE_ORIGINAL.search(html)
    original = limpiar(m.group(1)) if m else None

    return {"id": str(tmdb_id), "tipo": tipo, "titulo": titulo, "anio": anio,
            "idiomaOriginal": idioma, "tituloOriginal": original, "url": url}


def codigo_de_idioma(idioma):
    """Devuelve (codigo, conocido). codigo None + conocido True = original en español."""
    if not idioma:
        return None, False
    clave = idioma.strip().lower()
    if clave in IDIOMA_A_CODIGO:
        return IDIOMA_A_CODIGO[clave], True
    return None, False


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--id", required=True)
    ap.add_argument("--tipo", default="tv", choices=["tv", "movie"])
    args = ap.parse_args()
    d = ficha(args.id, args.tipo)
    print(json.dumps(d, ensure_ascii=False, indent=1))
    sys.exit(2 if d.get("error") or not d.get("anio") else 0)


if __name__ == "__main__":
    main()
