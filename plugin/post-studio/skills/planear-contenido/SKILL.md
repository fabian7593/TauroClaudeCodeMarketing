---
name: planear-contenido
description: Decide QUÉ piezas hay que producir para un título del catálogo antes de generar nada: si va como imagen individual o carrusel, si hay que dividir por temporadas, y si la colección entera (secuelas, spin-offs, películas de la misma franquicia) tiene que ir junta. Úsalo siempre como primer paso cuando el pedido nace de un título/colección del catálogo, antes de crear-imagen, crear-carrusel, crear-sinopsis o crear-texto.
---

# planear-contenido — qué piezas armar para un título

Un título del catálogo casi nunca es "un post". Puede ser una imagen sola, un carrusel de temporadas, un carrusel de películas, o **dos piezas separadas**. Este skill decide eso **antes** de generar nada, para no producir contenido incompleto que después haya que rehacer.

Regla de oro: **nunca produzcas una pieza de un título sin antes mirar su colección.** Una película suelta que pertenece a una saga se publica con toda su saga, no sola.

## 1. Traer el grupo del catálogo
```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/sincronizar-catalogo/scripts/consultar_catalogo.py" grupo "<título o VTX-id>"
```
Devuelve el título pedido + toda su colección, ya separada en `series` y `peliculas`. Si `catalogo.json` no existe todavía, corré primero el skill `sincronizar-catalogo`.

### Si el título no tiene `coleccion` cargada
Pasa seguido (ej. una serie de anime y sus películas que quedaron sin colección en la planilla). No asumas que está solo: buscá por la palabra clave de la franquicia:
```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/sincronizar-catalogo/scripts/consultar_catalogo.py" buscar "evangelion" --limite 20
```
Si aparecen hermanos evidentes (misma franquicia, distinto `tipo`/`categoria`), **proponé el grupo al usuario y pedí confirmación** antes de seguir. No inventes la agrupación en silencio.

Cuando el usuario confirma un grupo que el Excel no tiene, anotalo en **`catalogo.overrides.json`** (raíz del proyecto) para que sobreviva a la próxima sincronización:
```json
{ "colecciones": { "Evangelion": ["VTX-0286", "VTX-1264", "VTX-1265", "VTX-1266", "VTX-1267"] } }
```
y decile al usuario que conviene cargar esa colección también en el Excel, para que algún día el override sobre.

## 2. Chequear qué ya está hecho
```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/planear-contenido/scripts/estado.py" estado "<título o VTX-id>"
```
Si ya hay pieza para esos `vtxIds`, avisale al usuario antes de duplicar trabajo (puede querer regenerarla, ampliarla o saltarla).

## 3. Decidir las piezas

| Caso | Qué se produce |
|---|---|
| **Película suelta** (sin colección) | 1 pieza: imagen individual |
| **Serie de historia continua** (Breaking Bad, The Big Bang Theory) | 1 pieza: imagen individual. **No** dividir por temporada: es la misma historia, una imagen por temporada no aporta nada |
| **Serie antológica** (cada temporada es una historia distinta: American Horror Story) | 1 pieza: **carrusel de temporadas con TODAS las temporadas**, una imagen por temporada, cada una con su propio póster — **no se curan a 3-4** como las colecciones de películas grandes; eso solo aplica a la tira de la ficha de sinopsis (ver abajo), nunca al carrusel de arte |
| **Varias series de la misma franquicia** (las 7 de Digimon, las de The Walking Dead) | **Una pieza por serie, cada una con su propio póster.** Las series NO se agrupan en un carrusel de franquicia: cada serie tiene su público, su época y su arte, y merece su propio post |
| **Varias películas de la misma colección** (las 5 de La Purga, las de El Juego del Miedo) | 1 pieza: **carrusel de películas**, en orden cronológico |
| **Serie + películas de la misma franquicia** (Evangelion, La Purga) | **Piezas separadas**: cada serie por su lado, y las películas juntas en un carrusel aparte. Nunca mezclar serie y películas en el mismo carrusel |

**Agrupar es solo para películas.** Las películas de una colección van juntas porque se ven como saga; las series no: cada serie de una franquicia es una pieza propia.

