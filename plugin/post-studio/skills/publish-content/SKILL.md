---
name: publish-content
description: Publica o programa en redes sociales (Instagram, Facebook, X) un contenido ya preparado en la carpeta de contenido del proyecto, usando Zernio como herramienta principal y upload-post.com como respaldo cuando Zernio no se puede usar, vía automatización de navegador en Chrome real (no el navegador sandbox). Úsalo cuando el usuario pida publicar, subir, postear o programar un post/reel a redes sociales.
---

# publish-content — publicar en redes sociales (Zernio + upload-post.com de respaldo)

Esta skill toma contenido YA GENERADO en `<contentRoot>/social/` (por `post-copy`, `post-image`, `post-carousel` o `reel-highlights`) y lo publica o programa en redes sociales reales, usando el navegador **Chrome real del usuario** (herramientas `mcp__claude-in-chrome__*`) — NUNCA el navegador sandbox/preview (`mcp__Claude_Browser__*`), porque ese no tiene las sesiones logueadas del usuario en upload-post.com/Zernio. No genera contenido nuevo — si falta el `post.txt`, las imágenes o el reel, mandá al usuario a la skill correspondiente primero.

Antes de empezar, si no lo hiciste en esta sesión, corré (o al menos consultá) `content-setup` — necesitás el conector de Chrome real disponible y `brand.config.json` para la verificación de marca del paso 6.

**Orden de prioridad de plataformas, siempre**: Instagram > Facebook > X. Cuando haya que recortar plataformas por falta de cupo (ver paso 2), se recortan empezando por la de menor prioridad (X primero, después Facebook). Si el proyecto define otro orden en `brand.config.json` → `platforms`, seguí ese orden en su lugar.

## 0. Elegir la empresa/marca (esta skill NO es exclusiva de un solo proyecto)
Esta skill está pensada para reusarse en cualquier proyecto/empresa que instale el plugin. No asumas ciegamente qué perfil usar:

1. Leé `brand.config.json` y `CLAUDE.md` del proyecto actual — el nombre de marca ahí definido es el default razonable — pero **confirmalo mostrando las cuentas conectadas reales** (handle de Instagram, página de Facebook) antes de publicar, no solo el nombre del perfil.
2. Si hay más de un perfil disponible (en upload-post.com el combobox "Select Profile" en el formulario; en Zernio el dropdown "profiles" al crear un post), o si el usuario menciona otra empresa, preguntale explícitamente cuál usar.
3. Si el perfil/empresa que pide el usuario no existe todavía en ninguna de las dos herramientas, avisale — no lo inventes ni publiques con el perfil equivocado. Creá el perfil solo si el usuario te lo pide explícitamente.

## 1. Identificar qué se va a publicar
Si el usuario ya te dio el contexto (nombre/carpeta) en su mensaje, usalo directo. Si NO — **preguntá primero, no asumas**:
1. Listá las subcarpetas de `<contentRoot>/social/` (cada una es una pieza de contenido).
2. Preguntale al usuario cuál quiere publicar.

Dentro de la carpeta elegida, detectá qué contenido hay disponible:
- `post.txt` → texto base (siempre debería existir; ya trae los hashtags incluidos al final)
- `images/*.png` → 1 imagen = post de imagen única; 2+ = carrusel
- `reels/*.mp4` → reel/video

Si hay más de un tipo disponible (ej. imágenes Y reel para el mismo item), preguntá cuál de los dos publicar (o si son dos publicaciones separadas). Si hay varias versiones de reel (`-v2`, `-v3`...), confirmá cuál es la vigente — normalmente la de número más alto, pero preguntá si hay duda.

## 2. Confirmar fecha/hora real ANTES de preguntar por scheduling
Corré `date` (Bash) para saber el día y hora actuales reales. **No confíes en la fecha que asuma el usuario** — es un error fácil de cometer y cuesta caro (una publicación programada un día tarde). Decilo explícitamente: "hoy es [fecha real], entonces programo para [fecha elegida]".

## 3. Intentar primero con Zernio — upload-post.com es el respaldo
Probá **Zernio primero, siempre**. Solo si Zernio no se puede usar para esta publicación (sin crédito, error de la plataforma, plataforma pedida no conectada ahí, etc.) pasá a **upload-post.com** como respaldo.

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

Esta es también la razón por la que, hoy, esta skill no se puede programar de forma desatendida (ej. con un cron) — siempre necesita a alguien presente para el drag-and-drop del archivo. Si en el futuro Zernio/upload-post.com ofrecen una API o el flujo pasa a curl directo, esta restricción desaparece y recién ahí tendría sentido evaluar scheduling nativo.

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
- **X — obligatorio, no opcional**: X solo tiene "X Title (optional) — Overrides Title", sin campo de descripción separado. Si se deja vacío, hereda el "Title" global completo (multi-párrafo + hashtags), casi nunca deseable en un tweet. Completá **siempre** "X Title" con una versión corta (hook + CTA/link, sin todo el desarrollo ni todos los hashtags — `post-copy` ya genera esta versión corta cuando el post incluye X).
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
