# Incidentes de producción — historia completa

Este archivo guarda la **narración completa** de los incidentes que originaron las reglas
de `CLAUDE.md`. Las reglas en sí viven en `CLAUDE.md` y son las que mandan; acá está el
"qué pasó exactamente", que es largo y no hace falta tener cargado en cada sesión.

Se consulta cuando hace falta entender el porqué de una regla, o cuando algo parecido
vuelve a pasar y conviene ver cómo se resolvió la vez anterior.

---

## 2026-09-05 — Filas de audio: el idioma original, no `audioDual`

Se mostraba "Audio Inglés" en series coreanas/alemanas, o directamente se omitía la fila
del idioma original en doramas, porque el sistema decidía solo con el booleano `audioDual`
y el flag `esAnime`. `audioDual` dice si hay doblaje extra, pero no dice a qué idioma está
doblado ni cuál es el original.

Corregido a pedido explícito del usuario el 2026-09-05. Afectó a 17 piezas ya publicadas: Black Knight, El Asesino Mediático, El Juego del Calamar, Estamos Muertos, La Casa de Papel: Corea, La Chica Enmascarada, Alice, Aterrizaje de Emergencia en tu Corazón, Bad Guys, Besos Kitty, Como Peces Dorados, Ju-On: Orígenes, Este Mundo No Me Hará Mala Persona, Gul, Dark, Bandidos de Hoy, Evangelion: las películas)

Regla resultante: ver "Filas de audio/subtítulos en las imágenes" en `CLAUDE.md`.

---

## 2026-09-12 — "Anna": se describió el show equivocado

**Incidente 2026-09-12**: la pieza "Anna" (VTX-0155, tmdbId real `196268`, dorama coreano con Bae Suzy) tenía escritos la sinopsis y el caption de la MINISERIE ESPAÑOLA "Anna" (2021, sobre acoso digital/foto manipulada) — un show completamente distinto que solo comparte nombre. El póster sí era el correcto (bajado con el tmdbId correcto), pero al redactar el texto se tiró de memoria general por el nombre en vez de verificar los datos reales de esa ficha puntual de TMDB. Hay bastantes títulos que comparten nombre entre países/versiones (Anna, Lost — hay más de uno —, remakes, etc.) — el nombre del título NUNCA alcanza para saber de qué show se trata.

Regla resultante: ver "Todo dato de la pieza sale del `tmdbId` exacto del catálogo" en `CLAUDE.md`.

---

## 2026-09-12/13 — Ficha de sinopsis con un solo cuadro en la tira

**Incidente 2026-09-12/13**: al no encontrar una segunda imagen "distinta" en TMDB para Anna y Franco Escamilla (todos los candidatos alternativos traían logo de Netflix o eran pixel-idénticos al principal), se armó la ficha con un solo cuadro en la tira — el template (`sinopsis-template.html`) calcula el alto de la tira en base a la cantidad de imágenes, así que con 1 sola imagen la tira queda corta y descentrada, rompiendo el diseño (se nota comparado con cualquier otra ficha ya publicada). **La tira nunca baja de 2 cuadros.** Si TMDB no tiene una segunda imagen realmente distinta y sin logos, usar la mejor alternativa disponible aunque sea muy parecida a la principal (otra resolución/recorte del mismo material) — preferible a romper el diseño con 1 solo cuadro. Corregido en `POST/social/series/anna/` y `POST/social/peliculas/franco-escamilla-voyerista-auditivo/`.

Regla resultante: ver "La tira de la ficha de sinopsis SIEMPRE lleva mínimo 2 cuadros" en `CLAUDE.md`.
Desde 2026-09-14 esto además lo valida `producir_lote.py --validar` antes de renderizar.

---

## 2026-09-12 — 10 piezas de anime generadas con `panel_lateral`

**Incidente 2026-09-12**: se generaron 10 piezas de anime usando `layout: 'panel_lateral'` (panel de color sólido a la izquierda, con el color dominante del póster extraído y un patrón de puntos decorativo) — el usuario las rechazó de inmediato ("todas están malas... no sé por qué usaste ese color a la izquierda"). El template (`post-template.html`) soporta los dos layouts y trae `panel_lateral` como ejemplo por default en su CONFIG de demostración, pero **la casa SIEMPRE usa `full_bleed`** para el arte principal — nunca se usó `panel_lateral` en ninguna pieza real publicada. Antes de armar el `CONFIG` de un lote nuevo, especialmente si hay que reconstruir el pipeline de cero (ej. tras perderse los scripts de un directorio temporal), **abrí con `Read` el PNG de una pieza ya instalada** (ej. `POST/social/series/alice/images/01-alice.png` o `.../yu-gi-oh-duelo-de-monstruos/images/01-yu-gi-oh-duelo-de-monstruos.png`) y compará contra lo que se está por generar — nunca asumas la config de ejemplo del template.

Regla resultante: ver "Cómo debe verse la imagen de arte" en `CLAUDE.md`. Desde 2026-09-14
el motor `producir_lote.py` fija `full_bleed` y `badges: ['1080p']` por código, así que el
layout ya no es una decisión que se pueda equivocar en un lote.

---

## 2026-09-14 — El pipeline se rearmaba a mano en cada lote

Hasta el lote 21, el pipeline de producción (armar los CONFIG, renderizar con Chrome
headless, instalar las piezas) se reescribía de cero en una carpeta temporal en cada lote,
con los datos del lote incrustados dentro del propio `.py`. Los scripts se perdían al
limpiarse Temp, y cada lote volvía a emitir ~250 líneas de lógica ya conocida.

Medición sobre los transcripts reales del proyecto (8 sesiones):

- **2.810 millones de tokens** acumulados en total.
- La sesión más larga (3 al 13 de septiembre, ~98 piezas): 3.344 requests con un contexto
  promedio de **465.000 tokens** y picos de 862.000, para un total de 1.556 millones.
- Un solo turno de "producí el siguiente lote" llegó a **127 millones de tokens**
  (204 requests × ~623.000 de contexto).
- 425 lecturas de imagen = 180 MB de base64 arrastrados en el contexto: entre el 9% y el
  37% del total facturado, según cuánto compactara la sesión.
- El resto del gasto no era trabajo nuevo: era volver a pagar contexto ya acumulado, en una
  sesión que vivió 10 días con solo 10 compactaciones.

Reglas resultantes: ver "Producción en lote" en `CLAUDE.md` y el comando `/cmd-lote`.
El motor quedó verificado contra regresión: reproduce los 24 PNG del lote 21 byte a byte
idénticos, y los mismos `post.txt` y `pieza.json`.
