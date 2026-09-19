# Bankai+ — Contexto de Marca para Generación de Contenido

## Qué es Bankai+
Bankai+ es el servicio B2C de streaming de VORTEX TV, dirigido a Costa Rica y el mercado LATAM de habla hispana. Servicio de streaming legal, tecnología neutral, catálogo de 1,000+ títulos (series, películas, anime, infantil).

## Planes
- Basic: $6/mes (USD)
- Standard: ₡4,500/mes
- Family: ₡6,000/mes
- El precio "desde" que se usa en los posts (el más barato, Basic) va en USD con signo $. Standard y Family quedan en colones hasta que se confirme su conversión — no inventar ese tipo de cambio.
- **La línea de invitación del post (punto 7 de la estructura, abajo) ya NO menciona precio.** Desde 2026-09-16, en vez de "Planes desde $6 al mes" (o cualquier variante de precio) cierra siempre con: "Registrate en nuestra plataforma bankaiplus.com y obten un mes gratis 🤩" — pedido explícito del usuario. Aplica a piezas nuevas de acá en adelante; no se edita retroactivamente lo ya publicado.

## Tono de comunicación
- Español costarricense casual, conjugación "vos"
- Cercano, humano, "peer-like" — nunca suena a IA ni a corporativo
- Hooks emocionales únicos por serie/película — NUNCA reciclados entre posts

## Reglas estrictas (NO NEGOCIABLES)
1. NUNCA mencionar Netflix, HBO Max, Disney+, Prime Video u otras plataformas de streaming en posts orgánicos de Instagram/Facebook/TikTok/YouTube. (Comparación directa SÍ permitida en flyers, FAQs y WhatsApp — pero no en estos posts).
2. CTA fijo en todo post: "👉 ¿Querés verla hoy mismo? Escribinos al DM o entrá a bankaiplus.com" (va cerca del principio del post, no al final — ver estructura abajo). No se agrega ningún otro CTA además de este.
3. Nunca prometer dispositivos no soportados. No existe función de "cast"/mirroring desde el celular — la app se instala directo (por APK o Play Store) en cada dispositivo. Dispositivos compatibles hoy: Smart TV/Box con Android TV, Chromecast con Google TV (instalando la app directo en el dispositivo), Amazon Fire TV Stick, celular/tablet Android, pantallas automotrices. NO compatible todavía: Roku, Samsung/LG nativo, iOS (próximamente).
4. **Nunca escribir en tono de carencia, disculpa o "por ahora" sobre el catálogo.** Nada de "todavía falta una temporada para tenerla completa", "por ahora solo tenés la primera parte", "se puede ir empezando con lo que hay" ni ninguna variante que suene a excusa o a que Bankai+ ofrece algo a medias. (Incidente New Bandits, 2026-09-17 — pedido explícito del usuario.) Bankai+ se para siempre como la mejor plataforma: lo que SÍ está disponible se presenta como un valor completo en sí mismo, nunca como la parte que alcanzó a estar lista. Esto no cambia la regla de no prometer lo que falta en títulos `Incompleto` (ver `crear-texto/SKILL.md`) — simplemente esa ausencia no se menciona ni se pide disculpas por ella; se habla únicamente de lo que hay, en positivo.

## Todo dato de la pieza sale del `tmdbId` exacto del catálogo — nunca de memoria por el nombre del título
Hay bastantes títulos que comparten nombre entre países y versiones (Anna, Lost — hay más de uno —, remakes, etc.): **el nombre del título NUNCA alcanza para saber de qué show se trata.** Ya pasó una vez que se describió el show equivocado con el póster correcto (incidente "Anna", 2026-09-12 — narración completa en `docs/incidentes.md`).

