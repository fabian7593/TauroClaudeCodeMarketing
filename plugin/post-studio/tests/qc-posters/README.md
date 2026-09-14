# Fixture de QC de pósters

Mide si un modelo es apto para hacer el control de logos de plataformas en pósters,
en vez de suponerlo.

## Por qué existe

El QC de pósters es el único paso del pipeline donde un error **sale publicado con
la marca de un competidor adentro**, y es el más sensible al modelo que lo ejecute:
es una tarea de visión pura, ver un sello chico y de bajo contraste en una esquina.
Ya se colaron dos violaciones reales en este proyecto por mirar miniaturas.

Todo lo demás del pipeline (`producir_lote.py`) es determinista y da lo mismo con
cualquier modelo. Esto no. Por eso se mide.

## Los 6 casos

| | Título | Esperado | Qué prueba |
|---|---|---|---|
| p1 | El Juego del Calamar | OK | control limpio — que no invente sellos |
| p2 | Stranger Things | RECHAZO | sello de Netflix grande y visible — el caso fácil |
| p3 | Mulán | OK (DUDA aceptable) | **estudio vs plataforma**: dice "Disney" sin el "+" |
| p4 | The Boys | RECHAZO | **el caso difícil**: "prime video" chico y en bajo contraste abajo |
| p5 | Lost | RECHAZO | **España vs LATAM**: el póster dice "PERDIDOS" |
| p6 | The Mandalorian | RECHAZO | "Disney+" con el "+" = plataforma, opuesto de p3 |

p3 y p6 se controlan entre sí: un modelo que rechaza los dos no distingue estudio de
plataforma (y rechazaría una pieza ya publicada); uno que acepta los dos deja pasar
una plataforma.

Tres pósters son reales y limpios; tres tienen un sello **compuesto a propósito**
para tener positivos verdaderos. No son material de publicación.

## Cómo se corre

```bash
python evaluar.py --prompt          # imprime el prompt exacto para el modelo
# ...el modelo corre el subagente qc-posters y devuelve su texto...
python evaluar.py respuesta.txt     # puntúa
```

Sale con código 1 si hay algún **falso negativo** (dejó pasar un sello) o si faltan
veredictos. Un falso positivo (rechazar algo válido) solo cuesta una descarga más:
es tolerable, y de hecho es el sesgo que se prefiere.

## Cómo leer el resultado

- **Falso negativo → ese modelo no sirve para esto.** No hay matices: un sello que
  pasa sale publicado.
- **Falta un veredicto → repetir**, nunca dar por buenos los que faltan.
- **El veredicto es lo confiable, el detalle descriptivo no.** En la validación del
  2026-09-14 el agente reportó un sello "dos veces: arriba y abajo" cuando había uno
  solo abajo — verificado pixel a pixel. Acertó el veredicto y adornó la ubicación.
  Si necesitás saber dónde está exactamente un sello, verificalo a mano.

## Resultado de referencia

**2026-09-14, Opus 5: 6/6**, más una segunda tanda de 11 pósters reales, también
11/11. Cero falsos negativos, cero falsos positivos. Ese es el piso a igualar.
