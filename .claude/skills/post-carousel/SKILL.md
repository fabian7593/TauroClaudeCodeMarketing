---
name: post-carousel
description: Genera un post de carrusel (varias imágenes, un solo texto unificado) para Instagram+Facebook a partir de una colección de pósters guardados en una subcarpeta de POST/assets/posters/. Úsalo cuando el usuario pida "un solo post con varias imágenes/shows", un carrusel, o mencione una carpeta de colección dentro de assets/posters/.
---

# Generador de post en carrusel — TauroTV

Este skill orquesta a `post-image` (una vez por cada imagen) y a `post-instagram` (una sola vez, en modo carrusel) para producir **un solo post** con **N imágenes**. No dupliques trabajo: no le pidas al usuario datos que ya te dio en esta misma conversación.

## 0. Ubicación de entrada
`POST/assets/posters/<coleccion>/` — el usuario organiza ahí las imágenes que van en el carrusel (una subcarpeta por colección, ej. `assets/posters/digimon/`). Si la carpeta no existe o está vacía, pedile al usuario que suba las imágenes ahí antes de seguir — no busques pósters sueltos en otro lado para armar el carrusel.

## 1. Recopilar parámetros (una sola vez para todo el carrusel)
- `layout`: `'panel_lateral'` o `'full_bleed'`. Si no te lo dieron, preguntá — no asumas el default de `/post` acá, porque este comando se puede invocar solo.
- Audios/subtítulos: normalmente son los mismos para toda la colección (ej. mismo catálogo JP/MX/ES para todos los Digimon) — preguntá una vez. Si el usuario aclara que varían por imagen, pedí el detalle por imagen.
- `badges` (calidad): una vez, aplica a todas.
- **Orden de las imágenes**: por default, alfabético por nombre de archivo. La primera imagen del carrusel es la que más pesa para el algoritmo/engagement — preguntale al usuario si quiere un orden específico (ej. "la más nueva primero", "la más popular primero") en vez de asumir el alfabético.
- Título individual de cada imagen (nombre del show/temporada tal cual va en el arte) — si los nombres de archivo son claros (ej. `DigimonAdventure02.webp`), proponé los títulos inferidos y pedí confirmación en una sola pregunta batch, no uno por uno.

## 2. Generar cada imagen
Para cada póster de la colección, en el orden definido, seguí el proceso de `post-image` (sección 2 y 3 de ese skill) con estas particularidades:
- El slug de carpeta es el de la **colección**, no el de cada show: `POST/social/<slug-coleccion>/`
- Cada imagen usa el patrón `<NN>-<slug-item>` (`01-digimon-adventure`, `02-digimon-adventure-02`, ...) tanto para el `.html` de trabajo como para el PNG final, numerados según el orden acordado.
- Guardá cada PNG final en `POST/social/<slug-coleccion>/images/<NN>-<slug-item>.png`.
- `posterFocal`/`posterScale` se ajustan por imagen igual que en `post-image` (cada póster puede necesitar un encuadre distinto).

Podés reusar el mismo servidor de preview (`preview_start` una sola vez) y renderizar las N imágenes en la misma tanda antes de pasar al texto.

## 3. Generar el texto único del post (modo carrusel)
Usá `post-instagram`, pero con estas diferencias respecto a un post de una sola imagen:
- El **hook** debe hablar de la colección completa, no de un show puntual (ej. "Todo el universo Digimon en un solo lugar 🔥" en vez de un hook por temporada).
- Mencioná en el cuerpo que hay varias opciones para descubrir deslizando (ej. "Deslizá para ver las 4 temporadas disponibles 👉").
- El resto de la estructura de CLAUDE.md sigue aplicando igual (CTA fijo de cierre, sin mencionar competidores, etc.)
- Guardá en `POST/social/<slug-coleccion>/post.txt` y `POST/social/<slug-coleccion>/hashtags.txt` — un solo archivo de texto para todo el carrusel, no uno por imagen.

## 4. Entrega
Mostrá las N imágenes generadas (en orden) más el texto único del post, y confirmá cuántas imágenes quedaron, en qué orden, y en qué carpeta (`POST/social/<slug-coleccion>/`).
