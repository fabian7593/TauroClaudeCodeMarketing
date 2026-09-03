---
name: crear-imagen
description: Genera el arte de imagen de un post (layout "panel lateral" con filas de info tipo audio/subtítulo, o "full bleed" con la imagen completa) a partir del template HTML reutilizable del plugin, usando el logo y colores de la marca configurada en este proyecto. Úsalo cuando haya que crear/exportar la pieza visual (PNG) para un post de Instagram/Facebook, a partir de una imagen fuente (póster/key art/producto) del proyecto.
---

# crear-imagen — arte de imagen de un post

Este skill NO escribe el texto del post (eso lo hace `crear-texto`) — genera únicamente el **arte/imagen** (PNG) que lo acompaña.

Requiere que `preparar-entorno` ya se haya corrido al menos una vez en este proyecto (o corrélo ahora si `brand.config.json` no existe) — de ahí sale el logo resuelto y los colores de marca.

## 0. Ubicaciones
- **Template canónico** (nunca se edita directo): `${CLAUDE_PLUGIN_ROOT}/templates/post-template.html`. Si el plugin llega a incluir más de un diseño en el futuro (`${CLAUDE_PLUGIN_ROOT}/templates/*.html`), preguntá cuál usar cuando haya más de uno — hoy hay uno solo.
- **Copia editable del proyecto**: `<contentRoot>/_template/post-template.html` (`contentRoot` sale de `brand.config.json`, default `POST/`). Si no existe todavía, copiala desde el template canónico del plugin — esa copia es la que se edita/personaliza a partir de ahora, nunca vuelvas a pisarla automáticamente con la del plugin una vez que existe (solo si el usuario pide explícitamente "resetear el template").
- **Imágenes fuente**: `<contentRoot>/assets/posters/` — el usuario deja ahí las imágenes (jpg/png/webp) a usar. Si no te dice el archivo, buscá ahí el que se parezca al nombre pedido, o el modificado más recientemente si el usuario acaba de decir "ya la subí". Si el proyecto tiene catálogo, el póster también se puede bajar solo (ver sección 0.1). Las piezas de varios títulos van en subcarpeta: `<contentRoot>/assets/posters/<slug-pieza>/`.
- **Logo**: el que resolvió `preparar-entorno` en `brand.config.json` → `logoFolder` + `logoFile`. Si `logoFile` está vacío, corré el paso de logo de `preparar-entorno` antes de seguir — no asumas un nombre de archivo.

## 0.1 Elegir el póster (cuando el proyecto tiene catálogo con TMDB)
El póster que trae el catálogo suele ser el default de TMDB, casi siempre con el texto en inglés. **Regla: si el póster tiene texto, ese texto tiene que estar en español (LATAM/MX).**

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/crear-imagen/scripts/tmdb_posters.py" \
  --id <tmdbId> --tipo movie|tv --descargar "<contentRoot>/assets/posters/<slug>/<NN>-<slug-item>.jpg"
