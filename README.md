# Cómo usar este kit

Este proyecto genera y publica contenido de redes sociales para **Bankai+** (bankaiplus.com) usando el plugin **post-studio** (vive en [`plugin/post-studio/`](plugin/post-studio/)). El plugin en sí es genérico — no tiene nada de Bankai+ escrito adentro — y todo lo específico de esta marca (logo, tono, CTA, reglas) vive en [`CLAUDE.md`](CLAUDE.md) y [`brand.config.json`](brand.config.json), en este mismo repo. Si el día de mañana cambia algo de marca, se edita ahí — nunca en el plugin.

Esta página es la referencia rápida de uso, día a día. Para el detalle técnico completo (arquitectura, troubleshooting, cómo agregar un skill nuevo) están [`plugin/post-studio/README.md`](plugin/post-studio/README.md) y [`plugin/post-studio/docs/GUIA-DE-USO.md`](plugin/post-studio/docs/GUIA-DE-USO.md).

## 0. Instalación (una sola vez por PC)
Si es la primera vez que abrís este repo en esta máquina, corré esto en el chat de Claude Code:
```
/plugin marketplace add .
/plugin install post-studio@post-studio-marketplace
```
Después corré `/cmd-setup` una vez — valida (y crea si falta) las carpetas de `POST/`, confirma el logo y `brand.config.json`, revisa que tengas `ffmpeg`/Python/Chrome instalados, y te avisa si falta conectar el navegador Chrome real en Claude. Si algo falta, te va a decir exactamente qué hacer — no vas a tener que adivinar. Correlo también cada vez que algo cambie (PC nueva, logo nuevo, etc.).

## 1. Dos formas de pedir las cosas
- **Comandos** (`/cmd-algo`): los tipeás vos, a propósito. Siempre empiezan con `cmd-` para que se note a simple vista que es un atajo explícito.
- **Lenguaje natural**: no hace falta tipear ningún comando — con pedirlo con tus palabras alcanza (ej. *"hacéme un post de Frieren"*, *"sacame un reel de este video"*). Claude reconoce el pedido y activa el skill correspondiente solo.

Los dos caminos terminan haciendo lo mismo — usá el que te resulte más cómodo en cada momento.

## 2. Comandos disponibles

### `/cmd-catalogo` — sincronizar y consultar el catálogo
**Qué hace:** baja el Excel del catálogo maestro a un espejo local (`POST/catalogo.json`) y te deja consultarlo sin abrir el Excel.
**Cómo pedirlo:**
```
/cmd-catalogo
/cmd-catalogo digimon
/cmd-catalogo pendientes
```
**Antes de correrlo:** dejá el Excel del catálogo (`VORTEX_Catalogo_Master.xlsx`) en la raíz del proyecto. Cada vez que lo actualicés, lo reemplazás y volvés a correr el comando. (Si no está, se puede leer de Drive, pero es mucho más lento y caro.)

### `/cmd-contenido <título o colección>` — la pieza completa, a partir del catálogo
**Qué hace:** es el comando principal cuando el contenido sale del catálogo. Antes de generar nada mira **a qué colección pertenece** el título y decide qué hay que producir: una imagen sola, un carrusel de películas, un carrusel de temporadas, o dos piezas separadas (la serie por un lado, las películas por otro). Después baja los pósters (en español), arma las imágenes, la ficha de sinopsis y el texto.
**Cómo pedirlo:**
```
/cmd-contenido La Purga
/cmd-contenido digimon
```
**Qué vas a obtener:**
```
POST/social/la-purga/
├── post.txt                              ← caption + hashtags
├── pieza.json                            ← qué títulos cubre esta pieza y qué se generó
└── images/
    ├── 01-la-noche-de-la-expiacion.png   ← una imagen por película/temporada
    ├── ...
    └── 06-sinopsis-la-purga.png          ← ficha explicativa (va última, siempre)
```

