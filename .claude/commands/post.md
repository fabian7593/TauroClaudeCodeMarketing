---
description: Generar un post rápido de TauroTV para una serie o película
---

Generá un post para TauroTV sobre: $ARGUMENTS

Este comando es para un post de **una sola imagen**. Si el pedido implica varias imágenes/shows en un mismo post (carrusel), usá el comando `/post-carousel` en su lugar — no lo hagas acá.

Usá el skill post-instagram y seguí todas las reglas de marca definidas en CLAUDE.md. Si falta información clave (audios, subtítulos, tipo de post), preguntame antes de escribir el post final.

Instagram y Facebook están unificados: un solo texto, una sola imagen, guardados en `POST/social/[slug]/` (no generes carpetas separadas `instagram/` y `facebook/`).

## Imagen del post
Además del texto, generá la imagen del post con el skill post-image. Antes de generarla, preguntame (con AskUserQuestion) qué layout usar:
- **Full-bleed** (imagen completa del póster + franja inferior) — esta es la opción por default: si no respondo la pregunta o no queda claro, usá esta.
- **Panel lateral** (con banderas de audio/subtítulo visibles, estilo IPTV/anime).

La imagen de póster/key art para usar tiene que estar en `POST/assets/posters/` — si no está ahí todavía, pedímela antes de generar la imagen (no la busques en otro lado del proyecto).
