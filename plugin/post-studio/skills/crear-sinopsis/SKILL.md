---
name: crear-sinopsis
description: Genera la imagen de ficha/sinopsis de una pieza (columna de texto explicativo + tira de película con varios pósters + % de aprobación). Es la imagen que acompaña SIEMPRE a un post, sea imagen individual o carrusel. Úsalo después de planear-contenido y junto con crear-imagen/crear-carrusel, nunca solo.
---

# crear-sinopsis — imagen de ficha explicativa

Esta pieza es **obligatoria en todo post**, sea imagen individual o carrusel. Es la que engancha al que hace scroll: cuenta de qué va la serie/película/colección con más profundidad que el caption, y muestra varios pósters en una tira de película.

No confundir con `crear-imagen`: esa hace el arte de cada título (póster + título + audios). Esta hace **la ficha con el texto largo**.

## 0. Ubicaciones
- **Template canónico**: `${CLAUDE_PLUGIN_ROOT}/templates/sinopsis-template.html`
- **Copia editable del proyecto**: `<contentRoot>/_template/sinopsis-template.html` — si no existe, copiala del canónico. Una vez que existe, esa es la que se usa y se personaliza; no la pises automáticamente.
- **Salida**: `<contentRoot>/social/<categoria>/<slug>/images/<NN>-sinopsis-<slug>.png`, donde `<NN>` es **el número siguiente al último arte** y `categoria` es `series` o `peliculas` (la que ya tenga la pieza — esta imagen se genera siempre después del arte, así que la carpeta ya existe).

La ficha va **última**: primero se ve el arte (que es lo que frena el scroll) y al final el texto que explica. Un carrusel de 5 películas queda `01..05` de arte y `06-sinopsis`; un post de una sola imagen queda `01-arte` + `02-sinopsis` (o sea, dos slides).

## 1. Las imágenes de la tira — una distinta por cuadro
La tira lleva **2 a 4 cuadros, y cada cuadro un póster distinto**. Nunca repitas la misma imagen en dos cuadros.

De dónde salen, en este orden:
1. **Si la pieza cubre varios títulos** (carrusel de películas/series/temporadas): un póster de cada título, en orden cronológico. Con más títulos que cuadros, elegí los 3 más representativos (el primero de la saga, uno del medio, el último).
2. **Si la pieza cubre un solo título**: **variantes distintas del mismo título** en TMDB — el mismo script devuelve varios candidatos:
   ```bash
   python "${CLAUDE_PLUGIN_ROOT}/skills/crear-imagen/scripts/tmdb_posters.py" --id <tmdbId> --tipo movie|tv --indice 0
   python "${CLAUDE_PLUGIN_ROOT}/skills/crear-imagen/scripts/tmdb_posters.py" --id <tmdbId> --tipo movie|tv --indice 1
   ```
   Si el título es una serie con temporadas, también sirven los pósters de temporada (`--temporada N`).
3. **Si aun así no hay 2 imágenes distintas**: usá 2 cuadros en vez de 3. Mejor dos pósters reales que el mismo repetido.

Todos los pósters siguen la **regla de idioma** de `crear-imagen` (sección 0.1) — español LATAM/MX verificado contra `tituloEs` → inglés → textless → default del catálogo, **nunca español de España**, ni siquiera como último recurso. No la rederives acá, seguí esa.

Guardalos en `<contentRoot>/assets/posters/<slug>/` como el resto de los pósters de la pieza — no los dupliques en otra carpeta.

## 2. Escribir el texto de la ficha
Es **el texto más largo de toda la pieza** (≈450-750 caracteres) y tiene que ser **más profundo que el caption del post**, no un resumen del mismo. Basate en la sinopsis real (TMDB) y en los datos del catálogo — nunca inventes trama.

| Campo | Qué va |
|---|---|
| `title` | Nombre de la colección o del título, en español LATAM (el del catálogo) |
| `tagline` | Una línea corta que fije el tono. Puede ser el lema real de la saga o una frase propia — nunca spoiler |
| `body` | El texto largo (ver abajo) |
| `meta` | 2-3 chips de contexto: rango de años, cantidad de títulos/temporadas, clasificación por edad — el chip de edad va como badge corto (`+7`, `+13`, `+18`), **nunca el código crudo del catálogo** (`TV-Y7`, `TV-PG`, `TV-14`, `TV-MA` no son para mostrar, son solo la clave para mapear a la línea "Apta para..." del caption) |
| `score` | Calificación del catálogo pasada a porcentaje (7.8 → 78). Si la pieza cubre varios títulos, el promedio. `null` si no hay dato |

**Cómo escribir el `body`:**

- Si la pieza cubre **una colección o varias temporadas**: **no las describas una por una.** Contar "la primera va de esto, la segunda de aquello, la tercera..." se lee como una lista, aburre, y con 9 películas (Rápidos y Furiosos, El Juego del Miedo) directamente no entra.
  La forma que sí funciona:
  1. **La premisa que comparten todas** — la regla del universo, explicada bien. Ej. en La Purga: doce horas al año en las que cualquier delito es legal. Eso es lo que engancha y lo que la gente quiere entender.
  2. **Una línea que abra el abanico** — que cada entrega lleva a un escenario distinto, nombrando dos o tres ángulos en conjunto ("una casa sitiada, la calle, el origen de todo"), sin repartir una frase por título.
  3. **Por qué vale la pena verlas** — qué se siente, o qué gana el que las ve seguidas.
  Regla práctica: si sacás o agregás una película de la colección, el texto **debería seguir siendo válido sin reescribirlo**. Si no lo es, estás describiendo título por título.
