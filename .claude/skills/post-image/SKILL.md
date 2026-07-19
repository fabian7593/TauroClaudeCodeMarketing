---
name: post-image
description: Genera el arte de imagen de un post de TauroTV (layout "panel lateral" con banderas de audio/subtítulo, o "full bleed" con el póster completo) a partir del template HTML reutilizable del proyecto. Úsalo cuando haya que crear/exportar la pieza visual (PNG) para un post de Instagram/Facebook, a partir de una imagen de póster/key art del show.
---

# Generador de imagen de post — TauroTV

Este skill NO escribe el texto del post (eso lo hace `post-instagram`) — genera únicamente el **arte/imagen** (PNG) que acompaña al post, usando el template reutilizable de [POST/_template/post-template.html](../../../POST/_template/post-template.html).

## 0. Ubicaciones fijas del proyecto
- **Template HTML** (no se edita nunca directamente, se copia): `POST/_template/post-template.html`
- **Pósters/key art de origen**: `POST/assets/posters/` — el usuario deja ahí las imágenes (jpg/png/webp) que se van a usar. Si te pide generar la imagen de un show y no te dice el archivo, buscá en esa carpeta el archivo cuyo nombre se parezca al título, o el modificado más recientemente si el usuario acaba de decir "ya la subí".
- **Logo de marca**: `POST/assets/logo/TauroTV_Logo_trimmed.png` (ya recortado, no tiene margen transparente — no uses `TauroTV_Logo.png`, ese tiene padding y rompe la alineación).
- **Carpeta cortes/PNG de color**: no existe más — el color del panel se calcula en runtime a partir del color dominante de la imagen (no hace falta ni hay que descargar assets de color).

## 1. Recopilar parámetros
Preguntá lo que falte (no asumas):

| Parámetro | Cómo se resuelve |
|---|---|
| `layout` | `'panel_lateral'` o `'full_bleed'`. Si el comando que invoca este skill ya preguntó y tiene default, usá ese. |
| imagen de póster | Nombre de archivo dentro de `POST/assets/posters/`. Si el usuario no la subió todavía, pedísela antes de continuar (no podés generar la imagen sin ella). |
| `title` | Nombre del show/película tal cual se debe mostrar. |
| `rows` (audios/subtítulos) | Lista de `{code, label}`. Preguntá audios e idiomas de subtítulos si no los tenés (mismo dato que ya pide `post-instagram`, reusalo si ya lo tenés de esa conversación). |
| `format` | `'feed_portrait'` (1080x1350, default para feed) / `'feed_square'` (1080x1080) / `'reel_story'` (1080x1920, para Reels/Stories). Default: `feed_portrait`. |
| `badges` | Calidad: `'480p' \| '720p' \| '1080p' \| '4k' \| 'bluray'`. Default `['1080p']` salvo que el usuario diga otra cosa. |
| color del panel (solo panel_lateral) | Default `panelColorMode:'auto'` (color dominante de la imagen). Solo pasar a `'manual'` con un hex si el usuario pide explícitamente un color fijo. |

### Códigos de bandera disponibles
`MX` (Esp. Latino), `US` (Inglés), `ES` (Español/España), `JP` (Japonés), `BR` (Portugués/Brasil), `AR` (Argentina), `NEUTRO` (genérico/neutro). Si hace falta un idioma sin código definido, agregá una entrada nueva a `FLAG_COLORS`/`FLAG_TEXT_COLOR` en el HTML generado (no rompe nada, es solo CSS).

## 2. Crear el archivo de esta pieza
Instagram y Facebook están unificados (mismo post, mismo folder — ver skill `post-instagram`). Copiá el template a la carpeta del post (no edites `post-template.html` directamente — es el canónico reutilizable):

```
POST/social/<slug-del-show>/<NN>-<slug-item>.html
```

`<slug-del-show>` en minúsculas y guiones (ej. `digimon-adventure`). `<NN>` es un número de orden con cero a la izquierda (`01`, `02`...) — usalo siempre, incluso para un post de una sola imagen (queda `01-<slug-item>.html`), así el mismo patrón sirve para posts simples y para carruseles (ver skill `post-carousel`) sin tener que cambiar de convención.

Copiá también la imagen de póster desde `POST/assets/posters/` hacia esa misma carpeta como `<NN>-<slug-item>-source.<ext>` (mantiene el proyecto autocontenido por post).

Editá el objeto `CONFIG` al inicio del `<script>` con los parámetros del paso 1. **No toques nada fuera de `CONFIG`** salvo que el resultado visual lo requiera (ver troubleshooting abajo).

