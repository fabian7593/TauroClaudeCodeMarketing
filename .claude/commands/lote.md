---
description: Producir el próximo lote de piezas del catálogo (ej. /lote 10, /lote 10 anime, /lote 5 doramas)
---

Producí el próximo lote de piezas de contenido para Bankai+: $ARGUMENTS

## Cómo interpretar lo que te pedí

**Cantidad**: el número que aparezca en `$ARGUMENTS`. Si no hay ninguno, son **10**.

**Filtro**: si nombré una categoría, pasásela a `siguiente_lote.py --solo-categoria <Categoría>`. Si no nombré ninguna, **no filtres** — el orden mezclado por default ya alterna serie / película / anime / dorama, que es lo que manda `CLAUDE.md`.

| Si digo… | Categoría del catálogo |
|---|---|
| anime, animes | `Anime` |
| pelis de anime, películas de anime | `Anime Peliculas` |
| dorama, doramas, coreanas, k-drama | `Doramas` |
| serie, series | `Series` |
| peli, pelis, películas | `Peliculas` |
| colecciones, sagas | `Peliculas Colecciones` |
| infantiles, niños | `Infantiles Series` + `Infantiles Peliculas` (preguntame cuál si no está claro) |
| documental, documentales | `Documentales` |
| animados, caricaturas | `Animados` |

**"random", "mezclado", "variado" o nada** → el default (`--orden mezclado`), que ya intercala categorías. No inventes un modo aleatorio nuevo: el orden mezclado existe justamente para eso.

Si pido una categoría que ya está al 100% (ej. `Series`), decímelo y ofrecé la más cercana en vez de producir un lote vacío.

## Qué hacer

Seguí **paso por paso** el flujo de `plugin/post-studio/commands/cmd-lote.md`. Está todo ahí: elegir el lote, traer los datos del catálogo, planear las piezas, bajar los pósters con candidatos de sobra, el QC en una sola ronda con el subagente `qc-posters`, escribir el `lote.json`, correr el motor y registrar.

No lo reinterpretes ni armes un flujo propio, y **no reescribas el motor**: `producir_lote.py` ya está probado contra regresión.

## Qué mostrarme al terminar, sin resumir

1. **La salida completa del motor** — las seis líneas (`validación`, `verificación TMDB`, `build`, `render`, `qc`, `instalar`), tal cual salieron.
2. **La tabla de estadísticas por categoría** (`siguiente_lote.py --resumen`): categoría | hechas | total | faltan.
3. **El QC de pósters**: cuántos revisó el subagente, en cuántas rondas, y el veredicto de los que no salieron `OK`. Si hicieron falta más de **una** ronda, decime por qué — es la señal de que se bajaron pocos candidatos por slot.

No commitees nada salvo que te lo pida explícitamente.
