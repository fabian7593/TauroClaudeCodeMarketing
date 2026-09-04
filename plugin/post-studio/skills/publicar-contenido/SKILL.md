---
name: publicar-contenido
description: Publica o programa en redes sociales (Instagram, Facebook, X) un contenido ya preparado en la carpeta de contenido del proyecto. Camino preferido — Zernio vía API/MCP (`mcp__*__posts_create`), sin intervención manual, ideal para programar en lote o calendarios de varias semanas. Camino de respaldo — automatización de navegador en Chrome real contra Zernio o upload-post.com, para lo que la API no cubre (plataformas no conectadas ahí, o cuando las herramientas MCP no están disponibles en la sesión). Úsalo cuando el usuario pida publicar, subir, postear o programar uno o varios posts/reels a redes sociales.
---

# publicar-contenido — publicar en redes sociales (Zernio API primero, navegador de respaldo)

Esta skill toma contenido YA GENERADO en `<contentRoot>/social/` (por `crear-texto`, `crear-imagen`, `crear-carrusel` o `crear-reel`) y lo publica o programa en redes sociales reales. No genera contenido nuevo — si falta el `post.txt`, las imágenes o el reel, mandá al usuario a la skill correspondiente primero.

**Dos caminos, en este orden de preferencia:**
1. **Zernio API/MCP** (sección 5C) — herramientas `mcp__<id-de-conector-zernio>__posts_create` / `posts_cross_post` / etc. Si aparecen listadas (o las encontrás con `ToolSearch` buscando `posts_create`, `zernio_overview`), **usá este camino por default**, incluso para una sola publicación: no depende de que haya alguien presente para arrastrar un archivo, y es el único camino viable para programar varias publicaciones seguidas (un calendario de semanas) sin gastar una confirmación manual por cada una.
2. **Navegador (Chrome real del usuario)** (secciones 5A/5B) — herramientas `mcp__claude-in-chrome__*` — NUNCA el navegador sandbox/preview (`mcp__Claude_Browser__*`), porque ese no tiene las sesiones logueadas del usuario. Usalo solo cuando el camino 1 no sirve: herramientas MCP no disponibles en la sesión, la plataforma pedida no está conectada en la cuenta de Zernio del MCP (ej. X/Twitter), o el usuario pide explícitamente publicar "a mano"/verificar visualmente antes de confirmar.

Antes de empezar, si no lo hiciste en esta sesión, corré (o al menos consultá) `preparar-entorno` — necesitás `brand.config.json` para la verificación de marca del paso 6, y (si vas por el camino navegador) el conector de Chrome real disponible.

**Orden de prioridad de plataformas, siempre**: Instagram > Facebook > X. Cuando haya que recortar plataformas por falta de cupo o de conexión, se recortan empezando por la de menor prioridad (X primero, después Facebook). Si el proyecto define otro orden en `brand.config.json` → `platforms`, seguí ese orden en su lugar.

## 0. Elegir la empresa/marca (esta skill NO es exclusiva de un solo proyecto)
Esta skill está pensada para reusarse en cualquier proyecto/empresa que instale el plugin. No asumas ciegamente qué perfil usar:

1. Leé `brand.config.json` y `CLAUDE.md` del proyecto actual — el nombre de marca ahí definido es el default razonable — pero **confirmalo mostrando las cuentas conectadas reales** (handle de Instagram, página de Facebook) antes de publicar, no solo el nombre del perfil.
2. Si hay más de un perfil disponible (en upload-post.com el combobox "Select Profile" en el formulario; en Zernio el dropdown "profiles" al crear un post), o si el usuario menciona otra empresa, preguntale explícitamente cuál usar.
3. Si el perfil/empresa que pide el usuario no existe todavía en ninguna de las dos herramientas, avisale — no lo inventes ni publiques con el perfil equivocado. Creá el perfil solo si el usuario te lo pide explícitamente.