**Esto ahora se verifica mecánicamente.** `producir_lote.py --verificar-tmdb` (incluido en `--todo`) consulta la ficha real de cada `tmdbId` y cruza dos datos contra el `lote.json`:
- **el año**: si la ficha declara 2021 y TMDB dice que ese id es de 2022, el lote se frena — es exactamente la firma del incidente Anna (coreana 2022 vs miniserie española 2021);
- **el idioma original**: determina qué filas de audio corresponden sin depender de `audioDual` ni de adivinar por `categoria`, que es la regla que se violó en 17 piezas publicadas.

El chequeo no reemplaza la verificación humana de la trama — un texto puede describir mal un show del año correcto — pero atrapa el caso que ya ocurrió. Verificado: frena un incidente Anna simulado, y pasa limpio sobre el lote 21 real (14 fichas, cero falsos positivos).

**Regla estricta:**
1. El `tmdbId` de cada item es el que trae el catálogo (`POST/catalogo.json`, reflejo del Excel) — nunca se cambia, nunca se busca "a ojo" uno que parezca correcto.
2. Antes de escribir cualquier sinopsis, tagline, hook o descripción, confirmar que el año, el país/reparto y la trama descritos corresponden a esa ficha puntual de TMDB (`tmdbUrl` del catálogo) — no completar de memoria por el nombre, aunque sea un título conocido.
3. El póster ya verificado es una señal cruzada: si el reparto/idioma del póster no calza con lo que se está por escribir (ej. actores asiáticos en el póster pero un texto describiendo un colegio europeo), es alarma de que se mezclaron dos títulos distintos — parar y reverificar antes de seguir.

## La tira de la ficha de sinopsis SIEMPRE lleva mínimo 2 cuadros, nunca 1
El template (`sinopsis-template.html`) calcula el alto de la tira según la cantidad de imágenes: con 1 sola queda corta y descentrada, y rompe el diseño. **La tira nunca baja de 2 cuadros.** Si TMDB no tiene una segunda imagen realmente distinta y sin logos, usar la mejor alternativa disponible aunque sea muy parecida a la principal (otra resolución o recorte del mismo material) — preferible a romper el diseño con 1 solo cuadro. `producir_lote.py --validar` ya rechaza el lote si una tira tiene menos de 2 cuadros o repite uno. (Incidente 2026-09-12/13, ver `docs/incidentes.md`.)

## Filas de audio/subtítulos en las imágenes
Las imágenes de post llevan filas de info técnica. El criterio que manda es el **idioma original de rodaje/producción del título**, no el booleano `audioDual` solo — ese campo dice si hay doblaje extra, pero no dice a qué idioma está doblado ni cuál es el original. Corregido el 2026-09-05 después de que el sistema anterior (basado solo en `audioDual` + `esAnime`) mostrara "Audio Inglés" en series coreanas/alemanas/etc., o se comiera la fila de idioma original en doramas.

**Paso 1 — determinar el idioma original del título** (no asumir, revisar en este orden):
1. Campo `tercerAudio` del catálogo: si trae un valor que es un idioma real distinto del inglés (`Korean`/`Koreano`, `Portuguese`/`Portugues`/`Portugese`, `Italiano`, `German`, `Hindi`, etc.) — OJO, esa fila es texto libre con errores de tipeo y mayúsculas inconsistentes, y en la mayoría de los casos (`portugues` sobre un show en inglés como Ahsoka o Andor, `Espanol castellano` en Los Simpson) es solo una nota de doblaje EXTRA disponible en un show que sigue siendo en inglés — no cambia el idioma original. Solo cuenta como señal real cuando el título en sí no es angloparlante (con `categoria`, género y conocimiento del título se distingue rápido).
2. Campo `categoria` = `Doramas` → casi siempre coreano o japonés; hay que identificar cuál específicamente (país/estudio de origen), nunca asumir "coreano" a ciegas — ej. "Como Peces Dorados" (Fishbowl Wives) es japonés, no coreano, aunque esté en la misma categoría que series coreanas.
3. Campo `categoria` = `Anime` o `Anime Peliculas`, o `esAnime = true` → japonés. Si el título es evidentemente anime pero `esAnime` viene en `false` en el catálogo (dato incompleto, ej. pasó con Yu-Gi-Oh!), tratarlo igual como japonés — la descripción/hashtags pueden seguir llamándolo anime sin problema, ese flag solo controla esta fila.
4. Ninguno de los catálogos anteriores basta por sí solo: hay títulos que ni `tercerAudio` ni `categoria` marcan (pasó con "Bandidos de Hoy", brasileña, y "Ju-On: Orígenes", japonesa) — si al escribir la sinopsis identificás que el título es una producción extranjera no angloparlante (serie brasileña, dorama, coreana, europea, etc.), aplicá igual la regla de abajo aunque el catálogo no lo marque explícitamente.