En todos los casos, la pieza lleva **además** su imagen de ficha/sinopsis (skill `crear-sinopsis`) — eso no es opcional ni depende de si es carrusel o imagen sola. Va **al final**: primero el arte (`01`, `02`, ...) y la ficha como **última** imagen.

### El caso difícil: una entrada de catálogo que en realidad son varias historias
TMDB a veces junta como **una sola serie con N temporadas** lo que en realidad son series distintas (Digimon Adventure y Digimon Adventure 02 bajo un mismo ID; los arcos de Bleach). Señales de que estás ante esto:
- La columna `temporadas` dice "1 a N" pero el título del catálogo abarca varias series conocidas.
- Cada temporada tiene nombre propio en TMDB (no "Temporada 1", "Temporada 2").
- Cada temporada tiene protagonistas, arco o época distintos.

Cuando pasa: **no alcanza con el póster principal de TMDB**. Cada temporada necesita su propio póster (ver `crear-imagen`, sección de pósters por temporada), y la pieza se arma como carrusel de temporadas.

Si no tenés certeza de si una serie es antológica o continua, **preguntá una sola vez** con tu recomendación — no adivines.

## 4. Chequeos antes de dar el plan por bueno
- **Ignorá la columna "Agregado a la App"** (`agregadoAlaApp`). Es información interna del dueño del catálogo, no una condición para producir contenido: si el título está en el catálogo, se produce. Lo único que define si una pieza está lista o no es lo que dice su `pieza.json`: si ya se creó y si ya se publicó.
- **`estado: "Incompleto"`** + `notas` → faltan temporadas o episodios. La pieza puede hacerse igual, pero el texto no puede prometer lo que falta (ver `crear-texto`).
- **Orden del carrusel**: cronológico por `anio` salvo que el usuario pida otra cosa. La primera imagen es la que más pesa en el feed.
- **Cantidad**: si una colección tiene muchos títulos (10+), preguntá si va todo en un carrusel o se parte en tandas — Instagram tolera hasta 20 imágenes, pero un carrusel de 20 no lo ve nadie completo.

## 5. Entregar el plan
Antes de generar nada, mostrá el plan en el chat, corto y concreto:

```
Plan para "La Purga" (colección de 6 títulos):
  Pieza 1 — carrusel "la-purga" (5 películas, 2013→2021, todas en la app)
     01..05 (una imagen por película) + 06-sinopsis (última) + post.txt
  Pieza 2 — serie "The Purge" (2018): va como pieza propia, aparte
             (serie ≠ carrusel de películas)
```

Pedí confirmación (o al menos dejá el plan visible antes de arrancar) y recién ahí pasá a `crear-imagen` / `crear-carrusel` / `crear-sinopsis` / `crear-texto`.

## 6. Registrar la pieza al terminar
Cuando la pieza queda producida, escribí su ficha en `<contentRoot>/social/<slug>/pieza.json`:

```json
{
  "slug": "la-purga",
  "tipo": "carrusel",
  "titulo": "La Purga",
  "grupo": { "clase": "coleccion", "valor": "La Purga" },
  "vtxIds": ["VTX-1019", "VTX-0740", "VTX-0003", "VTX-0741", "VTX-1027"],
  "creada": "2026-09-02",
  "imagenes": [
    { "archivo": "POST/social/la-purga/images/01-la-noche-de-la-expiacion.png", "tipo": "arte", "vtxId": "VTX-1019" },
    { "archivo": "POST/social/la-purga/images/06-sinopsis-la-purga.png", "tipo": "sinopsis" }
  ],
  "sinopsis": { "creada": true, "archivo": "POST/social/la-purga/images/06-sinopsis-la-purga.png" },
  "texto": { "creado": true, "archivo": "POST/social/la-purga/post.txt" },
  "publicado": { "hecho": false, "fecha": null, "plataformas": [] },
  "nota": "La serie The Purge (VTX-0137) va en su propia pieza: las series no se agrupan con las películas."
}
```

Y regenerá el índice global:
```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/planear-contenido/scripts/estado.py" regenerar
```
`estado-catalogo.json` **no se edita a mano**: se regenera leyendo los `pieza.json` del disco. Si el regenerado reporta `problemas` (archivos declarados que no existen, PNGs que nadie declaró, piezas sin sinopsis), arreglalo antes de dar la tanda por terminada.
