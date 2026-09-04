---
name: crear-carrusel
description: Genera un post de carrusel (varias imágenes, un solo texto unificado) para Instagram+Facebook a partir de una colección de imágenes fuente guardadas en una subcarpeta de assets/posters/. Úsalo cuando el usuario pida "un solo post con varias imágenes/productos", un carrusel, o mencione una carpeta de colección dentro de assets/posters/.
---

# crear-carrusel — post de carrusel (N imágenes, un texto)

Este skill orquesta a `crear-imagen` (una vez por cada imagen) y a `crear-texto` (una sola vez, en modo carrusel) para producir **un solo post** con **N imágenes**. No dupliques trabajo: no le pidas al usuario datos que ya te dio en esta misma conversación.

## 0. De dónde sale el carrusel
Dos caminos, según cómo nació el pedido:

- **Desde el catálogo** (lo normal cuando el proyecto tiene uno): el carrusel ya viene decidido por `planear-contenido` — qué títulos entran, en qué orden y por qué (colección de películas, temporadas de una serie antológica, series de una franquicia). **No armes un carrusel de un título que pertenece a una colección sin correr antes `planear-contenido`**: si la saga tiene cinco películas, se publican las cinco, no una. Los pósters se bajan con `tmdb_posters.py` a `<contentRoot>/assets/posters/<slug-pieza>/` (ver `crear-imagen`, sección 0.1).
- **Manual**: `<contentRoot>/assets/posters/<coleccion>/` — el usuario organiza ahí las imágenes, una subcarpeta por colección. Si la carpeta no existe o está vacía, pedile que suba las imágenes ahí antes de seguir — no busques imágenes sueltas en otro lado.

## 0.1 Toda pieza lleva ficha de sinopsis
El carrusel **siempre** incluye la imagen de ficha de `crear-sinopsis`, y va **última**: primero las de arte (`01`, `02`, ...) y al final la ficha con el número siguiente (`06-sinopsis-<slug>.png` en un carrusel de 5). No es opcional.

## 1. Recopilar parámetros (una sola vez para todo el carrusel)
- `layout`: `'panel_lateral'` o `'full_bleed'`. Si no te lo dieron, preguntá — no asumas el default de `/cmd-post` acá, porque este comando se puede invocar solo.
- Info técnica por imagen (si el rubro de la marca la usa, ej. audios/subtítulos): normalmente es la misma para toda la colección — preguntá una vez. Si el usuario aclara que varía por imagen, pedí el detalle por imagen.
- `badges`: una vez, aplica a todas.
- **Orden de las imágenes**: si el carrusel viene del catálogo, **cronológico por año** (así se sigue la saga o la evolución de la franquicia). Si es manual, alfabético por nombre de archivo. En los dos casos la ficha de sinopsis va última, numerada después del último arte. La primera imagen de arte es la que más pesa para el algoritmo — si el usuario quiere otro orden (ej. "la más nueva primero"), preguntáselo antes de renderizar, no después.
- **Un póster distinto por imagen**: cada slide tiene que tener su propio póster. En un carrusel de temporadas eso significa bajar el póster de cada temporada (`tmdb_posters.py --temporada N`), no repetir el de la serie. Si para alguna no hay, avisalo.
- Título individual de cada imagen — si los nombres de archivo son claros, proponé los títulos inferidos y pedí confirmación en una sola pregunta batch, no uno por uno.

## 2. Generar cada imagen
Para cada imagen de la colección, en el orden definido, seguí el proceso de `crear-imagen` (sus secciones 1 y 2) con estas particularidades:
- El slug de carpeta es el de la **colección**, no el de cada item, y vive bajo la categoría que corresponda: `<contentRoot>/social/<categoria>/<slug-coleccion>/`, donde `categoria` es `series` (colección de temporadas de una serie antológica, ej. American Horror Story) o `peliculas` (colección de películas de una saga, ej. La Purga) — la trae resuelta `planear-contenido` en el campo `categoria` de cada grupo; si armás el carrusel a mano, derivala del campo `tipo` del catálogo (Serie → `series`, Película → `peliculas`).
- Cada imagen usa el patrón `<NN>-<slug-item>` (`01-digimon-adventure`, `02-digimon-adventure-02`, ...) para el PNG final, numerado según el orden acordado.
- Guardá cada PNG final en `<contentRoot>/social/<categoria>/<slug-coleccion>/images/<NN>-<slug-item>.png` — nada más que el PNG queda en el proyecto (mismo criterio de limpieza que `crear-imagen`, ver su sección 3).
- `posterFocal`/`posterScale` se ajustan por imagen igual que en `crear-imagen` (cada imagen puede necesitar un encuadre distinto).

Podés reusar el mismo servidor de preview (un solo `python -m http.server` para todo el lote) y renderizar las N imágenes en la misma tanda antes de pasar al texto.

## 3. Generar el texto único del post (modo carrusel)
Usá `crear-texto`, con estas diferencias respecto a un post de una sola imagen:
- El **hook** debe hablar de la colección completa, no de un item puntual (ej. "Todo el universo Digimon en un solo lugar 🔥" en vez de un hook por temporada).
- Mencioná en el cuerpo que hay varias opciones para descubrir deslizando (ej. "Deslizá para ver las 4 temporadas disponibles 👉").
- El resto de las reglas de marca (`CLAUDE.md`/`brand.config.json`) sigue aplicando igual.
- Guardá en `<contentRoot>/social/<categoria>/<slug-coleccion>/post.txt` (caption + hashtags juntos, como en `crear-texto`) — un solo archivo de texto para todo el carrusel, no uno por imagen.

## 4. Entrega
Mostrá las N imágenes generadas (en orden) más el texto único del post, y confirmá cuántas imágenes quedaron, en qué orden, y en qué carpeta (`<contentRoot>/social/<categoria>/<slug-coleccion>/`).
