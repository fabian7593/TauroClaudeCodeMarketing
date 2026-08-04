---
name: content-setup
description: Verifica y prepara el entorno de post-studio en el proyecto actual — carpetas de contenido, software necesario (ffmpeg/ffprobe/Chrome/Python), brand.config.json, logo de marca, y conectores MCP (como el navegador Chrome real). Úsalo cuando el usuario pida configurar/instalar/preparar el plugin, cuando corra /cmd-setup, cuando el proyecto no tenga brand.config.json todavía, o cuando otro skill de post-studio detecte que algo falta y no pueda seguir sin resolverlo.
---

# content-setup — preflight y bootstrap de post-studio

Este skill es la red de seguridad del plugin: nada de "se rompió y no dijo nada". Cualquier otro skill de post-studio que dependa de algo (una carpeta, un ejecutable, un dato de marca, un conector) puede remitir acá en vez de fallar en silencio o inventar un valor.

No todo chequeo aplica siempre — corré solo lo relevante para lo que el usuario está por hacer (ver tabla al final). `/cmd-setup` corre los 5 pasos completos, pensado para la primera vez que se usa el plugin en un proyecto/PC nueva.

## 1. Carpetas del proyecto
Raíz de contenido: `contentRoot` en `brand.config.json` (ver paso 2) — si `brand.config.json` no existe todavía, asumí `POST/` como default y confirmalo con el usuario en el paso 2.

Verificá que existan (usando `Bash`/`PowerShell`, no asumas):
```
<contentRoot>/assets/posters/
<contentRoot>/assets/videos/
<contentRoot>/assets/audio/
<contentRoot>/assets/logo/
<contentRoot>/social/
<contentRoot>/_template/
```
Si falta alguna, preguntá (una sola vez, todas juntas) si las creás ahora. Si el usuario dice que sí, crealas vacías (con un `.gitkeep` si el proyecto usa git, para que no se pierdan al no tener contenido). Si dice que no, avisá qué comandos van a fallar hasta que existan y por qué.

## 2. brand.config.json
Vive en la raíz del proyecto (al lado de `CLAUDE.md`, si existe). Es una **cache mecánica derivada** — la fuente humana de las reglas de marca sigue siendo `CLAUDE.md` (o el que el proyecto use); este archivo es lo que los demás skills leen para chequeos exactos sin tener que interpretar prosa cada vez.

Si no existe:
1. Si hay un `CLAUDE.md` en la raíz, leelo y proponé valores para los campos de abajo basados en lo que ya dice (no le preguntes al usuario algo que ya está escrito ahí).
2. Para lo que falte, preguntá en un solo batch de preguntas (`AskUserQuestion` si son pocas opciones claras, o preguntas de texto libre si no):

```json
{
  "brandName": "",
  "website": "",
  "whatsapp": "",
  "cta": "",
  "tone": "",
  "contentRoot": "POST",
  "logoFolder": "POST/assets/logo/",
  "logoFile": null,
  "logoAspect": null,
  "colorMode": "auto",
  "colorPrimary": null,
  "colorSecondary": null,
  "forbiddenMentions": [],
  "unsupportedClaims": [],
  "platforms": ["instagram", "facebook"],
  "timezone": ""
}
```

- `cta`: el texto exacto de cierre que va en TODOS los posts (ver reglas de marca del proyecto).
- `colorMode: "auto"` es el default recomendado — el color del panel/branding se calcula del color dominante de cada imagen, funciona para cualquier marca sin configurar nada. Solo pasar a `"manual"` con `colorPrimary`/`colorSecondary` si el usuario pide explícitamente colores fijos de marca.
- `forbiddenMentions`: competidores u otras menciones que la marca no quiere ver en posts orgánicos (puede quedar vacío si no aplica).
- `timezone`: zona horaria real del usuario para programar publicaciones (ej. `America/Costa_Rica`) — si la plataforma de publicación no la tiene en su lista (pasa seguido), `publish-content` ya sabe buscar el offset UTC equivalente más cercano.

3. Escribí el archivo, mostrale al usuario un resumen corto de lo que quedó configurado, y aclará que puede pedir "actualizá mi brand.config" cuando algo cambie (no hace falta borrar el archivo, alcanza con pedir la actualización).

