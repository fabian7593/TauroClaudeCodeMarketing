---
description: Generar un post rápido (texto + imagen) para una pieza de contenido
---

Generá un post para: $ARGUMENTS

Este comando es para un post **suelto**, de una sola imagen de arte, cuando el pedido no nace del catálogo. Si el proyecto tiene catálogo y el título está ahí, usá `/cmd-contenido` en su lugar: ese revisa la colección y evita publicar una película sola cuando pertenece a una saga. Si el pedido implica varias imágenes en un mismo post (carrusel), usá `/cmd-carousel`.

Aunque sea una sola imagen de arte, la pieza igual lleva su **ficha de sinopsis** (`crear-sinopsis`) como segunda imagen (`02-sinopsis-<slug>.png`, después del arte) — eso no es opcional.

Usá el skill `crear-texto` y seguí todas las reglas de marca definidas en `CLAUDE.md`/`brand.config.json` de este proyecto (si `brand.config.json` no existe todavía, corré primero el skill `preparar-entorno`). Si falta información clave, preguntame antes de escribir el post final.

Instagram y Facebook están unificados: un solo texto, una sola imagen, guardados en `<contentRoot>/social/<categoria>/[slug]/` (no generes carpetas separadas por plataforma). `categoria` es `series` o `peliculas`, según el `tipo` del catálogo (o preguntame si el título no está en el catálogo).

## Imagen del post
Además del texto, generá la imagen del post con el skill `crear-imagen`. Antes de generarla, preguntame (con `AskUserQuestion`) qué layout usar:
- **Full-bleed** (imagen completa + franja inferior) — esta es la opción por default: si no respondo la pregunta o no queda claro, usá esta.
- **Panel lateral** (con filas de info visibles, ej. audio/subtítulo si aplica al rubro).

La imagen fuente tiene que estar en `<contentRoot>/assets/posters/` — si no está ahí todavía, pedímela antes de generar la imagen (no la busques en otro lado del proyecto).

## Reel (opcional)
Preguntame (con `AskUserQuestion`) si además querés un reel para este post. Si digo que sí:
- Si ya hay un video para esto en `<contentRoot>/assets/videos/`, usalo. Si no, pedime que lo suba ahí antes de continuar — no generes el reel sin un video real.
- Usá el skill `crear-reel` para armarlo (incluye su propia pregunta sobre qué audio usar — no la salteés).
- Guardalo en `<contentRoot>/social/<categoria>/[slug]/reels/` (mismo slug y categoría que el post).

Si digo que no, o no respondo, seguí solo con texto + imagen — no generes el reel por default.