**Paso 2 — filas según el idioma original identificado:**
- **Original = español** (LATAM o España, ej. telenovelas, series de España): solo `Audio Esp. Latino`. No hace falta fila de idioma original (ya es el mismo idioma) ni subtítulo.
- **Original = inglés**: sigue el criterio de siempre — `Audio Dual = Sí` → `Audio Esp. Latino` + `Audio Inglés` + `Subtítulo Español`; `Audio Dual = No` → solo `Audio Esp. Latino`.
- **Original = cualquier otro idioma** (coreano, japonés, portugués, italiano, alemán, hindi, etc.): **SIEMPRE las 3 filas** — `Audio Esp. Latino` + `Audio [Idioma Original]` + `Subtítulo Español` — **sin importar lo que diga `audioDual`**. Bankai+ siempre ofrece las tres para contenido extranjero no angloparlante; no usar la ausencia de dato en `audioDual` como excusa para omitir la fila del idioma original o el doblaje latino. Esta es la regla que se venía pasando por alto (corregida a pedido explícito del usuario el 2026-09-05; afectó a 17 piezas ya publicadas, listadas en `docs/incidentes.md`). `producir_lote.py --validar` la chequea antes de renderizar.

Idiomas/banderas ya soportados en la plantilla (`plugin/post-studio/templates/post-template.html`, `FLAG_COLORS`): MX (latino), US (inglés), JP (japonés), KR (coreano), BR (portugués — usar aunque el título no sea brasileño, es la única bandera de portugués definida), IT (italiano), DE (alemán), IN (hindi), CN (chino), TR (turco — agregado 2026-09-14 para el lote de películas, primer título turco del catálogo), ES (subtítulo). Si aparece un idioma original nuevo que no está en esa lista, agregar el gradiente CSS ahí antes de usarlo — nunca approximar con la bandera de otro idioma.

**Ojo con "Doramas" ≠ automáticamente coreano**: la categoría del catálogo agrupa coreano, japonés Y CHINO por igual — "Espera, Mi Juventud" (categoría Doramas) resultó ser china (el póster mostraba texto en pinyin), no coreana. Siempre verificar con el póster/conocimiento del título antes de asumir el idioma dentro de "Doramas".

**Las banderas van SIN el código de dos letras encima** (nunca "MX", "ES", "KR", etc. como texto sobre el ícono) — pedido explícito del usuario el 2026-09-06, aplica a todas las filas de audio/subtítulo de cualquier idioma, no solo a alguna en particular. Solo la bandera sola, el label de al lado ya dice el idioma en palabras. Implementado en `post-template.html`: `flag.textContent` queda siempre vacío.