### `/cmd-post <show/producto>` — post de una sola imagen
**Qué hace:** escribe el texto del post (caption + hashtags) y genera el arte/imagen que lo acompaña, listo para Instagram y Facebook (comparten el mismo texto e imagen).
**Cómo pedirlo:**
```
/cmd-post Frieren, anime, drama y fantasía
```
o en lenguaje natural: *"hacéme un post de Frieren, es anime de drama y fantasía"*.
**Qué te va a preguntar:** datos técnicos si aplican (audios/subtítulos disponibles), layout de la imagen (`full_bleed` por default, o `panel_lateral`), y si además querés un reel para este mismo post.
**Qué vas a obtener:**
```
POST/social/frieren/
├── post.txt              ← caption + hashtags, listo para pegar
├── images/01-frieren.png ← arte final
└── reels/                ← solo si pediste reel también
```

### `/cmd-carousel <coleccion>` — post de varias imágenes
**Qué hace:** arma un solo post con varias imágenes (carrusel) y un único texto que invita a deslizar, a partir de una colección ya guardada en `POST/assets/posters/<coleccion>/`.
**Cómo pedirlo:**
```
/cmd-carousel digimon
```
(`digimon` tiene que ser el nombre de la subcarpeta dentro de `POST/assets/posters/` con las imágenes ya adentro).
**Qué te va a preguntar:** layout (una vez, aplica a todas las imágenes), orden de las imágenes (por default alfabético), título de cada una.
**Qué vas a obtener:**
```
POST/social/digimon/
├── post.txt                       ← un solo texto para todo el carrusel
└── images/
    ├── 01-digimon-adventure.png
    ├── 02-digimon-tamers.png
    └── ...
```

### `/cmd-reel <video(s)>` — reel a partir de video(s) existentes
**Qué hace:** convierte video(s) ya guardados en `POST/assets/videos/` en un reel vertical (9:16) con marca de agua (logo + bankaiplus.com), en uno de tres modos:
- **Highlights**: recorta un solo video a los mejores 15-30s con transiciones.
- **Video completo**: mantiene el video entero sin cortar, solo le da formato vertical.
- **Fusión**: combina los mejores momentos de 2+ videos en un único reel.

**Cómo pedirlo:**
```
/cmd-reel black-knight-trailer.mp4
```
o en lenguaje natural: *"convertime este video completo a reel, sin cortar nada"* / *"fusioná estos 3 videos en un reel"*.
**Qué te va a preguntar:** qué modo usar (si no quedó claro en el pedido), y qué audio usar en modo Highlights/Fusión.
**Qué vas a obtener:** `POST/social/<slug>/reels/<slug>-reel.mp4` (si ya existe uno para ese slug, guarda el nuevo como `-v2.mp4`, `-v3.mp4`, etc. en vez de pisarlo).

### `/cmd-motion <imagen>` — prompt de animación para Kling AI
**Qué hace:** analiza una imagen real y escribe un prompt de movimiento (imagen-a-video) listo para pegar en Kling AI — describe solo qué se mueve y cómo, nunca la apariencia.
**Cómo pedirlo:**
```
/cmd-motion 01-frieren.png
```
**Qué vas a obtener:** el prompt (positivo + negativo) mostrado directo en el chat, en inglés, listo para copiar — no genera ni guarda ningún archivo, solo texto.

### `/cmd-publish <contenido>` — publicar o programar en redes
**Qué hace:** toma contenido ya generado en `POST/social/<slug>/` y lo publica o programa en Instagram/Facebook/X, usando **Zernio primero** y **upload-post.com como respaldo automático** cuando hace falta. Antes de publicar corre una verificación obligatoria de reglas de marca (CTA, menciones prohibidas, tono) — si algo no pasa, se frena y te explica por qué en vez de publicar a medias.
**Cómo pedirlo:**
```
/cmd-publish frieren
```
**Qué te va a preguntar:** cuál publicar (si hay varias piezas listas y no lo aclaraste), fecha/hora real de la publicación, y formato si hay ambigüedad (reel/story/feed).
**Qué esperar:** en el paso de adjuntar el archivo, Claude te va a pedir que vos mismo arrastres el video/imagen a la ventana del navegador — es una limitación de la herramienta, no del plugin, así que hoy no hay scheduling 100% desatendido. Al final te confirma qué se publicó, con qué herramienta, en qué plataformas y para cuándo.

