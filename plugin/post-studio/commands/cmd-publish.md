---
description: Publicar o programar en redes sociales un contenido ya generado
---

Publicá o programá en redes sociales: $ARGUMENTS

Usá el skill `publicar-contenido`. Si `$ARGUMENTS` pide un lote/calendario (varias piezas, "los próximos N posts", "seguí el calendario") en vez de una sola pieza puntual, andá directo a la sección 5C de esa skill (Zernio vía API/MCP, sin navegador) — empezando por `scripts/siguiente_lote_zernio.py` para elegir qué piezas. Si `$ARGUMENTS` está vacío o no deja claro qué publicar, listá las subcarpetas de `<contentRoot>/social/series/` y `<contentRoot>/social/peliculas/` (o corré el script de arriba) y preguntame — no asumas. Seguí el orden de caminos de esa skill (API/MCP primero, navegador de respaldo) y no publiques sin pasar la verificación de marca del paso 6.