```

El script busca en **español**. Si TMDB no tiene ninguno, sale con código 2 y no baja nada: en ese caso **usá el póster default del catálogo** (columna `posterUrl`, casi siempre en inglés) y **avisáselo al usuario** al entregar la imagen. No busques reemplazo en otro idioma ni cambies de título: mejor el default conocido que un póster raro. Con `--indice N` elegís otro candidato de la lista (útil cuando el primero es feo o no se entiende a tamaño chico), y con `--temporada N` traés los pósters de una temporada puntual.

**Pósters por temporada**: cuando la pieza es un carrusel de temporadas (serie antológica, o una entrada de TMDB que junta varias series — ver `planear-contenido`), **cada temporada necesita su propio póster**: `--tipo tv --temporada <n>`. No repitas el póster principal de la serie en todas las imágenes: si cada temporada cuenta una historia distinta, tiene que verse distinta. Si TMDB no tiene póster propio para una temporada, decílo y usá el de la serie para esa sola.

**Mirá el póster antes de usarlo** (`Read`) — no es opcional, y no alcanza con mirar el nombre del archivo:
- Que el título se entienda y no sea una imagen recortada rara.
- Que el idioma del texto sea el que decís que es.
- **Que no traiga el logo ni el nombre de NINGUNA plataforma de streaming**, no solo las de `forbiddenMentions` — esa lista es el mínimo explícito, pero la regla de marca es "ninguna plataforma de streaming", punto. Ya aparecieron en la práctica: la "N" roja de Netflix, "A NETFLIX SERIES", "ONLY ON…", "HBO Original"/"HBO Max", "MAX Original", el logo de Disney+, y también otras menos obvias como **Showtime** o **Apple TV+** — cualquier sello de una plataforma competidora cuenta, la esté buscando o no. TMDB está lleno de pósters promocionales con esa marca quemada. Si el candidato la trae, descartalo y pasá al siguiente (`--indice N`), o usá una versión sin texto (`--idioma xx`). El chequeo de texto automático (`forbiddenMentions`) no ve esto — es SIEMPRE un chequeo visual, mirando el póster.

## 1. Recopilar parámetros
Preguntá lo que falte (no asumas):

| Parámetro | Cómo se resuelve |
|---|---|
| `layout` | `'panel_lateral'` o `'full_bleed'`. Si el comando que invoca este skill ya preguntó y tiene default, usá ese. |
| imagen fuente | Nombre de archivo dentro de `<contentRoot>/assets/posters/`. Si el usuario no la subió todavía, pedísela antes de continuar. |
| `title` | Nombre del producto/show tal cual se debe mostrar. |
| `rows` (info técnica, ej. audios/subtítulos) | Lista de `{code, label}` — solo aplica si el rubro de la marca usa ese tipo de dato (ej. streaming). **Si el proyecto define reglas para estas filas en `CLAUDE.md` (qué fila va según qué dato del catálogo), seguilas al pie: no las completes a ojo ni prometas un audio o subtítulo que el catálogo no confirma.** Reusá el dato si ya lo tenés de esta misma conversación (`crear-texto` suele preguntarlo también). |
| `format` | `'feed_portrait'` (1080x1350, default feed) / `'feed_square'` (1080x1080) / `'reel_story'` (1080x1920). Default: `feed_portrait`. |
| `badges` | Etiqueta de calidad/destacado opcional. Default vacío salvo que el usuario pida uno. |
| color del panel (solo panel_lateral) | Default `brand.config.json.colorMode` (normalmente `'auto'` = color dominante de la imagen, funciona para cualquier marca sin configurar nada). Solo pasar a colores manuales (`colorPrimary`/`colorSecondary`) si el usuario pide explícitamente colores fijos. |

## 2. Render en carpeta de trabajo temporal (no en el proyecto)
Para evitar arrastrar archivos intermedios al repo y evitar cuentas de rutas relativas por profundidad de carpeta, todo el trabajo de esta sección pasa en el **directorio scratchpad de esta sesión de Claude Code** (el indicado en tus instrucciones de sistema), no dentro de `<contentRoot>/`:

1. Copiá ahí, como archivos hermanos (mismo nivel, sin subcarpetas):
   - la copia editable del template → `work.html`
   - el logo resuelto → `logo.<ext>` (mismo `<ext>` que el archivo real; si es `.svg` y más adelante hace falta rasterizarlo para otro skill, no es necesario acá — el HTML renderiza SVG nativo)
   - la imagen fuente elegida → `source.<ext>`
2. Editá el bloque `CONFIG` de `work.html` con los parámetros del paso 1, más:
   - `logo: './logo.<ext>'`
   - `posterImage: './source.<ext>'`
   - `site: brand.config.json.website`
   - si `colorMode` es `'manual'`: `panelColorMode:'manual'`, `panelColorManual: brand.config.json.colorPrimary`
   
   Como todo queda al mismo nivel, las rutas relativas son siempre `./archivo`, sin importar cuántos niveles tenga `<contentRoot>/social/<slug>/` — no hay matemática de `../..` que se pueda romper al mover el post a otra carpeta.
3. Serví ese directorio con un servidor local simple (`python -m http.server <puerto> --directory <scratch-dir>` — si el proyecto ya tiene un `.claude/launch.json` con una entrada de preview server para contenido, reusala; si no existe, creala apuntando al `contentRoot`, no al scratch, para que sirva también como preview interactivo a futuro).
4. Renderizá con **Chrome headless** (más confiable que capturas del Browser pane para tamaños exactos):

```bash
chrome.exe --headless=new --disable-gpu --no-sandbox --hide-scrollbars \
  --user-data-dir="<ruta-corta-temporal>" \
  --screenshot="<salida>.png" \
  --window-size=<W>,<H> --force-device-scale-factor=1 --virtual-time-budget=3000 \
  "http://localhost:<puerto>/work.html"
