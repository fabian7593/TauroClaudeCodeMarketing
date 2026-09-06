# -*- coding: utf-8 -*-
"""
Elige las próximas N piezas para programar en Zernio (camino API, ver SKILL.md
seccion 5C), sin repetir nada ya programado/publicado ni piezas reservadas
para una epoca que todavia no llega.

Reglas que aplica (mismas usadas a mano el 2026-09-03, ver
POST/calendario-publicacion.md):
  1. Salta cualquier pieza con publicado.hecho=true o publicado.programado ya
     seteado en su pieza.json -- eso es "ya usada", no se repite.
  2. Si una pieza tiene SOLO epocas distintas de "Cualquier Momento" (ej. una
     pieza atada solo a Navidad), se salta salvo que la fecha de referencia
     (--fecha, default hoy) caiga dentro de esa epoca -- ese cruce fino
     (que fecha del año corresponde a que epoca) hoy se decide a mano, este
     script solo filtra las que son evergreen ("Cualquier Momento") mas las
     que el usuario fuerce con --incluir-epoca.
  3. Orden de la seleccion: RANDOM por default (--orden random) -- el
     catalogo esta cargado con vtxId aproximadamente alfabetico por titulo
     dentro de cada categoria, asi que "vtxId mas bajo primero" terminaba
     publicando en tandas todas-la-A, todas-la-B..., que se ve mecanico en
     el feed. Pedido explicito del usuario el 2026-09-03: se puede publicar
     random, no tiene que ir en orden alfabetico. Usa --orden vtxid solo
     cuando el orden SI importa (ej. una saga que conviene ir soltando en
     secuencia, o se quiere agotar el catalogo de forma prolija a proposito).
  4. Avisa (no descarta) las piezas con mas de 10 imagenes en su carrusel --
     Instagram/Facebook no aceptan mas de 10 elementos por post (contando la
     ficha de sinopsis). Hay que recortar a mano cual publicar, ver SKILL.md
     5C punto 5.
  5. Epoca NO significa "solo el dia exacto". Pedido explicito del usuario
     el 2026-09-05: un feriado/epoca (Halloween, Navidad, Dia del Nino, etc.)
     se cubre con contenido tematico ubicado CERCA de la fecha real -- unos
     dias antes o despues sirve igual, no hace falta pegarle al dia exacto.
     Ademas, acercandose a una epoca marcada (ej. las ultimas 1-2 semanas de
     octubre para Halloween) hay que REVISAR ACTIVAMENTE el catalogo con
     --incluir-epoca "<nombre>" y no asumir que alcanza con lo que ya cayo
     "Cualquier Momento": si el volumen tematico ya producido es bajo (el
     2026-09-05 la meta que fijo el usuario fue "al menos 5 piezas" para
     Halloween y solo habia 1 ya producida -- Stranger Things -- mas 2
     piezas evergreen que igual encajan por genero -- American Horror Story,
     La Purga), hay que PRODUCIR piezas nuevas para esa epoca en vez de
     rellenar con lo primero que salga random (ver POST/calendario-publicacion.md,
     seccion "Ronda Halloween 2026-10"). Esto aplica a cualquier epoca
     marcada, no solo Halloween -- es la politica estandar de ahora en mas.

Uso:
  python siguiente_lote_zernio.py --limite 4
  python siguiente_lote_zernio.py --limite 10 --incluir-epoca "Navidad"
  python siguiente_lote_zernio.py --limite 6 --orden vtxid
  python siguiente_lote_zernio.py --limite 6 --semilla 42   # random reproducible (debug)
  python siguiente_lote_zernio.py --limite 10 --incluir-epoca "Halloween"  # acercandose a fin de octubre
"""
import argparse
import glob
import json
import os
import random

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))


def cargar_catalogo():
    path = os.path.join(ROOT, "POST", "catalogo.json")
    data = json.load(open(path, encoding="utf-8"))
    return {i["vtxId"]: i for i in data["titulos"]}


def cargar_piezas():
    piezas = []
    for pf in glob.glob(os.path.join(ROOT, "POST", "social", "*", "*", "pieza.json")):
        piezas.append(json.load(open(pf, encoding="utf-8")))
    return piezas


def min_vtx(pz):
    vids = pz.get("vtxIds") or []
    nums = [int(v.replace("VTX-", "")) for v in vids]
    return min(nums) if nums else 99999


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limite", type=int, default=10, help="cuantas piezas devolver (default 10)")
    ap.add_argument("--incluir-epoca", action="append", default=[],
                     help="nombre de epoca a incluir ademas de 'Cualquier Momento' (repetible)")
    ap.add_argument("--orden", choices=["random", "vtxid"], default="random",
                     help="random (default) mezcla el catalogo elegible; vtxid mantiene el orden secuencial del catalogo")
    ap.add_argument("--semilla", type=int, default=None,
                     help="semilla para --orden random (solo para debug/reproducir una corrida; en uso normal no se pasa)")
    args = ap.parse_args()

    epocas_ok = {"Cualquier Momento"} | set(args.incluir_epoca)

    items = cargar_catalogo()
    piezas = cargar_piezas()

    elegibles = []
    for pz in piezas:
        pub = pz.get("publicado", {})
        if pub.get("hecho") or pub.get("programado"):
            continue

        vids = pz.get("vtxIds", [])
        epocas = set()
        for v in vids:
            it = items.get(v)
            if it and it.get("epoca"):
                epocas.add(it["epoca"])

        # si TODAS las epocas de la pieza quedan fuera de las permitidas, se salta
        if epocas and not (epocas & epocas_ok):
            continue

        n_img = len(pz.get("imagenes", []))
        elegibles.append((min_vtx(pz), pz, n_img, epocas))

    if args.orden == "vtxid":
        elegibles.sort(key=lambda x: x[0])
    else:
        rng = random.Random(args.semilla)
        rng.shuffle(elegibles)

    seleccion = elegibles[: args.limite]

    print(f"Elegibles totales: {len(elegibles)} | devolviendo {len(seleccion)} | orden: {args.orden}\n")
    for vtx, pz, n_img, epocas in seleccion:
        aviso = f"  <-- {n_img} imagenes, SUPERA el limite de 10 del carrusel, recortar antes de publicar" if n_img > 10 else ""
        ep = f" [epoca: {', '.join(sorted(epocas))}]" if epocas and epocas != {"Cualquier Momento"} else ""
        print(f"VTX{vtx:04d}  {pz['slug']:45s} {pz['titulo']}{ep}{aviso}")

    if not seleccion:
        print("No hay piezas elegibles nuevas -- todo el catalogo producido ya esta usado o reservado por epoca.")


if __name__ == "__main__":
    main()