- Si cubre **un solo título**: es un **resumen que da ganas de verlo**. Contá de qué va (planteo, quién es quién, qué se pone en juego) sin spoilers, y dejá claro por qué vale la pena sentarse a verlo. Si el puntaje o el reconocimiento del título suman de verdad al argumento, mencionalos en una frase; si no aportan, no los metas de relleno.
- **Vendé, no describas el envase.** Las virtudes técnicas (un plano secuencia, una fotografía, un formato raro) se cuentan como lo que le hacen sentir al que mira, no como ficha técnica. Y nunca en negativo: escribir "no hay giro sorpresa", "no pasa gran cosa" o "la serie no se mueve de ahí" le saca las ganas al lector aunque sea cierto. Si algo es una virtud, se dice como virtud.
- **Idioma: español latino neutro.** Se entiende igual en Costa Rica, México o Argentina: sin voseo, sin jerga de un solo país y sin palabras rebuscadas. Nada de "de un tirón", "flipante", "chévere", "guay", "padrísimo". Frases cortas y claras antes que adornadas.
- Tono: humano y directo, sin sonar a IA ni a contratapa de DVD. (El caption sí usa el tono de marca de `CLAUDE.md` — la ficha es más neutra porque la lee toda LATAM.)
- Sin emojis, sin hashtags, sin CTA: eso es del caption, no de la ficha.
- Si el título es `Incompleto` en el catálogo, no digas "completa" ni "todas las temporadas".

## 3. Render
Igual que `crear-imagen` (misma mecánica, mismo Chrome headless):
1. Copiá al directorio scratch de la sesión, como archivos hermanos: la copia editable del template (`work.html`), el logo (`logo.png`) y las imágenes de la tira (`img1.jpg`, `img2.jpg`, ...).
2. Editá el bloque `CONFIG` con los campos de arriba, más `logo: './logo.png'`, `site: brand.config.json.website`, `images: ['./img1.jpg', ...]`.
3. Serví el scratch con `python -m http.server <puerto> --directory <scratch>` y renderizá:
   ```bash
   chrome.exe --headless=new --disable-gpu --no-sandbox --hide-scrollbars \
     --user-data-dir="C:\ct2\profile" --screenshot="C:\ct2\salida.png" \
     --window-size=1080,1350 --force-device-scale-factor=1 --virtual-time-budget=4000 \
     "http://localhost:<puerto>/work.html"
   ```
   Notas ya resueltas (no las reinvestigues): la ruta de `--screenshot` tiene que ser **absoluta de Windows** (con ruta relativa Chrome no escribe el archivo y no avisa); `--user-data-dir` en ruta corta; `--virtual-time-budget=4000` porque el color de acento y el ajuste del texto se calculan de forma asíncrona.
4. Matá el `http.server` por PID antes de borrar el scratch (queda vivo aunque termine el comando y bloquea la carpeta en Windows).

## 4. Verificar antes de darla por buena
**Abrí el PNG con `Read` y leé el texto renderizado, no el que escribiste.** Es el paso que atrapa lo que se rompe entre el borrador y la imagen final. Recién después de esto se puede dar un veredicto sobre la pieza.

**En un lote de varias piezas, seguí la misma economía de tokens que `crear-imagen` sección 2 (verificación en lote)**: un contact sheet con todas las fichas del lote en vez de leer cada una suelta, y muestreo (~1 de cada 2-3) una vez que el diseño ya está probado — no la rederives acá.

Revisión visual:
- [ ] El texto entra completo y no quedó cortado abajo (el template baja el tamaño solo; si igual no entra, **acortá el texto**, no toques el layout)
- [ ] Cada cuadro de la tira tiene un póster **distinto**
- [ ] El logo y el sitio se leen sobre la placa oscura
- [ ] El color de acento del título no pelea con la imagen
- [ ] El % del anillo coincide con la calificación del catálogo

Revisión del contenido (releé el texto de la ficha **y** el `post.txt` de la pieza, uno al lado del otro):
- [ ] La ficha **da ganas de ver** el título — no lo describe en negativo ni suena a resumen de Wikipedia
- [ ] Está en español latino neutro: sin voseo, sin jerga de un país, sin palabras rebuscadas
- [ ] No hay spoilers
- [ ] Si la pieza cubre varios títulos, el texto habla del conjunto — no es una lista de "la primera..., la segunda..."
- [ ] La ficha y el caption **no dicen lo mismo**: el que lee los dos encuentra información nueva en cada uno
- [ ] Los datos duros (año, temporadas, edad, puntaje) coinciden entre ficha, caption y catálogo

## 5. Entrega
Copiá solo el PNG final a `<contentRoot>/social/<categoria>/<slug>/images/<NN>-sinopsis-<slug>.png` (numerado después del último arte), limpiá el scratch, y registrá la pieza (`sinopsis.creada: true` en `pieza.json`, ver `planear-contenido`).