## 1. Identificar qué se va a publicar
Si el usuario ya te dio el contexto (nombre/carpeta) en su mensaje, usalo directo. Si NO — **preguntá primero, no asumas**:
1. `<contentRoot>/social/` tiene un nivel de categoría antes de cada pieza (`series/`, `peliculas/`) — listá las subcarpetas de **cada una** de esas dos (`<contentRoot>/social/series/` y `<contentRoot>/social/peliculas/`), no las de `social/` a secas: esa primera listá solo mostraría `series`/`peliculas`, no piezas reales.
2. Preguntale al usuario cuál quiere publicar.

Dentro de la carpeta elegida, detectá qué contenido hay disponible:
- `post.txt` → texto base (siempre debería existir; ya trae los hashtags incluidos al final)
- `images/*.png` → 1 imagen = post de imagen única; 2+ = carrusel
- `reels/*.mp4` → reel/video

Si hay más de un tipo disponible (ej. imágenes Y reel para el mismo item), preguntá cuál de los dos publicar (o si son dos publicaciones separadas). Si hay varias versiones de reel (`-v2`, `-v3`...), confirmá cuál es la vigente — normalmente la de número más alto, pero preguntá si hay duda.

## 2. Confirmar fecha/hora real ANTES de preguntar por scheduling
Corré `date` (Bash) para saber el día y hora actuales reales. **No confíes en la fecha que asuma el usuario** — es un error fácil de cometer y cuesta caro (una publicación programada un día tarde). Decilo explícitamente: "hoy es [fecha real], entonces programo para [fecha elegida]".

## 3. Elegir camino: API (5C) primero, navegador (5A/5B) de respaldo
Antes de tocar el navegador, fijate si las herramientas MCP de Zernio están disponibles (ver sección 5C, punto 1). Si sí, y la plataforma pedida está conectada ahí, **usá 5C y saltate el resto de esta sección** — no hace falta decidir entre Zernio-navegador y upload-post.com.

Si 5C no aplica (herramientas no disponibles, plataforma no conectada en esa cuenta de Zernio, repo privado sin otra forma de hostear el media, o el usuario pidió explícitamente el camino navegador), seguí con el camino navegador de acá abajo: probá **Zernio primero, siempre**. Solo si Zernio no se puede usar para esta publicación (sin crédito, error de la plataforma, plataforma pedida no conectada ahí, etc.) pasá a **upload-post.com** como respaldo.

1. Andá a `https://zernio.com/dashboard/posts-all` (Chrome real, sesión ya logueada — si pide login, avisale al usuario, no intentes loguearte vos). Fijate el saldo de "Free credits" visible en la esquina inferior izquierda — si está en $0 o muy bajo, o si al intentar publicar da un error de crédito/límite, Zernio queda descartado para esta publicación.
2. Fijate qué plataformas están conectadas en Zernio para el perfil elegido (puede variar según el proyecto). Si el usuario pidió una plataforma que no está conectada ahí, Zernio no alcanza para esa plataforma igual — hay que usar upload-post.com para esa.
3. Si Zernio sirve para las plataformas pedidas: seguí directo por el paso **5A (Zernio)**.
4. Si Zernio NO sirve (sin crédito, plataforma no conectada, error persistente tras un reintento razonable): andá a `https://app.upload-post.com/api-keys`, mirá "API Usage" (`CURRENT USAGE` / `USAGE LIMIT`), calculá `restante = USAGE LIMIT - CURRENT USAGE`, y aplicá esta tabla:

| Restante en upload-post.com | Qué hacer |
|---|---|
| ≥ 3 (o ≥ cantidad de plataformas pedidas) | Publicar en **upload-post.com**, todas las plataformas pedidas, orden de prioridad IG > FB > X |
| 2 | Publicar en **upload-post.com**, pero solo **Instagram + Facebook** (se cae X) |
| 1 | Publicar en **upload-post.com**, pero solo **Instagram** |
| 0 | Ninguna de las dos herramientas sirve para esta publicación — avisale al usuario y pedile indicación (ej. esperar al reset de cupo, o agregar crédito a Zernio) |

Seguí por el paso **5B (upload-post.com)**.

Contale siempre al usuario qué herramienta vas a usar y por qué antes de seguir (ej. "Zernio tiene crédito disponible, publico ahí en Facebook e Instagram" o "Zernio no tiene X conectado, para esa plataforma uso upload-post.com"). Si se cae alguna plataforma por límite o conexión, aclará cuál y por qué.

