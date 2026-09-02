---
description: Producir el contenido completo de un título del catálogo (plan + imágenes + ficha de sinopsis + texto)
---

Producí el contenido para: $ARGUMENTS

Este es el comando principal cuando el pedido nace del catálogo. Hace la pieza **completa**, no una imagen suelta.

## Orden de trabajo (no lo saltees)
1. **`planear-contenido`** — traé el título y **toda su colección**, y decidí qué piezas hay que armar (imagen individual / carrusel de películas / carrusel de temporadas / serie por un lado y películas por otro). Mostrame el plan antes de generar nada. Si el título pertenece a una saga, la pieza es la saga: no produzcas un título suelto de una colección.
2. **Pósters** — bajá un póster distinto por slide con `tmdb_posters.py`, respetando la regla de idioma (español; si TMDB no tiene, el póster default del catálogo, avisándolo) y usando pósters por temporada cuando la pieza es un carrusel de temporadas.
3. **`crear-imagen`** (o `crear-carrusel` si son varias) — el arte de cada título/temporada.
4. **`crear-sinopsis`** — la ficha con el texto explicativo. **Siempre**, sea imagen individual o carrusel. Va **última**, numerada después del último arte.
5. **`crear-texto`** — el caption + hashtags, con título, gancho, invitación a sumarse a la plataforma, y los datos reales del catálogo (edad, puntaje, temporadas). El texto largo va en la ficha, no repetido acá.
6. **Registrar** — escribí el `pieza.json` de la pieza y regenerá el índice con `estado.py regenerar`.

## Qué preguntarme
Solo lo que no se pueda deducir: si una serie es antológica o de historia continua cuando no está claro, si una colección grande va entera o en tandas, y si querés un orden distinto al cronológico. Todo lo demás (layout, formato, filas de audio) sale de las reglas del proyecto y del catálogo.

## Antes de darlo por terminado
Avisame explícitamente si: algún título está **incompleto** en el catálogo, o algún póster **no se consiguió en español**. (La columna "Agregado a la App" es informativa mía: no la uses para decidir nada.)
