---
name: sincronizar-catalogo
description: Baja el catálogo maestro del proyecto (una hoja de cálculo con los títulos/productos y sus datos) a un espejo local JSON, y lo consulta sin cargarlo entero en contexto. Úsalo cuando haya que actualizar el catálogo, buscar un título/colección, o cuando otro skill necesite datos del catálogo (colección a la que pertenece, temporadas, TMDB, calificación, clasificación por edad).
---

# sincronizar-catalogo — espejo local del catálogo maestro

El catálogo del proyecto vive en una hoja de cálculo (Excel/Sheets) que cambia seguido. Este skill lo baja a un **espejo local JSON** y expone consultas puntuales, para que ningún otro skill tenga que leer miles de filas dentro del contexto.

Dos archivos, dos responsabilidades — no los mezcles:
- **`<contentRoot>/catalogo.json`** — qué existe en el catálogo (datos). Generado, no se edita a mano.
- **`<contentRoot>/estado-catalogo.json`** — qué contenido ya se produjo (estado). Lo maneja `planear-contenido` con su script `estado.py`.

## 0. Configuración del proyecto
Todo lo específico del catálogo (ruta del archivo, hoja, nombres de columnas) vive en **`catalogo.config.json`** en la raíz del proyecto. El plugin no sabe nada de ese Excel: si el catálogo cambia de columnas, se ajusta ese archivo, nunca los scripts.

Si `catalogo.config.json` no existe, creálo mirando la hoja real (una vez): qué hoja usar, y el mapa `encabezado del Excel → campo del espejo`.

## 1. De dónde se lee (en orden de preferencia)

### Vía A — Excel local (la que hay que usar siempre que se pueda)
El usuario deja el archivo en la ruta de `fuente.archivoLocal` (por default, la raíz del proyecto).

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/sincronizar-catalogo/scripts/parse_catalogo.py" \
  --config catalogo.config.json --xlsx VORTEX_Catalogo_Master.xlsx
```

Por qué es la vía buena: lee celdas reales con `openpyxl`, mapea por **nombre** de columna (aguanta que agreguen o muevan columnas), y **no pasa una sola celda por el contexto del modelo**. Cuesta prácticamente cero.

### Vía B — conector de Drive (respaldo)
Solo si no hay copia local del Excel. Leé el archivo de Drive con el conector; cuando la respuesta es grande, la herramienta la guarda en un `.txt` — pasá ese archivo:

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/sincronizar-catalogo/scripts/parse_catalogo.py" \
  --config catalogo.config.json --dump <ruta-del-volcado>.txt
```

Esta vía mapea por **posición** de columna (el volcado no trae encabezados usables), así que si el Excel cambió de estructura hay que actualizar `columnas` en el config. Es más frágil y más cara: preferí siempre la vía A.

**Cuándo re-sincronizar**: cada vez que el usuario diga que actualizó el catálogo, y antes de planear una tanda grande de contenido. No hace falta re-sincronizar para cada post.

## 2. Consultar sin quemar contexto
Nunca leas `catalogo.json` entero (son miles de títulos). Usá el script de consulta:

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/sincronizar-catalogo/scripts/consultar_catalogo.py" <comando>
```

| Comando | Para qué |
|---|---|
| `ver <VTX-id o texto>` | Ficha de un título |
| `buscar <texto> [--limite N]` | Buscar por título en español/inglés o colección |
| `coleccion <nombre>` | Todos los títulos de una colección, ordenados por año |
| `colecciones [--min N]` | Ranking de colecciones por cantidad de títulos |
| `grupo <VTX-id o texto>` | **El comando clave**: el título + toda su colección, ya separada en `series` y `peliculas` |
| `pendientes` | Títulos que el Excel todavía no marca como publicados — es solo una pista del Excel. **El estado real de producción lo da `estado.py`** (qué pieza está creada y cuál publicada), no esta columna |

`grupo` es el que usa `planear-contenido` antes de decidir qué piezas armar.

## 3. Campos del espejo
Cada título trae: `vtxId`, `categoria`, `tipo` (Serie/Película), `tituloEs`, `tituloEn`, `anio`, `temporadas`, `episodios`, `duracionMin`, `generos[]`, `calificacion`, `clasificacion`, `estado` (Completo/Incompleto), `audioDual`, `tercerAudio`, `tmdbId`, `tmdbUrl`, `posterUrl`, `notas`, `agregadoAlaApp`, `anadidoARedes`, `coleccion`, `epoca`, `esAnime`.

Dos cosas a tener presentes al usar estos datos:
- **`agregadoAlaApp`** → dato informativo del dueño del catálogo. **No condiciona la producción de contenido**: si el título está en el catálogo, se puede producir. Lo que define el estado real de una pieza es su `pieza.json` (creada / publicada).
- **`estado: "Incompleto"`** + `notas` → faltan temporadas/episodios. Nunca prometas en el post lo que falta (ej. si falta la temporada 4, no digas "todas las temporadas").
- Las columnas de logística interna (dónde está guardado, de qué plataforma salió) **no se copian** al espejo: son ruido y arrastran nombres de plataformas competidoras que por regla de marca no pueden aparecer en un post.

## 4. Al terminar
Decí cuántos títulos y colecciones quedaron sincronizados y desde qué vía, y avisá si el script reportó `avisos` (columnas nuevas del Excel que nadie mapeó todavía — ahí hay que actualizar `catalogo.config.json`).