```

Notas ya resueltas (no las reinvestigues):
- La ruta de `--screenshot` tiene que ser **absoluta**. Con ruta relativa, Chrome termina con código 0, no imprime error **y no escribe el archivo** — parece que funcionó y no hay PNG.
- **Usá `/` (forward slash), no `\`, incluso en Windows** — Chrome los acepta igual. Si armás la ruta con una variable de shell justo después de `\` (ej. `--screenshot="C:\ct2\${out}.png"`), en este entorno de Bash el `${out}` puede no expandirse y Chrome termina intentando escribir el nombre literal `${out}.png` (falla con "Access is denied", sale con código 0 y no genera archivo — el mismo síntoma que una ruta relativa, así que es fácil confundir los dos). Con `/` el problema no aparece: `--screenshot="C:/ct2/${out}.png"`.
- `--user-data-dir` en una ruta **corta** (ej. `C:\ct2\profile` en Windows) — rutas largas de `AppData\Local\Temp\...` fallan con "Access is denied" por longitud/permisos.
- `--no-sandbox` necesario en entornos sin sandbox de usuario configurado.
- `--virtual-time-budget=3000` obligatorio — sin eso la captura sale en blanco/incompleta porque el color dominante y el tamaño del póster se calculan de forma asíncrona.
- Tamaños por `format`: `feed_square`=1080x1080, `feed_portrait`=1080x1350, `reel_story`=1080x1920.

5. Verificá el PNG con la tool `Read` antes de darlo por bueno: el logo/título original no debe quedar tapado, las filas de info no se cortan ni se pegan, el color del panel combina con la imagen, y el logo se ve completo y bien proporcionado (el template mide el aspect ratio real del logo al cargarlo, así que un logo distinto siempre se ve correcto sin ajustar nada a mano).

### Guía para `posterFocal`/`posterScale` (solo panel_lateral)
Mirá la imagen fuente antes de fijar estos valores:
- Ubicá dónde está cualquier texto/logo propio de la imagen y el sujeto/acción principal.
- `posterFocal` (formato `'X% Y%'`) debe dejar ese contenido **fuera** de la franja que tapa el panel.
- Si algo queda cortado o tapado, subí `posterFocal` X hacia la derecha o bajá `posterScale` (menos zoom = menos recorte).
- En `full_bleed` no hace falta tocar estos valores — se ve la imagen completa siempre.

## 3. Guardar el resultado final y limpiar
- Copiá **solo el PNG final** a `<contentRoot>/social/<slug>/images/<NN>-<slug-item>.png` (`<NN>` con cero a la izquierda: `01`, `02`... — mismo patrón para post simple o carrusel, ver skill `crear-carrusel`).
- **Terminá el proceso del servidor** (`python -m http.server`) antes de borrar la carpeta scratch, no solo los archivos — un `http.server` sigue vivo en background aunque termine el comando que lo lanzó, y mientras esté vivo mantiene la carpeta bloqueada en Windows (el borrado falla con "Device or resource busy" aunque los archivos ya no se estén usando). Si lo lanzaste con `&`, matalo por PID (ej. buscar el puerto con `netstat -ano | grep ":<puerto>"` y terminar ese PID) antes de intentar borrar la carpeta.
- Borrá todo lo demás del directorio scratch de esta corrida (`work.html`, `logo.<ext>`, `source.<ext>`, el `--user-data-dir` temporal) — en `<contentRoot>/social/<slug>/` no debe quedar nada más que el PNG final. No se guardan copias de trabajo ni copias de la imagen fuente dentro del proyecto.

## 4. Troubleshooting conocido
- **Texto con tildes/emoji rotos (`InglÃ©s`)**: problema de encoding al generar el HTML por script — escribí el archivo en UTF-8 sin BOM (el `Write`/`Edit` normal de Claude Code ya lo hace bien; si usás PowerShell directo, especificá `-Encoding utf8` explícito, nunca `Get-Content`/`Set-Content` sin eso).
- **Filas de info que chocan con el logo (full_bleed)**: el layout mide alturas reales en el DOM (`getBoundingClientRect`) para evitarlo — si modificás el template y vuelve a pasar, no "adivines" alturas con porcentajes fijos, mantené el patrón de medición real.
- **El panel tapa contenido de la imagen original**: ajustá `posterFocal`/`panelWidth`, ver guía arriba.
- **Screenshot recortado/chico**: usar Chrome headless (paso 2.4) en vez de la tool `computer` del Browser pane — más confiable para tamaños exactos de export final.
- **Logo desproporcionado o cortado**: no debería pasar (el aspect ratio se mide del archivo real al cargar, no está hardcodeado) — si pasa, revisá que `logo.<ext>` se haya copiado bien al scratch y que la ruta en `CONFIG.logo` apunte ahí.

## 5. Entrega
Mostrá el PNG final al usuario (`SendUserFile` si está disponible; si no, la ruta del archivo) y confirmá layout/formato/color usados antes de darlo por terminado.