## Estructura fija de post (Instagram/Facebook)
1. Título del show/película/saga (primera línea, para saber de qué se habla sin leer todo)
2. Hook emocional (1-2 líneas que paren el scroll)
3. CTA fijo: "👉 ¿Querés verla hoy mismo? Escribinos al DM o entrá a bankaiplus.com" (tal cual, sin agregar nada al final)
4. Info técnica: 🎧 Audios disponibles | 📺 Subtítulos disponibles
5. Descripción del show (2-3 líneas humanas, cercanas, sin sonar a IA) — informada por los datos reales del catálogo: año/antigüedad, puntaje, clasificación por edad, temporadas
6. Clasificación por edad en una línea corta y amena: "Apta para toda la familia", "Apta de 7 años en adelante", "Apta para mayores de 13", "Apta para mayores de 18" — nunca advertencias ni sermones
7. Invitación a sumarse a Bankai+ (por qué vale la pena estar adentro, distinto del CTA de contacto) — cierra siempre con "Registrate en nuestra plataforma bankaiplus.com y obten un mes gratis 🤩" (ver nota en `## Planes` — ya no se menciona precio acá)
8. Pregunta de engagement + "¡Cuéntanos en los comentarios! 👇" — **última línea del post, sin nada después**

**Sin hashtags y sin menciones de Costa Rica en el texto del post** — pedido explícito del usuario 2026-09-12. Antes se cerraba con una línea de hashtags (incluyendo uno de geolocalización tipo `#CostaRica`); de ahora en adelante esa línea **no va**, en ningún post nuevo. La segmentación geográfica sigue existiendo para audiencia/horario de publicación (ver más abajo), pero no se escribe en el caption ni en hashtags.

## Cómo debe verse la imagen de arte — SIEMPRE `layout: 'full_bleed'`, NUNCA `panel_lateral`
El template (`post-template.html`) soporta los dos layouts y trae `panel_lateral` como ejemplo por default en su CONFIG de demostración, pero **la casa SIEMPRE usa `full_bleed`** para el arte principal — nunca se usó `panel_lateral` en ninguna pieza real publicada. Un lote generado con `panel_lateral` fue rechazado entero (incidente 2026-09-12, ver `docs/incidentes.md`). Desde 2026-09-14 `producir_lote.py` fija `full_bleed` y `badges: ['1080p']` por código, así que en un lote el layout ya no es una decisión que se pueda equivocar — y no hace falta abrir ningún PNG de referencia para confirmarlo.

**Estructura exacta del arte (`full_bleed`)**, de abajo hacia arriba, todo dentro de una imagen 1080x1350:
1. **Póster completo de fondo** (`posterFull`, `background-size:contain`, centrado) sobre una copia del mismo póster desenfocada y oscurecida (`posterBlur`, cubre todo el canvas) — así no quedan barras negras lisas si el aspect ratio del póster no calza exacto con 1080x1350, se ven blureadas con el propio arte.
2. **Degradado oscuro** desde abajo (para que el texto sea legible sobre cualquier imagen).
3. **Badge dorado "1080p" arriba a la derecha** (`badges: ['1080p']`) — aparece en el 100% de las piezas ya publicadas, siempre incluirlo.
4. **Fila(s) de logo + sitio** (`bankaiplus.com`) pegadas abajo del todo, logo y texto en una misma fila horizontal.
5. **Filas de audio/subtítulo** justo arriba de eso, en fila horizontal (no apiladas en columna) — banderas + label, ver sección de audio más abajo para cuáles filas van.
6. **Título del show** (blanco, negrita, mayúsculas) arriba de las filas, pegado al margen izquierdo.

CONFIG mínimo correcto para el arte:
```
{
  format: 'feed_portrait',
  layout: 'full_bleed',
  posterImage: './poster.jpg',
  title: '...',
  titleFont: 'font-sans',
  titleCase: 'case-upper',
  rows: [...],
  badges: ['1080p'],
  logo: './logo.png',
  site: 'bankaiplus.com'
}
```
`panelColorMode`, `panelColorManual`, `panelWidth`, `decorative`, `posterFocal`, `posterScale` son exclusivos de `panel_lateral` y no aplican ni hace falta tocarlos en `full_bleed` — el motor mide todo solo (alto real del logo, de las filas, etc.) y apila desde abajo.

La imagen de ficha/sinopsis (`sinopsis-template.html`) es un diseño aparte y no tiene este problema — esa sí se armó bien en el incidente del 2026-09-12, no tiene modo "panel" ni "full_bleed", solo su propio layout fijo (tira de pósters + columna de texto + anillo de aprobación).

