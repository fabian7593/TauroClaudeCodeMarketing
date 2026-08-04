---
name: post-carousel
description: Genera un post de carrusel (varias imágenes, un solo texto unificado) para Instagram+Facebook a partir de una colección de imágenes fuente guardadas en una subcarpeta de assets/posters/. Úsalo cuando el usuario pida "un solo post con varias imágenes/productos", un carrusel, o mencione una carpeta de colección dentro de assets/posters/.
---

# post-carousel — post de carrusel (N imágenes, un texto)

Este skill orquesta a `post-image` (una vez por cada imagen) y a `post-copy` (una sola vez, en modo carrusel) para producir **un solo post** con **N imágenes**. No dupliques trabajo: no le pidas al usuario datos que ya te dio en esta misma conversación.

## 0. Ubicación de entrada
`<contentRoot>/assets/posters/<coleccion>/` (`contentRoot` sale de `brand.config.json`) — el usuario organiza ahí las imágenes que van en el carrusel, una subcarpeta por colección. Si la carpeta no existe o está vacía, pedile al usuario que suba las imágenes ahí antes de seguir — no busques imágenes sueltas en otro lado para armar el carrusel.

## 1. Recopilar parámetros (una sola vez para todo el carrusel)
- `layout`: `'panel_lateral'` o `'full_bleed'`. Si no te lo dieron, preguntá — no asumas el default de `/cmd-post` acá, porque este comando se puede invocar solo.
- Info técnica por imagen (si el rubro de la marca la usa, ej. audios/subtítulos): normalmente es la misma para toda la colección — preguntá una vez. Si el usuario aclara que varía por imagen, pedí el detalle por imagen.
- `badges`: una vez, aplica a todas.
- **Orden de las imágenes**: por default, alfabético por nombre de archivo. La primera imagen es la que más pesa para el algoritmo/engagement — preguntale al usuario si quiere un orden específico (ej. "la más nueva primero") en vez de asumir el alfabético.
- Título individual de cada imagen — si los nombres de archivo son claros, proponé los títulos inferidos y pedí confirmación en una sola pregunta batch, no uno por uno.

## 2. Generar cada imagen
Para cada imagen de la colección, en el orden definido, seguí el proceso de `post-image` (sus secciones 1 y 2) con estas particularidades:
- El slug de carpeta es el de la **colección**, no el de cada item: `<contentRoot>/social/<slug-coleccion>/`
- Cada imagen usa el patrón `<NN>-<slug-item>` (`01-digimon-adventure`, `02-digimon-adventure-02`, ...) para el PNG final, numerado según el orden acordado.
- Guardá cada PNG final en `<contentRoot>/social/<slug-coleccion>/images/<NN>-<slug-item>.png` — nada más que el PNG queda en el proyecto (mismo criterio de limpieza que `post-image`, ver su sección 3).
- `posterFocal`/`posterScale` se ajustan por imagen igual que en `post-image` (cada imagen puede necesitar un encuadre distinto).

Podés reusar el mismo servidor de preview (un solo `python -m http.server` para todo el lote) y renderizar las N imágenes en la misma tanda antes de pasar al texto.

## 3. Generar el texto único del post (modo carrusel)
Usá `post-copy`, con estas diferencias respecto a un post de una sola imagen:
- El **hook** debe hablar de la colección completa, no de un item puntual (ej. "Todo el universo Digimon en un solo lugar 🔥" en vez de un hook por temporada).
- Mencioná en el cuerpo que hay varias opciones para descubrir deslizando (ej. "Deslizá para ver las 4 temporadas disponibles 👉").
- El resto de las reglas de marca (`CLAUDE.md`/`brand.config.json`) sigue aplicando igual.
- Guardá en `<contentRoot>/social/<slug-coleccion>/post.txt` (caption + hashtags juntos, como en `post-copy`) — un solo archivo de texto para todo el carrusel, no uno por imagen.

## 4. Entrega
Mostrá las N imágenes generadas (en orden) más el texto único del post, y confirmá cuántas imágenes quedaron, en qué orden, y en qué carpeta (`<contentRoot>/social/<slug-coleccion>/`).
