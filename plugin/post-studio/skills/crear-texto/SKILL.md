---
name: crear-texto
description: Escribe el texto (caption + hashtags) de un post de Instagram/Facebook/TikTok/YouTube Shorts para la marca configurada en este proyecto, siguiendo sus reglas de tono y de marca. Úsalo cuando el usuario pida crear, redactar o armar el texto de un post para un producto/show/servicio/anuncio.
---

# crear-texto — texto de post para redes sociales

Este skill NO genera imágenes ni videos (eso lo hacen `crear-imagen`, `crear-carrusel` y `crear-reel`) — genera únicamente el **texto** del post: caption, hashtags, y (si aplica) guion corto para formatos de video vertical.

## 0. Marca del proyecto
Antes de escribir una sola línea, leé `CLAUDE.md` y `brand.config.json` en la raíz del proyecto (ver skill `preparar-entorno` si `brand.config.json` no existe todavía — corré ese skill primero, no inventes reglas de marca). De ahí sale: tono de voz, CTA fijo de cierre, menciones prohibidas, reclamos que no se pueden prometer, y estructura de post si el proyecto define una propia.

Si el proyecto no tiene ningún archivo de reglas de marca, preguntale al usuario por lo mínimo indispensable antes de escribir: nombre de marca, tono deseado, y si hay un CTA fijo que siempre tiene que aparecer.

## 1. Recopilar datos
Si falta información, preguntá:
- Nombre del producto/show/servicio y categoría/género
- Datos técnicos relevantes si aplican (ej. audios e idiomas de subtítulos disponibles, si la marca es de streaming/video)
- Tipo de post (entretenimiento / producto / prueba social — o el mix que defina el proyecto)
- Plataforma de destino (Instagram, Facebook, TikTok, YouTube Shorts, X) — el texto base es similar entre Instagram/Facebook, pero TikTok/Shorts necesitan además un guion corto de video, y X necesita una versión recortada (ver paso 4).

## 1.1 Si el contenido viene de un catálogo con datos de TMDB
Si el proyecto tiene espejo local del catálogo, sacá los datos de ahí primero (es gratis y ya está normalizado):
```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/sincronizar-catalogo/scripts/consultar_catalogo.py" ver "<título o VTX-id>"
```
De ahí salen `anio`, `generos`, `calificacion`, `clasificacion`, `temporadas`, `episodios`, `duracionMin`, `estado`, `coleccion`. Lo único que el espejo **no** trae es la sinopsis: para eso sí abrí la página de TMDB (`tmdbUrl`) con `WebFetch`.

Datos que hay que usar (no son decorativos — cambian lo que se escribe):
- **Sinopsis real**: usala como base de la "Descripción" del paso 2 — reescribila con tu propia voz y tono de marca, nunca la copies textual (es contenido de terceros) ni la resumas de forma genérica ("una historia de acción y aventura" sirve poco — contá algo puntual de esa sinopsis que enganche).
- **Género(s)**: informa el hook, la descripción y los hashtags — no fuerces géneros que no aparecen ahí.
- **Clasificación por edad** (ej. `TV-Y7`, `PG`, `TV-MA`, `R`): si es apta para toda la familia (`G`, `PG`, `TV-Y`, `TV-Y7`, `TV-G` o equivalente), podés mencionarlo como algo positivo ("para ver en familia", etc.) — si NO lo es (`R`, `TV-MA`, `NC-17` o equivalente), no la vendas como apta para todo público, y evitá un tono que sugiera que es para chicos.
- **Calificación** (puntaje, ej. 8.2/10): usala como dato de prueba social si suma al hook o a la descripción ("una de las mejor calificadas del catálogo", etc.) — no la repitas si no aporta nada natural a la frase, y no la satures de decimales tipo "calificación de 8.234".

- **Año / antigüedad**: cambia el ángulo del texto. Un estreno reciente se vende como novedad; un clásico de hace 20-30 años se vende por nostalgia o por "si no la viste, es el momento". No trates un título de 1992 como si fuera un estreno.
- **Temporadas / episodios / duración**: sirven para el argumento de "maratón" (muchas temporadas) o de "se ve en una noche" (miniserie, película corta). Nunca prometas más temporadas de las que dice el catálogo.
- **Estado `Incompleto`** (+ `notas`): faltan temporadas o episodios. El texto **no puede** decir "completa", "todas las temporadas" ni "de principio a fin". Se puede publicar igual, pero sin prometer lo que falta.
- **Colección**: si el título pertenece a una saga y la pieza cubre la colección entera, el texto habla de la saga, no de un título suelto (ver `planear-contenido`).

