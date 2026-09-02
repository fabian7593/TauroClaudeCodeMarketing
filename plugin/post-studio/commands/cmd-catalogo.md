---
description: Sincronizar el catálogo maestro al espejo local y consultar qué hay / qué falta
---

Trabajá con el catálogo del proyecto: $ARGUMENTS

Usá el skill `sincronizar-catalogo`.

- **Sin argumentos, o "sincronizá" / "actualizá"**: regenerá el espejo local desde la hoja fuente. Preferí siempre el Excel local (`fuente.archivoLocal` de `catalogo.config.json`); si no está, usá el conector de Drive como respaldo y decile al usuario que dejando el `.xlsx` en el proyecto sale mucho más barato y confiable. Al terminar, informá cuántos títulos y colecciones quedaron, y si hubo `avisos` (columnas nuevas sin mapear).
- **Con un título o colección** (ej. `/cmd-catalogo digimon`): consultá el espejo (`buscar`, `coleccion`, `grupo`) y mostrá qué hay, a qué colección pertenece y qué contenido ya está producido (`estado.py estado`). No generes contenido acá — para eso está `/cmd-contenido`.
- **"qué falta" / "pendientes"**: mostrá el resumen de producción (`estado.py resumen`) y una tanda de títulos sin contenido, priorizando los que ya están en la app (`pendientes --solo-en-app`).

Si el espejo no existe todavía, sincronizalo primero sin preguntar.