Si ya existe, no lo reescribas sin que el usuario lo pida — solo usalo.

## 3. Logo
Buscá en `<logoFolder>` (default `<contentRoot>/assets/logo/`) archivos `*.png`, `*.jpg`, `*.jpeg`, `*.svg`.

- **Ninguno encontrado**: no sigas — pedile al usuario que suba un logo a esa carpeta (aceptás PNG, JPG o SVG) antes de generar cualquier imagen o video con marca.
- **Uno solo**: usalo.
- **Más de uno**: preguntá cuál es el canónico (si hay un nombre que sugiere "trimmed"/"recortado" vs. el original con padding, proponelo como default y confirmá).
- **Márgenes/padding visible**: si el archivo es PNG/JPG y a simple vista (mirándolo con `Read`) tiene un margen transparente o blanco grande alrededor del logo real, ofrecé generar una versión recortada (guardarla aparte, ej. `<nombre>-trimmed.png`, nunca pisar el original) y usar esa versión recortada para renders. Un logo con margen sin recortar queda chico y descentrado en los templates.
- **SVG**: se puede usar directo en el template HTML (los navegadores lo renderizan nativo). Para el watermark de video (ffmpeg no decodifica SVG), avisale a `reel-highlights` que necesita una versión PNG rasterizada — ese skill la genera una sola vez y la cachea (ver su paso de marca de agua).

Guardá el nombre de archivo final elegido en `brand.config.json` → `logoFile` (y `logoAspect` si ya lo mediste, ver `post-image`) — los demás skills leen ese campo en vez de volver a buscar o de asumir un nombre de archivo fijo.

## 4. Software
Chequeá SOLO lo que aplique a la acción que el usuario está por hacer (no bloquees un post de texto simple por no tener ffmpeg):

| Si el usuario va a... | Verificá |
|---|---|
| generar imagen de post/carrusel | `python --version` (o `python3`), y que exista un navegador Chrome/Chromium (`chrome --version`, `chromium --version`, o rutas típicas de instalación por SO) |
| generar/editar un reel | además: `ffmpeg -version`, `ffprobe -version` |
| publicar/programar | conector de Chrome real (ver paso 5) |

Si falta algo, decí exactamente qué falta y cómo instalarlo según el sistema operativo detectado (`uname` en Bash, o `$PSVersionTable.Platform`/`[System.Environment]::OSVersion` en PowerShell):
- **Windows**: `winget install <paquete>` (ej. `winget install Gyan.FFmpeg`, `winget install Python.Python.3.12`) o Chocolatey si el usuario lo usa.
- **macOS**: `brew install <paquete>`.
- **Linux**: `apt install <paquete>` / `dnf install <paquete>` según la distro.

No instales nada vos mismo sin que el usuario lo pida explícitamente — mostrá el comando y esperá confirmación de que ya lo corrió antes de continuar.

## 5. Conectores MCP
Solo aplica cuando el usuario va a publicar (`publish-content`). Intentá resolver las tools del navegador Chrome real:

```
ToolSearch query: "select:mcp__claude-in-chrome__tabs_context_mcp"
```

- Si el tool aparece con su schema completo → conector disponible, seguí.
- Si no aparece / la búsqueda no devuelve nada usable → avisá: "Para publicar automáticamente necesitás conectar el navegador Chrome en Claude: Settings → Connectors → Chrome. Conectalo y volvé a intentar." No sigas al paso de publicar sin esto.

Si en el futuro otro skill necesita otro conector (ej. Google Drive para traer assets), aplicá el mismo patrón: buscarlo, y si no está, decir exactamente dónde conectarlo — nunca asumir que está y fallar más adelante sin explicar por qué.

## 6. Resumen final
Mostrale al usuario, en una lista corta, qué se validó/creó en esta corrida: carpetas (ya existían / creadas), `brand.config.json` (ya existía / creado / actualizado), logo (ruta encontrada, o pendiente), software (todo OK / qué falta), conectores (OK / pendiente de conectar). Si todo está en verde, decilo explícitamente ("Todo listo para usar post-studio") — no dejes al usuario adivinando si puede seguir.