**Cómo se dice la edad en el post** (una línea corta, amena y descriptiva — nunca un sermón tipo "no la veas con los chiquitos"):

| Clasificación | Cómo se escribe |
|---|---|
| `G`, `TV-Y`, `TV-G` | Apta para toda la familia |
| `PG` | Apta para toda la familia, mejor con un adulto cerca |
| `TV-Y7` | Apta de 7 años en adelante |
| `PG-13`, `TV-14` | Apta para mayores de 13 |
| `R`, `TV-MA` | Apta para mayores de 18 |
| `NC-17` | Solo para adultos |

Va como un dato más, en su propia línea o integrada a la descripción — corta, sin explicar por qué ni advertir de nada.

## 2. Escribir el post
Seguí la estructura de post que defina `CLAUDE.md` del proyecto. Si no define una estructura propia, usá esta por default:
1. **Título** — el nombre del título/colección como primera línea, para que se sepa de qué se habla sin leer todo
2. Hook emocional (1-2 líneas que paren el scroll)
3. CTA agresivo con la acción que la marca quiera (comprar, escribir al DM, visitar el sitio)
4. Info técnica relevante si aplica
5. Descripción cercana, humana, sin sonar a IA (2-3 líneas) — informada por la sinopsis real de TMDB y por los datos del paso 1.1 (edad, puntaje, temporadas), nunca genérica
6. **Clasificación por edad**, en una línea corta y amena (ver tabla del paso 1.1)
7. **Invitación a sumarse a la plataforma** — una línea que invite a entrar/suscribirse, distinta del CTA de contacto: el CTA dice cómo escribir, la invitación dice por qué vale la pena estar adentro
8. Pregunta de engagement
9. Hashtags (ver paso 3)

**El caption no es la ficha.** Si la pieza lleva imagen de sinopsis (`crear-sinopsis`, y lleva siempre), el texto largo y profundo va **en la imagen**; el caption es más corto y más comercial. No repitas el mismo párrafo en los dos lados: el que lee la imagen y después el caption tiene que encontrar algo nuevo, no el mismo texto copiado.

**Emojis**: salvo que `CLAUDE.md`/`brand.config.json` del proyecto pida lo contrario, no uses emojis en el hook, la descripción ni la pregunta de engagement — el texto tiene que sentirse escrito por una persona, no decorado. La única excepción es el `cta` fijo de `brand.config.json`: si ese texto ya trae emojis definidos como parte de la marca, van tal cual están, no se los saques ni se los agregues a mano en otro lado del post.

Verificaciones obligatorias antes de entregar (mecánicas, no "a ojo" — chequealas una por una contra `brand.config.json`):
- [ ] El hook es único, nunca reutilizado en posts anteriores de esta cuenta
- [ ] No aparece ninguna palabra de `forbiddenMentions`
- [ ] No se promete nada de `unsupportedClaims`
- [ ] Se incluye el `cta` fijo tal cual está en `brand.config.json` (con sus emojis, si los tiene definidos)
- [ ] El tono coincide con `tone`
- [ ] Sin emojis fuera del `cta` fijo (ver arriba)
- [ ] Si había sinopsis de TMDB disponible, la descripción refleja algo real de ahí — no es un relleno genérico
- [ ] Si el título no es apto para toda la familia, el post no lo presenta como tal
- [ ] Está el título arriba, la línea de edad y la invitación a sumarse a la plataforma
- [ ] Si el catálogo marca el título como `Incompleto`, el texto no promete temporadas o episodios que faltan
- [ ] El texto no repite el párrafo de la imagen de sinopsis
- [ ] El texto **vende**: nada de describir el título en negativo ("no pasa gran cosa", "no hay sorpresas"). Lo que es una virtud se escribe como virtud
- [ ] Los datos duros (año, temporadas, edad, puntaje) coinciden con el catálogo y con la ficha de sinopsis
- [ ] El texto completo (caption + hashtags) entra en el límite de Instagram, 2200 caracteres — es la plataforma más chica de las que arma esta skill; si lo pasa, recortá la descripción antes que el CTA, la edad o los hashtags
- [ ] Cada hashtag es una sola palabra pegada (`#EjemploAsi`), sin espacios adentro — ver formato técnico en el paso 3