## Cómo se arma cada pieza de contenido
- **Toda pieza lleva una imagen de ficha/sinopsis** (texto explicativo largo + tira de pósters + % de aprobación), sea post de una imagen o carrusel. Va **última**, después del arte. El texto profundo va ahí; el caption es más corto y más comercial, nunca el mismo párrafo repetido.
- **Las películas de una colección se publican juntas** como carrusel: si una película es parte de una saga, va con toda su saga, no sola.
- **Las series NO se agrupan**: cada serie de una franquicia (las de Digimon, las de The Walking Dead) es su propia pieza, con su propio póster. Serie y películas de la misma franquicia son siempre piezas distintas.
- **Series antológicas** (cada temporada es otra historia, ej. American Horror Story) van como carrusel de temporadas, con el póster propio de cada temporada. Las series de historia continua (Breaking Bad, The Big Bang Theory) van con una sola imagen.
- **Pósters — idioma del texto, en este orden de preferencia**:
  1. **Español LATAM/MX** — pero ojo: TMDB junta España y Latinoamérica en el mismo idioma "es", no los separa. Un póster en "es" **solo sirve si el texto que muestra es como LATAM le dice al título** (comparar contra el `tituloEs` del catálogo, que ya está en español LATAM). Si el póster trae la traducción/título de España (ej. "Perdidos" para lo que acá se conoce como "Lost"), **no sirve aunque sea el único candidato en español** — se descarta igual que si no existiera.
  2. **Nunca español de España/castellano** — ni como texto principal ni como último recurso. No es un idioma aceptable en ningún punto de esta lista, se prefiere inglés antes que castellano.
  3. Si no hay ningún candidato en español LATAM válido: **inglés**.
  4. Si tampoco hay en inglés: sin texto (**textless**).
  5. Solo si no hay nada de lo anterior: el póster default del catálogo (columna Póster), avisando qué idioma trae.
- **Ningún póster puede traer el logo de una plataforma competidora** (la N de Netflix, "A NETFLIX SERIES", HBO, Prime, Disney+). Muchos pósters promocionales de TMDB lo tienen quemado: hay que mirarlos antes de usarlos y descartar los que lo traigan. Es la misma regla de menciones prohibidas, pero dentro de la imagen.
- El detalle operativo de todo esto está en los skills `planear-contenido`, `crear-sinopsis` y `crear-imagen` del plugin post-studio.

## Producción en lote: usar SIEMPRE `producir_lote.py`, nunca rearmar el pipeline

**Cualquier pedido de producir varias piezas dispara este flujo, esté o no escrito con detalle.** "Generame las próximas 10 imágenes del catálogo", "hacé 10 piezas más", "seguí con el siguiente lote", "producime 5 de anime" — todas son lo mismo: andá directo al comando `/lote` (`.claude/commands/lote.md`), que interpreta la cantidad y el filtro de categoría y remite al flujo completo de `plugin/post-studio/commands/cmd-lote.md`. No hace falta que el pedido explique el procedimiento; el procedimiento vive acá.

Al terminar, mostrar siempre las tres cosas sin resumir: la salida completa del motor, la tabla de estadísticas por categoría, y el resultado del QC de pósters (cuántos, en cuántas rondas, y los que no salieron `OK`).

Un lote de piezas se produce con **un solo comando**:

```bash
python plugin/post-studio/skills/crear-imagen/scripts/producir_lote.py <scratch>/lote.json --todo
```

Valida → arma los HTML desde `POST/_template/` → renderiza con Chrome headless a 1080x1350 → deja contact sheet y copias de QC → instala PNG + `post.txt` + `pieza.json`. Lo único que se escribe a mano es el `lote.json`, que son **datos puros** (formato comentado en `scripts/lote.ejemplo.json`). El flujo completo del lote está en el comando `/cmd-lote`.