Cada plataforma cuenta como 1 "upload" en upload-post.com. El cupo se resetea mensualmente (fecha visible en "NEXT RESET" de esa misma página).

## 4. Preguntar configuración restante (formato, si aplica)
Antes de preguntar formato, si hay ambigüedad entre reel/imagen o carrusel, dale al usuario contexto breve para decidir informado:

- **Instagram**: los Reels tienen mucho más alcance orgánico que un post de imagen única. Los carruseles rinden mejor que una imagen sola, pero menos que un Reel.
- **Facebook**: mismo patrón — Reels priorizados en el feed, imágenes sueltas con alcance orgánico bajo.
- **X (Twitter)**: no tiene "Reels" ni carrusel deslizable tipo IG — un tweet con varias imágenes las muestra en grilla fija (hasta 4). Un video sube como "el tweet tiene un video", no como formato separado.

Preguntá formato (Reel/Story/Feed, orden del carrusel, etc.) solo si no es obvio por el contenido disponible.

## 5A. Camino Zernio (herramienta principal)
Zernio (`https://zernio.com/dashboard/posts-all`) es más simple que upload-post.com — no tiene el problema de límite de caracteres en el título de Facebook.

1. `navigate` a `https://zernio.com/dashboard/posts-all` (Chrome real, asumí sesión iniciada; si pide login, avisale al usuario).
2. **"+ Create post"**.
3. **profiles**: seleccioná el perfil confirmado en el paso 0 (por default "Default" si solo hay uno).
4. **platforms**: hacé clic en las tarjetas de las plataformas a activar. El ícono de estado de cada tarjeta cambia de un círculo rojo (sin seleccionar/sin media aún) a un check verde una vez seleccionada — el círculo rojo por sí solo mientras no hay media adjunta todavía es normal, no es un error.
5. Campo **"content"** (arriba de todo): pegá el texto completo de `post.txt` — a diferencia de upload-post.com, **tanto Facebook como Instagram usan este mismo campo por default** (Facebook permite hasta 8000 caracteres, Instagram hasta 2200). Solo completá el campo "custom caption" específico de cada plataforma (aparece debajo de cada tarjeta activada) si necesitás un texto distinto para esa plataforma puntual — dejalo vacío para que use el "content" general.
6. **Add media**: ver la restricción dura de subida manual más abajo — pedile al usuario que arrastre el archivo.
7. Por cada plataforma activada vas a ver un toggle **Feed / Story / Reel / Carousel** (Reel se habilita solo cuando hay un video adjunto) — elegí `Reel` si es video, salvo que el usuario pida Story explícita.
8. **publishing**: pestaña "Schedule" (o "Now" si es inmediato), completá **date & time** y **timezone** — Zernio suele tener zonas horarias latinoamericanas directo en la lista; si no tiene la del usuario, usá el offset UTC equivalente más cercano (ver `brand.config.json` → `timezone`).
9. No hay separación de título/descripción por plataforma como en upload-post.com — no hace falta el ajuste especial de Facebook acá.

### ⚠️ Restricción dura: no podés adjuntar el archivo vos mismo
`mcp__claude-in-chrome__file_upload` NO puede leer archivos del proyecto ni de ningún path local — solo archivos ya compartidos con esa sesión del navegador, y con límite de 10MB. Esto pasa con CUALQUIER archivo, chico o grande, en CUALQUIER sitio (Zernio o upload-post.com). **Nunca hagas click vos mismo en el botón/campo de "Add media"** — abre un selector nativo del sistema operativo que no podés ver ni controlar y queda colgado en pantalla. **Siempre** pedile al usuario que arrastre o seleccione el archivo manualmente en el campo de subida de la página (decile el nombre exacto y la carpeta donde está, y pedile que no cierre la ventana hasta que vos confirmes con un screenshot — si el modal se cierra antes de tiempo se pierde todo lo tipeado y hay que empezar de nuevo). Esperá confirmación visual antes de seguir.