**Control final de la pieza**: antes de dar la pieza por terminada, leé el `post.txt` **y** el texto ya renderizado en la imagen de sinopsis, juntos. Recién ahí se puede decir que está lista: si los dos textos se contradicen, se repiten o alguno no cumple, se corrige antes de entregar.

## 3. Hashtags — van DENTRO del mismo texto, no aparte
Generá 5-8 hashtags relevantes (categoría/nicho del contenido, geografía si la marca tiene mercado específico, y marca) y ponelos al final del mismo bloque de texto. **Nunca un hashtag con el nombre de una plataforma competidora** (`#Netflix`, `#HBOMax`, `#DisneyPlus`, `#PrimeVideo`) — pasa fácil cuando el título es un spinoff/adaptación conocido de esa plataforma (ej. universo La Casa de Papel, Marvel, un anime de temporada). Es la misma regla de `forbiddenMentions` que ya se chequea en el cuerpo del texto; revisala también en los hashtags, no solo en las primeras líneas. — **no los guardes en un archivo separado**, van pegados abajo del caption porque así es como se pegan en la plataforma real.

**Formato técnico del hashtag — un espacio adentro lo rompe en dos palabras sueltas** y la plataforma deja de reconocerlo como hashtag desde ahí (ej. `#ParaToda LaFamilia` se publica como el hashtag `#ParaToda` seguido del texto plano "LaFamilia", visible pero sin funcionar como etiqueta — pasó una vez en este proyecto y no se notó hasta programar la publicación). Antes de dar un hashtag por terminado:
- Sin espacios ni signos de puntuación adentro (`CamelCase` para separar palabras: `#ParaTodaLaFamilia`, no `#Para Toda La Familia` ni `#Para-Toda-La-Familia`).
- Sin tildes ni eñes si el resto de los hashtags de la pieza tampoco las llevan (consistencia dentro del mismo post).
- Repasá el bloque final de hashtags carácter por carácter buscando un espacio de más — es el error más fácil de cometer al armarlos a mano y el más fácil de no ver en una lectura rápida.

## 4. Adaptaciones por plataforma
- **TikTok/Shorts**: además del caption, generá un guion de 15-30 segundos con marcas de tiempo simples (0-3s hook visual, 3-15s desarrollo, 15-30s CTA).
- **X**: además del caption largo, generá una versión corta (hook + CTA, sin todo el desarrollo ni todos los hashtags) — X no tiene espacio para el post completo.

No generes acá un prompt de imagen ni de animación — si el usuario necesita eso, es el skill `generar-prompt-movimiento` (a partir de una imagen real) el que lo cubre; ese prompt se muestra en el chat, no se guarda como archivo de este post.

## 5. Guardar en la carpeta del proyecto
La raíz de contenido es `contentRoot` de `brand.config.json` (default `POST/` si no está configurado). Instagram y Facebook comparten el mismo texto e imagen — van en una única carpeta, no dupliques contenido en carpetas separadas por plataforma. Dentro de `social/` hay un nivel de **categoría** antes del slug — `series` o `peliculas` — para no mezclar ambos tipos de contenido en el mismo listado:

```
<contentRoot>/social/<categoria>/[slug]/
├── post.txt          (caption + hashtags juntos, listo para copiar y pegar)
├── images/            (lo produce crear-imagen / crear-carrusel)
├── reels/              (lo produce crear-reel, si aplica)
├── tiktok/
│   └── guion.txt        (solo si el post es para TikTok/Shorts)
└── youtube-shorts/
    └── guion.txt
```

`slug` en minúsculas y guiones (ej. `frieren`, `dragon-ball-z`). `categoria` sale del campo `tipo` del catálogo del título (Serie → `series`, Película → `peliculas`) — si el pedido viene de `planear-contenido`, ya te la da resuelta en el campo `categoria` de cada grupo; si no, preguntale al usuario o inferila del título antes de crear la carpeta. Si `<contentRoot>/social/<categoria>/[slug]/` no existe, creala. Si el post lleva imagen, usá el skill `crear-imagen` (o `crear-carrusel` si son varias) para producirla dentro de `images/`.

## 6. Confirmación final
Después de guardar `post.txt`, mostrá en el chat un resumen corto de qué se creó y en qué ruta, más el texto completo del post para que el usuario lo revise sin abrir el archivo.