### `/cmd-setup` — chequear/preparar el entorno
**Qué hace:** valida carpetas, `brand.config.json`, logo, software (`ffmpeg`/Python/Chrome) y el conector de Chrome real, todo en un solo paso.
**Cómo pedirlo:** `/cmd-setup` (sin argumentos).
**Cuándo correrlo:** primera vez en una PC nueva, o cada vez que cambie algo del entorno (logo nuevo, PC nueva, algo dejó de andar). Al final te muestra un resumen de qué quedó OK y qué sigue pendiente.

## 3. Dónde queda todo guardado
```
VORTEX_Catalogo_Master.xlsx   ← el catálogo maestro (lo dejás vos acá, no va al repo)
catalogo.config.json          ← cómo leer ese Excel (hoja, columnas)
POST/
├── assets/
│   ├── logo/          ← logo de marca (no tocar el nombre de archivo)
│   ├── posters/        ← pósters fuente; los de una colección van en su subcarpeta
│   │   └── la-purga/    ← un póster por película/temporada de esa pieza
│   ├── videos/           ← videos fuente para reels
│   └── audio/             ← música opcional para reels
├── _template/
│   ├── post-template.html    ← arte de cada título
│   └── sinopsis-template.html ← ficha explicativa
├── social/
│   └── <slug>/             ← una carpeta por PIEZA (puede cubrir varios títulos)
│       ├── post.txt
│       ├── pieza.json       ← qué títulos cubre y qué se generó
│       ├── images/
│       └── reels/
├── catalogo.json        ← espejo local del catálogo (generado, no se edita)
└── estado-catalogo.json ← índice de producción (generado, no se edita)
```

### Catálogo y estado — qué existe y qué ya se hizo
Son dos archivos con dos responsabilidades distintas, y **ninguno de los dos se edita a mano**:

- **`POST/catalogo.json`** — espejo local del Excel: qué títulos existen, a qué colección pertenecen, temporadas, TMDB, calificación, si ya están en la app. Se regenera con `/cmd-catalogo` cada vez que actualizás el Excel.
- **`POST/estado-catalogo.json`** — índice de producción: qué piezas ya se hicieron y qué títulos cubren. Se **regenera leyendo el disco**, así que no puede mentir: si una pieza declara un archivo que no existe, o hay un PNG que ninguna pieza declara, aparece en `problemas`.

La fuente de verdad de cada pieza es su propio **`POST/social/<slug>/pieza.json`**: qué títulos del catálogo cubre (`vtxIds`), qué imágenes tiene, si ya tiene ficha de sinopsis, texto, y si se publicó. Eso es lo que hay que mirar (o preguntar con `/cmd-catalogo <título>`) antes de producir algo, para no repetir trabajo.

## 4. Configuración de marca
`CLAUDE.md` (reglas en prosa) y `brand.config.json` (la misma info, mecánica) tienen todo lo de Bankai+: nombre, sitio, WhatsApp, CTA fijo, tono, menciones prohibidas, reclamos no soportados. Todos los comandos/skills los leen automáticamente — no hace falta pasarles nada de marca a mano. Si algo de esto cambia, actualizá primero `CLAUDE.md` y después pedile a `/cmd-setup` que regenere `brand.config.json`.

## 5. Para escalar después
El plugin está armado para crecer: agregar un skill nuevo (otro tipo de pieza, otra plataforma, otro formato) no rompe lo que ya existe — ver la sección "Agregar un skill nuevo" en [`plugin/post-studio/docs/GUIA-DE-USO.md`](plugin/post-studio/docs/GUIA-DE-USO.md). También se pueden sumar subagentes especializados en `.claude/agents/` (ej. uno que audite reglas de marca antes de publicar). Avisame cuando quieras armar alguna de estas y seguimos.