**Por qué esta regla existe (2026-09-14):** hasta el lote 21 este pipeline se reescribía a mano en una carpeta temporal en cada lote, con los datos incrustados dentro del propio `.py`. Se medió el costo real en los transcripts del proyecto: **2.810 millones de tokens acumulados**, con un solo turno de "producí el siguiente lote" llegando a **127 millones**. El 90% de eso no era trabajo nuevo — era volver a pagar contexto ya acumulado. El motor está verificado contra regresión: reproduce los 24 PNG del lote 21 **byte a byte idénticos**, y los mismos `post.txt` y `pieza.json`.

Reglas derivadas, todas no negociables:
1. **Un lote = una sesión nueva.** El arrastre de conversación es el mayor gasto individual del proyecto. El estado vive en disco (`pieza.json`, `estado-catalogo.json`), no en la conversación.
2. **No rearmar el motor ni sus scripts.** Si algo no entra en el `lote.json`, se corrige el `lote.json`; si falta una capacidad real, se extiende `producir_lote.py` en el repo y se vuelve a correr `--verificar` para probar que el diseño no se movió.
3. **El QC de pósters va por el subagente `qc-posters`** (`.claude/agents/qc-posters.md`), no en la sesión principal. Sigue siendo 100% de los pósters, a resolución completa, uno por uno — lo único que cambia es que las imágenes viven en el contexto del subagente y no en el principal. Si devuelve menos veredictos que pósters enviados, se repiten los faltantes.
4. **Para revisar renders, el contact sheet y las copias de 600px de `<work>/qc/`**, no los PNG de 1080. El PNG de 1080x1350 se renderiza una sola vez y es el que se publica — nunca se baja de resolución para ahorrar. Referencia medida: 24 PNG a 1080 = ~89.000 tokens; contact sheet + 8 copias de 600px = ~7.500, con la misma información útil.

## Orden de producción por lotes (mezclado, no por categoría agotada)
`siguiente_lote.py` recorría el catálogo en orden estricto de vtxId ascendente, lo que agotaba una categoría interna entera (ej. Series) antes de tocar la siguiente (ej. Películas) — con Series ya al 100%, esto significaba decenas de lotes seguidos de solo Anime/Documentales/Infantiles antes de llegar a películas reales. Corregido a pedido explícito del usuario 2026-09-07: **la producción debe alternar tipos** — a veces película, a veces serie, a veces anime, a veces dorama, lo que haya pendiente — no seguir agotando una categoría por orden de catálogo.
- El script ahora soporta `--orden mezclado` (default) que intercala round-robin por categoría interna del catálogo (Series, Doramas, Anime, Peliculas, Peliculas Colecciones, Anime Peliculas, Infantiles Series, Infantiles Peliculas, Documentales, Animados, SHOW), respetando el orden de vtxId dentro de cada categoría. `--orden vtxid` deja el comportamiento viejo disponible si hiciera falta.
- **Después de producir cada lote pedido por el usuario, siempre devolver una tabla de estadísticas** (categoría interna | hechas | total | faltan) igual a la usada el 2026-09-07, para que el usuario vea a simple vista cuántas vueltas de producción automática faltan. `siguiente_lote.py --resumen` ya expone `porCategoria` con estos datos (cuenta piezas, no títulos sueltos — un carrusel de colección cuenta 1).

## Mix de contenido recomendado
70% entretenimiento (recomendaciones, trivia) / 20% producto (planes, CTA directo, comparación de precio) / 10% prueba social (testimonios, capturas, resultados)

## Segmentación geográfica
Priorizar audiencia de Costa Rica y LATAM para horario de publicación (7-10pm hora Costa Rica) y análisis de audiencia — esto es criterio interno de programación, **no texto que se escribe en el post** (ver "Sin hashtags..." arriba: nada de "Costa Rica" ni hashtags de geolocalización dentro del caption).

## Contacto
WhatsApp: +506 6171-9869
Web: bankaiplus.com