Esta restricción es exclusiva del camino navegador. **El camino Zernio API (sección 5C) no la tiene** — ahí la "subida" es una URL pública, no un archivo local, así que no hace falta que nadie esté presente ni arrastre nada. Preferí siempre 5C cuando esté disponible; quedate en el camino navegador solo cuando 5C no cubra la plataforma o la sesión no tenga las herramientas MCP de Zernio cargadas.

## 5C. Camino Zernio API/MCP (preferido — sin intervención manual, sirve para lotes)

Este camino publica llamando directo a las herramientas del conector Zernio (`mcp__<id>__posts_create`, `posts_cross_post`, `accounts_list`, `validate_media`, `usage_get_usage`, etc.) en vez de manejar el navegador. No depende de que el usuario esté mirando ni de arrastrar archivos, así que es el único camino apto para programar un calendario de varias semanas de una sola vez.

**Disparadores típicos de este camino** (el usuario no necesita repetir instrucciones exactas — cualquiera de estas frases alcanza): "programá los próximos N posts en Zernio", "seguí con el calendario de publicación", "llená [días] con contenido distinto al ya programado", "armá el próximo lote de publicaciones". Si no dice cuántas piezas ni qué fechas, preguntá (o inferí de `POST/calendario-publicacion.md` si ya existe: mismo patrón semanal, continuando desde la última fecha ya programada).

0. **Elegir QUÉ piezas programar**: corré `python plugin/post-studio/skills/publicar-contenido/scripts/siguiente_lote_zernio.py --limite N` — devuelve N piezas ya producidas (`pieza.json` con `sinopsis.creada` y `texto.creado`), **saltando automáticamente** cualquier pieza con `publicado.hecho` o `publicado.programado` ya seteado (para no repetir contenido) y las que están reservadas para una época del año que todavía no llega. Si una pieza listada supera 10 imágenes, el script lo avisa — aplicá el punto 5 de acá abajo antes de programarla. No re-derives esta lógica a mano; si el script no cubre un caso nuevo, ajustalo ahí en vez de improvisar en el chat.
   - **Orden: random por default**, no alfabético/secuencial. El catálogo trae el `vtxId` casi alfabético por título dentro de cada categoría, así que ir siempre por el más bajo primero terminaba publicando tandas "todo con A", "todo con B"... — se ve mecánico en el feed. Pedido explícito del usuario (2026-09-03): puede publicarse random. Usá `--orden vtxid` solo cuando el orden importe de verdad (ej. soltar una saga en secuencia a propósito).
