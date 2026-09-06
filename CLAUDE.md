# Bankai+ — Contexto de Marca para Generación de Contenido

## Qué es Bankai+
Bankai+ es el servicio B2C de streaming de VORTEX TV, dirigido a Costa Rica y el mercado LATAM de habla hispana. Servicio de streaming legal, tecnología neutral, catálogo de 1,000+ títulos (series, películas, anime, infantil).

## Planes
- Basic: $6/mes (USD)
- Standard: ₡4,500/mes
- Family: ₡6,000/mes
- El precio "desde" que se usa en los posts (el más barato, Basic) va en USD con signo $. Standard y Family quedan en colones hasta que se confirme su conversión — no inventar ese tipo de cambio.

## Tono de comunicación
- Español costarricense casual, conjugación "vos"
- Cercano, humano, "peer-like" — nunca suena a IA ni a corporativo
- Hooks emocionales únicos por serie/película — NUNCA reciclados entre posts

## Reglas estrictas (NO NEGOCIABLES)
1. NUNCA mencionar Netflix, HBO Max, Disney+, Prime Video u otras plataformas de streaming en posts orgánicos de Instagram/Facebook/TikTok/YouTube. (Comparación directa SÍ permitida en flyers, FAQs y WhatsApp — pero no en estos posts).
2. CTA fijo en todo post: "👉 ¿Querés verla hoy mismo? Escribinos al DM o entrá a bankaiplus.com" (va cerca del principio del post, no al final — ver estructura abajo). No se agrega ningún otro CTA además de este.
3. Nunca prometer dispositivos no soportados. No existe función de "cast"/mirroring desde el celular — la app se instala directo (por APK o Play Store) en cada dispositivo. Dispositivos compatibles hoy: Smart TV/Box con Android TV, Chromecast con Google TV (instalando la app directo en el dispositivo), Amazon Fire TV Stick, celular/tablet Android, pantallas automotrices. NO compatible todavía: Roku, Samsung/LG nativo, iOS (próximamente).

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
- **Original = cualquier otro idioma** (coreano, japonés, portugués, italiano, alemán, hindi, etc.): **SIEMPRE las 3 filas** — `Audio Esp. Latino` + `Audio [Idioma Original]` + `Subtítulo Español` — **sin importar lo que diga `audioDual`**. Bankai+ siempre ofrece las tres para contenido extranjero no angloparlante; no usar la ausencia de dato en `audioDual` como excusa para omitir la fila del idioma original o el doblaje latino. Esta es la regla que se venía pasando por alto (corregida a pedido explícito del usuario el 2026-09-05, afectó 17 piezas ya publicadas: Black Knight, El Asesino Mediático, El Juego del Calamar, Estamos Muertos, La Casa de Papel: Corea, La Chica Enmascarada, Alice, Aterrizaje de Emergencia en tu Corazón, Bad Guys, Besos Kitty, Como Peces Dorados, Ju-On: Orígenes, Este Mundo No Me Hará Mala Persona, Gul, Dark, Bandidos de Hoy, Evangelion: las películas).

Idiomas/banderas ya soportados en la plantilla (`plugin/post-studio/templates/post-template.html`, `FLAG_COLORS`): MX (latino), US (inglés), JP (japonés), KR (coreano), BR (portugués — usar aunque el título no sea brasileño, es la única bandera de portugués definida), IT (italiano), DE (alemán), IN (hindi), CN (chino), ES (subtítulo). Si aparece un idioma original nuevo que no está en esa lista, agregar el gradiente CSS ahí antes de usarlo — nunca approximar con la bandera de otro idioma.

**Ojo con "Doramas" ≠ automáticamente coreano**: la categoría del catálogo agrupa coreano, japonés Y CHINO por igual — "Espera, Mi Juventud" (categoría Doramas) resultó ser china (el póster mostraba texto en pinyin), no coreana. Siempre verificar con el póster/conocimiento del título antes de asumir el idioma dentro de "Doramas".

**Las banderas van SIN el código de dos letras encima** (nunca "MX", "ES", "KR", etc. como texto sobre el ícono) — pedido explícito del usuario el 2026-09-06, aplica a todas las filas de audio/subtítulo de cualquier idioma, no solo a alguna en particular. Solo la bandera sola, el label de al lado ya dice el idioma en palabras. Implementado en `post-template.html`: `flag.textContent` queda siempre vacío.

## Estructura fija de post (Instagram/Facebook)
1. Título del show/película/saga (primera línea, para saber de qué se habla sin leer todo)
2. Hook emocional (1-2 líneas que paren el scroll)
3. CTA fijo: "👉 ¿Querés verla hoy mismo? Escribinos al DM o entrá a bankaiplus.com" (tal cual, sin agregar nada al final)
4. Info técnica: 🎧 Audios disponibles | 📺 Subtítulos disponibles
5. Descripción del show (2-3 líneas humanas, cercanas, sin sonar a IA) — informada por los datos reales del catálogo: año/antigüedad, puntaje, clasificación por edad, temporadas
6. Clasificación por edad en una línea corta y amena: "Apta para toda la familia", "Apta de 7 años en adelante", "Apta para mayores de 13", "Apta para mayores de 18" — nunca advertencias ni sermones
7. Invitación a sumarse a Bankai+ (por qué vale la pena estar adentro, distinto del CTA de contacto)
8. Pregunta de engagement + "¡Cuéntanos en los comentarios! 👇"
9. Hashtags relevantes

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

## Mix de contenido recomendado
70% entretenimiento (recomendaciones, trivia) / 20% producto (planes, CTA directo, comparación de precio) / 10% prueba social (testimonios, capturas, resultados)

## Segmentación geográfica
Priorizar audiencia de Costa Rica y LATAM. Usar hashtags regionales y horario de publicación 7-10pm hora Costa Rica.

## Contacto
WhatsApp: +506 6171-9869
Web: bankaiplus.com
