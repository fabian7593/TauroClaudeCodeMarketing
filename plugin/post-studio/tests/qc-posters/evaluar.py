# -*- coding: utf-8 -*-
"""
evaluar.py — puntúa una corrida del subagente `qc-posters` contra la verdad conocida.

Para qué: el QC de pósters es el único paso del pipeline donde un error sale
publicado con la marca de un competidor adentro, y es también el más sensible al
modelo que lo ejecute (es una tarea de visión: ver un sello chico y de bajo
contraste). Antes de confiarle un lote a un modelo nuevo — Sonnet, Haiku, otra
versión de Opus — conviene medirlo en vez de suponerlo.

Flujo:

  1) Pedile al modelo que corra el subagente `qc-posters` sobre los 6 pósters de
     `posters/` (el prompt exacto lo imprime `--prompt`).
  2) Guardá su respuesta tal cual en un archivo de texto.
  3) python evaluar.py respuesta.txt

Imprime aciertos, fallos y — lo que más importa — si hubo algún **falso negativo**
(dejó pasar un póster con sello de plataforma), que es el único error que no se
puede tolerar.

Los pósters de `posters/` son fixtures: tres son pósters reales limpios y tres
tienen un sello compuesto a propósito. No son material de publicación.
"""
import argparse
import json
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
VEREDICTOS = ("RECHAZO", "ALARMA", "DUDA", "OK")

PROMPT = """Tu rol y tus reglas están definidos en este archivo:
{agente}

Leelo completo primero y seguilo al pie de la letra: es tu instrucción operativa.
No hagas nada más que lo que ese archivo dice.

Tu tarea: revisá estos 6 pósters para un lote de Bankai+.

Carpeta base: {carpeta}

{lista}
Devolvé un veredicto por póster, en orden, con el formato exacto que indica tu
archivo de instrucción, y el resumen de una línea al final."""


def cargar():
    with open(os.path.join(AQUI, "esperado.json"), encoding="utf-8") as fh:
        return json.load(fh)["casos"]


def parsear(texto):
    """Saca {id: veredicto} del texto libre del agente. Tolerante al formato:
    busca el primer veredicto de la línea y el pN que aparezca en ella."""
    hallados = {}
    for linea in texto.splitlines():
        m_id = re.search(r"\b(p[1-6])\b", linea, re.I)
        if not m_id:
            continue
        for v in VEREDICTOS:
            if re.search(r"\b%s\b" % v, linea, re.I):
                hallados.setdefault(m_id.group(1).lower(), v)
                break
    return hallados


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("respuesta", nargs="?", help="archivo con la respuesta del agente")
    ap.add_argument("--prompt", action="store_true", help="imprime el prompt a darle al modelo")
    args = ap.parse_args()

    casos = cargar()
    carpeta = os.path.join(AQUI, "posters")

    if args.prompt or not args.respuesta:
        agente = os.path.abspath(os.path.join(AQUI, "..", "..", "..", "..",
                                              ".claude", "agents", "qc-posters.md"))
        lista = "".join(
            '%d. %s.jpg | tituloEs: "%s" | idioma: %s\n' % (i, c["id"], c["tituloEs"], c["idioma"])
            for i, c in enumerate(casos, 1))
        print(PROMPT.format(agente=agente, carpeta=carpeta, lista=lista))
        if not args.respuesta:
            print("\n---\nGuardá la respuesta del agente en un archivo y corré:")
            print("  python evaluar.py respuesta.txt")
        return

    with open(args.respuesta, encoding="utf-8", errors="replace") as fh:
        hallados = parsear(fh.read())

    ok = 0
    falsos_negativos = []
    falsos_positivos = []
    faltantes = []
    print("%-4s %-26s %-9s %-9s %s" % ("id", "título", "esperado", "obtuvo", ""))
    print("-" * 78)
    for c in casos:
        esp = c["esperado"]
        aceptables = [esp] + c.get("aceptable", [])
        got = hallados.get(c["id"])
        if got is None:
            faltantes.append(c["id"])
            marca = "SIN VEREDICTO"
        elif got in aceptables:
            ok += 1
            marca = "ok" + (" (aceptable)" if got != esp else "")
        elif esp == "RECHAZO":
            falsos_negativos.append(c["id"])
            marca = "FALSO NEGATIVO  <-- dejó pasar algo que debía rechazar"
        else:
            falsos_positivos.append(c["id"])
            marca = "falso positivo"
        print("%-4s %-26s %-9s %-9s %s" % (c["id"], c["tituloEs"][:26], esp, got or "-", marca))

    print("-" * 78)
    print("aciertos: %d/%d" % (ok, len(casos)))
    if faltantes:
        print("SIN VEREDICTO: %s  -- el agente no revisó todo, repetir" % ", ".join(faltantes))
    if falsos_positivos:
        print("falsos positivos: %s  (rechazó algo válido: cuesta una descarga más, tolerable)"
              % ", ".join(falsos_positivos))
    if falsos_negativos:
        print("FALSOS NEGATIVOS: %s" % ", ".join(falsos_negativos))
        print("  Este modelo NO es apto para el QC de pósters: dejó pasar un sello de")
        print("  plataforma. Un falso negativo sale publicado con la marca de un competidor.")
        sys.exit(1)
    if faltantes:
        sys.exit(1)
    print("\nAPTO: ningún falso negativo. Detalle descriptivo: recordá que el veredicto")
    print("es lo confiable — la ubicación exacta del sello puede venir adornada.")


if __name__ == "__main__":
    main()