1. **Herramientas disponibles**: si no aparecen en el prompt, buscalas con `ToolSearch` (`query: "select:posts_create,accounts_list,validate_media,usage_get_usage,analytics_get_best_time_to_post"` o similar). Si no existen en esta instalación, no hay camino 5C — andá a 5A/5B.
2. **Cuentas**: `accounts_list` para obtener el `account_id` de cada plataforma del perfil confirmado en el paso 0. Guardalos (no cambian entre sesiones salvo que se reconecte la cuenta).
3. **Plan/cupo**: si hay duda de si el plan cubre las plataformas o el volumen pedido, `usage_get_usage` (rango `cycle`) — mirá `lineItems`: si el ítem de "Connected Accounts" tiene un "Free Tier Credit applied" que lo deja en $0 neto, el plan gratuito ya cubre esas cuentas sin costo extra.
4. **Media = URL pública, no archivo local**. `media_urls` (o el parámetro equivalente) solo acepta URLs accesibles desde internet, comma-separated. Para imágenes que viven en `<contentRoot>/social/<categoria>/<slug>/images/` de este repo:
   - El archivo tiene que estar **comiteado Y pusheado** al remoto de GitHub (`git status -sb` sin líneas de diff pendientes para esas imágenes, y `git log origin/main..HEAD` vacío). Si no está pusheado, la URL da 404 aunque exista en tu disco — pusheá primero.
   - Si el repo es público, la URL es `https://raw.githubusercontent.com/<owner>/<repo>/<branch>/<ruta-relativa-al-repo>` (mismo `archivo` que ya guarda `pieza.json`, con `\` cambiado a `/`).
   - Si el repo es privado, esta técnica no sirve sin autenticación adicional — usá el camino navegador, o `media_generate_upload_link`/equivalente si el conector lo ofrece (ese sí requiere al usuario subiendo por navegador, una vez, así que perdés la ventaja de "sin intervención manual").
   - Antes de programar un lote grande, validá al menos una imagen nueva con `validate_media` (devuelve tamaño, tipo, y si entra dentro del límite de cada plataforma) — no asumas que el hosting funciona.
5. **Límite de carrusel — 10 elementos, sin excepción, en Instagram y Facebook**. Si `pieza.json` tiene más de 10 imágenes en su carrusel de arte (colecciones grandes, series antológicas con muchas temporadas), **no se puede publicar completo en un solo post** — hay que recortar a 10 para ESTA publicación puntual, sin tocar los archivos originales de la pieza (esos quedan completos para archivo/futuro uso, ej. si el proyecto alguna vez postea directo a un sitio propio sin ese límite):
   - Contá TODAS las imágenes del post (arte + la ficha de sinopsis al final) — el límite es sobre el total, no solo sobre el arte.
   - Para elegir cuáles sacar: si hay datos de calificación/popularidad por ítem, sacá los de menor calificación/reconocimiento primero. Si no hay datos objetivos, usá criterio informado (temporadas o entregas peor recibidas por crítica/audiencia) y **decile al usuario cuáles sacaste y por qué** — es una decisión de curación, no la escondas.
   - La ficha de sinopsis va siempre incluida como última imagen (no cuenta como una de las "descartables").
6. **Calcular `schedule_minutes`** (minutos desde ahora, no timestamp absoluto — así funciona el parámetro de este conector): tomá la hora UTC actual real (`date -u` por Bash) y la hora objetivo en la zona horaria del proyecto (`brand.config.json` → `timezone`; Costa Rica es UTC-6 fijo, sin horario de verano). `minutos = (objetivo_UTC - ahora_UTC) en minutos`. Si programás muchas fechas de una vez, generá la lista completa primero (script Python en el scratchpad de la sesión) y verificala antes de empezar a llamar a la herramienta — un error de zona horaria repetido 24 veces es carísimo de corregir después.
7. **Una llamada por plataforma**: la mayoría de estos conectores exponen `posts_create` con un solo `platform`/`account_id` por llamada (repetí la llamada por cada plataforma con el mismo `content`/`media_urls`/`schedule_minutes`) y a veces también `posts_cross_post` para varias a la vez — pero ojo, `posts_cross_post` puede no aceptar una demora de programación custom (revisá su descripción: algunos solo programan "a 1 hora de ahora" en modo scheduled). Para un calendario con fechas específicas, usá `posts_create` por plataforma, no `posts_cross_post`.
8. **Verificación de marca** (paso 6 de esta skill) aplica igual acá, ANTES de la primera llamada del lote — revisala una vez sobre el texto/plantilla y confiá en que se repite igual en cada pieza si vas iterando sobre varias.
9. **Confirmá cada respuesta**: la herramienta devuelve el ID del post y la fecha programada (normalmente en UTC) — usalo para verificar que cayó en la fecha/hora esperada, no asumas que el cálculo de minutos salió bien sin chequear al menos el primero del lote contra la hora local esperada.
10. **Marcá el tracking**: después de programar, actualizá `pieza.json` de cada pieza con un campo `publicado.programado` (`fecha`, `plataformas`, `via: "zernio"`) — **no** marques `publicado.hecho: true` todavía, eso es para cuando la publicación ya salió en vivo (Zernio no expone ese estado por MCP hoy; si el proyecto necesita saber qué salió realmente en vivo, hay que consultarlo aparte, ej. `posts_list` con `status: "published"` cerca de la fecha programada). Corré `estado.py regenerar` después.
11. **Actualizá `POST/calendario-publicacion.md`** (si existe en el proyecto) agregando las piezas y fechas nuevas a su lista — es la fuente de verdad de qué se programó y cuándo, no lo dejes solo en la memoria de la conversación.

## 5B. Camino upload-post.com (respaldo, cuando Zernio no sirve para esta publicación)
1. `navigate` a `https://app.upload-post.com/` (Chrome real, asumí sesión iniciada; si pide login, avisale al usuario, no intentes loguearte vos).
2. **Calendar > "+ Crear"**.
3. Perfil: el confirmado en el paso 0.
4. "Upload Media File" → plataformas: las decididas en el paso 3.
5. Campo **"Title"** global: pegá el texto completo de `post.txt`.
6. Ver la misma restricción dura de subida manual del paso 5A — aplica igual acá.

### Ajustes específicos por plataforma en upload-post.com
- **Facebook — límite de 255 caracteres en el título**: NO dejes que Facebook herede el "Title" global completo (falla con "Facebook title is too long" si el caption pasa de 255 caracteres, que es casi siempre). Completá manualmente:
  - **"Facebook Title (optional)"**: el hook / primera línea del post, corto.
  - **"Facebook Description (optional)"**: el texto completo del post.
  - **"Facebook Post Type"**: `Reel` si es video (ya suele venir así por default), o el tipo que corresponda si es imagen.
- **Instagram**: no tiene campo de título propio — el "Title" global ES el caption que se publica tal cual. "Reel Type" ya viene en "Regular Reel" con "Share to Feed" por default, dejalo así salvo Story explícita.
- **X — obligatorio, no opcional**: X solo tiene "X Title (optional) — Overrides Title", sin campo de descripción separado. Si se deja vacío, hereda el "Title" global completo (multi-párrafo + hashtags), casi nunca deseable en un tweet. Completá **siempre** "X Title" con una versión corta (hook + CTA/link, sin todo el desarrollo ni todos los hashtags — `crear-texto` ya genera esta versión corta cuando el post incluye X).
- **Timezone**: si la lista no tiene la zona horaria exacta del proyecto (`brand.config.json` → `timezone`), usá el offset UTC equivalente más cercano disponible en la lista.

## 6. Verificación de marca — OBLIGATORIA antes de publicar, en cualquiera de los dos caminos
Repasá el texto final ensamblado (el que realmente va a quedar en cada plataforma) contra `brand.config.json` y `CLAUDE.md` del proyecto actual — no asumas reglas de una marca distinta a la configurada acá:

- [ ] No aparece ninguna palabra de `brand.config.json` → `forbiddenMentions`
- [ ] Incluye el `cta` de `brand.config.json` tal cual (si el proyecto define uno fijo)
- [ ] No promete nada de `brand.config.json` → `unsupportedClaims`
- [ ] El tono coincide con `brand.config.json` → `tone`
- [ ] El texto corresponde al contenido/carpeta que se está publicando (coherencia)
- [ ] El archivo adjunto en el preview es el correcto (nombre y contenido visual coinciden con lo esperado)
- [ ] Si se recortó el texto para X, el CTA y la esencia del hook se mantienen
- [ ] Las cuentas/handles conectados corresponden a la empresa confirmada en el paso 0

Si CUALQUIERA de estos falla, **DETENÉTE, no publiques**, y contale al usuario exactamente qué encontraste y por qué no seguiste — no lo arregles en silencio ni lo publiques igual.

## 7. Publicar
Si la verificación del paso 6 pasó limpia, hacé clic en el botón final ("Schedule Post" en ambas herramientas, o el equivalente de "publicar ya") sin volver a preguntarle "¿confirmás?" al usuario — esta skill fue pedida explícitamente para operar así. Después:
1. Confirmá visualmente que se programó/publicó (screenshot del calendario, o mensaje de éxito).
2. Mostrale al usuario un resumen corto: qué se publicó, con qué herramienta (upload-post.com o Zernio, y por qué esa), en qué plataformas, con qué formato, y cuándo (fecha/hora exacta, aclarando la zona horaria real del usuario).

## 8. Si algo sale mal
Si la herramienta devuelve un error (límite de caracteres, campo requerido faltante, sin crédito/cupo, plataforma no conectada, etc.), leé el mensaje exacto, arreglá lo que corresponda, y reintentá — no le pases el error crudo al usuario sin antes intentar resolverlo vos. Si el error es justamente de que Zernio no sirve para esta publicación (sin crédito, error persistente, plataforma no conectada), volvé al paso 3 y pasá a upload-post.com como respaldo, aplicando su tabla de cupo. Si ambas herramientas fallan, explicaselo al usuario y pedile indicación — no elijas publicar a medias ni con datos incompletos.