⚠️ **Ojo con las rutas relativas al mover el archivo**: `post-template.html` vive en `POST/_template/` (un nivel bajo `POST/`), y la copia queda en `POST/social/<slug>/` (**dos** niveles bajo `POST/` — la misma profundidad, no cambia aunque el archivo tenga prefijo numérico). Los valores por default de `CONFIG.logo` y `CONFIG.posterImage` están pensados para la profundidad de `_template/` — ajustalos siempre a:
- `logo: '../../assets/logo/TauroTV_Logo_trimmed.png'` (dos `../`, no uno)
- `posterImage: './<NN>-<slug-item>-source.<ext>'` (mismo folder, nombre con el prefijo numérico del paso anterior)

Verificá siempre el PNG renderizado antes de entregarlo — si el logo sale como ícono de imagen rota, es este problema de ruta.

### Guía obligatoria para `posterFocal` / `posterScale` (solo panel_lateral)
Mirá la imagen de póster antes de fijar estos valores:
- Ubicá dónde está el logo/título original del show y la cara/acción principal.
- `posterFocal` (formato `'X% Y%'`) debe dejar ese contenido **fuera** de la franja que tapa el panel (aprox. el `panelWidth` configurado, medido desde la izquierda).
- Si el logo original queda cortado o tapado, subí `posterFocal` X hacia la derecha o bajá `posterScale` (menos zoom = menos recorte).
- En `full_bleed` no hace falta tocar estos valores — se ve la imagen completa siempre (contain, con fondo desenfocado si no llena el canvas).

## 3. Levantar el preview y renderizar

1. Asegurate de que `.claude/launch.json` tenga la config `post-preview-server` (sirve `POST/` en el puerto 8791 vía `python -m http.server`). Si no existe, creala.
2. `preview_start` con `name: "post-preview-server"`.
3. Renderizá con **Chrome headless** (más confiable que capturas de pantalla del Browser pane para tamaños exactos). Comando de referencia — ajustá el tamaño según `format`:

```
chrome.exe --headless=new --disable-gpu --no-sandbox --hide-scrollbars \
  --user-data-dir="C:\ct2\profile" \
  --screenshot="<ruta-salida>.png" \
  --window-size=<W>,<H> --force-device-scale-factor=1 --virtual-time-budget=3000 \
  "http://localhost:8791/social/<slug>/<NN>-<slug-item>.html"
```

Notas de esta máquina (ya resueltas, no las re-investigues):
- Usá un `--user-data-dir` en una ruta **corta** (ej. `C:\ct2\profile`), no dentro de rutas largas de `AppData\Local\Temp\...` — ahí falla con "Access is denied" por longitud/permisos de path.
- `--no-sandbox` es necesario en este entorno.
- `--virtual-time-budget=3000` es obligatorio — sin eso la captura sale en blanco/incompleta porque el color dominante y el tamaño del póster se calculan de forma asíncrona (canvas + carga de imagen).
- Tamaños por `format`: `feed_square`=1080x1080, `feed_portrait`=1080x1350, `reel_story`=1080x1920.

4. Verificá el resultado con la tool `Read` sobre el PNG generado antes de darlo por bueno — mirá que: el logo/título original no esté tapado, las filas de idioma no se corten ni se peguen, y el color del panel combine con la imagen.
5. Copiá/movés el PNG final a `POST/social/<slug>/images/<NN>-<slug-item>.png` — esta carpeta `images/` es la que usa el post final (sirve tanto para Instagram como Facebook, es un solo asset).
6. Limpiá el `--user-data-dir` temporal si corresponde.

## 4. Troubleshooting conocido
- **Texto con tildes/emoji rotos (`InglÃ©s`)**: problema de encoding al generar el HTML por script — escribí el archivo con UTF-8 sin BOM (`New-Object System.Text.UTF8Encoding $false` en PowerShell, o el `Write`/`Edit` normal de Claude Code, nunca `Get-Content`/`Set-Content` de PowerShell sin especificar `-Encoding utf8` explícito).
- **Filas de idioma que chocan con el logo (full_bleed)**: el layout mide alturas reales en el DOM (`getBoundingClientRect`) para evitarlo — si modificás el template y ves que vuelve a pasar, no vuelvas a "adivinar" alturas con porcentajes fijos, mantené el patrón de medición real.
- **El panel tapa el logo original del show**: ajustá `posterFocal`/`panelWidth`, ver guía arriba.
- **Screenshot del Browser pane sale recortado/chico**: usar Chrome headless (paso 3) en vez de la tool `computer` — es más confiable para tamaños exactos de export final.

## 5. Entrega
Mostrá el PNG final al usuario (`SendUserFile` si está disponible en la sesión; si no, pasale la ruta del archivo como link) y confirmá layout/formato/color usados antes de darlo por terminado.
