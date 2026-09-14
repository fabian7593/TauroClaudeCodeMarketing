---
description: Producir un lote completo de piezas con el motor producir_lote.py (camino económico en tokens)
---

Producí el siguiente lote de piezas: $ARGUMENTS (si no digo cuántas, son 10).

Este es el comando de **producción en serie**. `/cmd-contenido` hace una pieza a fondo, conversando; este hace un lote entero con el motor y el mínimo de vueltas. Usá este siempre que sean varias piezas.

## Antes de empezar: sesión limpia

**Un lote = una sesión.** Si esta sesión ya produjo un lote antes, decímelo y frená: conviene arrancar una sesión nueva. Todo lo que se acumuló en la conversación anterior se vuelve a cobrar en cada mensaje de este lote, y ese arrastre fue históricamente el mayor gasto del proyecto. El estado no se pierde: vive en `pieza.json`, `estado-catalogo.json` y el catálogo.

## Orden de trabajo

1. **Elegir el lote**
   ```bash
   python "plugin/post-studio/skills/planear-contenido/scripts/siguiente_lote.py" --limite <N>
   ```
   Respeta el orden mezclado (alterna serie / película / anime / dorama, no agota una categoría).

2. **Traer los datos reales de cada título** con `consultar_catalogo.py`. El `tmdbId` sale del catálogo y **no se cambia nunca**. Antes de escribir un solo texto, confirmá que año, país/reparto y trama de esa ficha puntual de TMDB son los que vas a describir — hay títulos que comparten nombre entre países y versiones, y el nombre nunca alcanza.

3. **Planear las piezas** (`planear-contenido`): qué va como imagen individual, qué como carrusel de colección, qué se separa. Mostrame el plan **en una tabla corta** antes de seguir.

4. **Bajar los pósters, con candidatos de sobra desde el arranque.** Con `tmdb_posters.py`, siguiendo la regla de idioma (LATAM → inglés → textless → default). Bajá también la variante alternativa que va a la tira de la ficha: **la tira nunca baja de 2 cuadros**.

   **Bajá 2-3 candidatos por cada espacio a llenar, no uno solo** (`--indice 0`, `--indice 1`, `--indice 2`; y si el título es de una franquicia conocida, sumá el de `--idioma en` aunque el de `es` parezca bien). Descargar de más es barato — son segundos y no gastan contexto. Volver a pedirle al subagente que revise un reemplazo es caro: cada ronda extra es un arranque en frío completo.

5. **QC de pósters con el subagente `qc-posters`, en UNA sola ronda.** Pasale **todos** los candidatos juntos, agrupados por slot, con ruta + `tituloEs` + idioma de cada uno. Pedile que diga, por grupo, cuál es el primer candidato que sirve. **No abras los pósters vos.**

   - Si devuelve menos veredictos que pósters enviados, repetí solo los faltantes.
   - Una segunda ronda solo si un slot entero quedó sin candidato válido. **Tres rondas encadenadas es la señal de que bajaste pocos candidatos en el paso 4** — en la primera corrida real esto costó ~25 de los 40 minutos del lote.
   - `DUDA` nunca se trata como `OK`; ante `ALARMA`, parar y reverificar el `tmdbId`.

6. **Escribir el `lote.json`** — es lo único que escribís a mano. Formato completo y comentado en `plugin/post-studio/skills/crear-imagen/scripts/lote.ejemplo.json`. Los textos siguen `crear-texto` (caption, tono de marca) y `crear-sinopsis` (ficha, español latino neutro, más profunda que el caption).

7. **Correr el motor**
   ```bash
   python "plugin/post-studio/skills/crear-imagen/scripts/producir_lote.py" <scratch>/lote.json --todo
   ```
   Valida (incluyendo el cruce contra la ficha real de TMDB: año e idioma original), arma los HTML, renderiza a 1080x1350, genera el contact sheet y las copias de QC, e instala PNG + `post.txt` + `pieza.json`. Si la validación falla, corregí el `lote.json` y volvé a correr — no toques el template ni el motor para hacer pasar una pieza.

8. **Revisar el lote en una lectura**: el `contact_sheet.jpg` de `<work>/qc/`, más una muestra de ~1 de cada 3 copias de 600px. A resolución completa solo lo que se vea mal. Los captions (`post.txt`) los revisás como texto, todos juntos con un `cat`, que es prácticamente gratis.

9. **Registrar y entregar**: `estado.py regenerar`, la tabla de estadísticas por categoría (`siguiente_lote.py --resumen`: categoría | hechas | total | faltan), y el commit.

## Qué preguntarme
Solo lo que no se pueda deducir: si una serie es antológica o de historia continua cuando no está claro, y si una colección grande va entera o en tandas. Layout, formato, filas de audio y estructura del post salen de las reglas y del catálogo — no me los preguntes.

## Economía de tokens (el punto de este comando)
- No abras pósters en esta sesión: eso es del subagente.
- No abras los PNG de 1080 salvo que la copia de 600px muestre un problema.
- No reescribas el motor ni sus scripts: ya están en el repo y probados contra regresión.
- Agrupá las llamadas independientes en un mismo mensaje y evitá narrar cada paso: cada mensaje vuelve a pagar todo el contexto acumulado.
