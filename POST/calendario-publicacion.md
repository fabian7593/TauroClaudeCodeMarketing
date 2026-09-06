# Calendario de publicación — Bankai+

## Decisión vigente (desde 2026-09-03)

**4 publicaciones por semana**, en Instagram (@bankaiplus) y Facebook (Taurotv), horario Costa Rica:

| Día | Hora (CR) | Rol |
|---|---|---|
| Martes | 7:00 pm | Entretenimiento — rompe el silencio post-finde |
| Jueves | 7:00 pm | Entretenimiento — siembra qué ver el fin de semana |
| Viernes | 8:00 pm | Empuje más fuerte (producto/CTA) — TGIF, ya deciden el plan de la noche |
| Sábado | 6:00 pm | Cierre de fin de semana — antes de que se decidan por otro plan |

**Por qué esta franja y no mediodía**: el scroll de almuerzo es rápido, "matar el rato" — no es el momento en que alguien decide qué ver. La noche (después de cenar, antes de dormir) es el momento real de intención: es cuando el CTA "¿Querés verla hoy mismo?" convierte mejor. Coincide con la regla ya fijada en `CLAUDE.md` (horario 7-10pm hora Costa Rica).

**Por qué 4 días y no solo viernes/sábado**: publicar únicamente fin de semana deja 5 días de silencio semanal — se pierde el hábito de scroll entre semana.

## Estado de la data al decidir esto

Al momento de fijar este calendario, la cuenta de Zernio tenía solo 7 posts publicados — muestra insuficiente para un "mejor horario" estadístico confiable (la mayoría de franjas en `analytics_get_best_time_to_post` tenían 1 sola publicación). La única señal repetible: miércoles/jueves 6pm ya acumulaban varios posts con engagement consistente, lo que valida la franja nocturna sobre el mediodía.

## Ventana de prueba: 6 semanas

**Del 2026-09-08 al 2026-10-17** (24 publicaciones) + 1 publicación extra el 2026-10-20 (American Horror Story, que no entraba en el conteo por su carrusel de 12 imágenes — ver nota abajo).

**Revisar después del 2026-10-17**: volver a consultar `analytics_get_best_time_to_post` con la muestra ya más grande (~25 posts) y ajustar días/horas con datos reales de esta cuenta en vez de reglas generales. Si el calendario cambia, actualizar este archivo (no crear uno nuevo).

## Selección de piezas para este primer lote

Se tomaron piezas ya producidas (arte + ficha de sinopsis + caption listos en `POST/social/`), en orden de `vtxId` ascendente, saltando:
- Las que ya tenían un post publicado antes de este calendario (detectadas cruzando `posts_list` de Zernio contra los títulos de las piezas: `one-piece`, `genius`, `futurama`, `black-knight`).
- Las que tienen `epoca` distinta de "Cualquier Momento" y no aplican a la fecha actual (reservadas para su temporada — ej. la única pieza con `epoca: Navidad` se guarda para diciembre).

No hubo piezas ya creadas con `epoca: Día del Niño` (el único feriado relevante dentro de esta ventana, 9 de setiembre en Costa Rica) — por eso el lote quedó compuesto enteramente por contenido "Cualquier Momento", como corresponde cuando no hay coincidencia real con el catálogo ya producido.

## Regla nueva: límite de 10 imágenes por carrusel (Instagram y Facebook)

Instagram/Facebook no aceptan más de 10 elementos en un mismo post-carrusel. **American Horror Story** (12 temporadas + 1 ficha = 13 imágenes en su pieza) no entra completo en un solo post:
- Se sacaron 3 temporadas para esa publicación puntual — Roanoke (S6), NYC (S11) y Delicate (S12), las peor recibidas por crítica/audiencia — dejando 9 pósters + la ficha = 10.
- La pieza original en `POST/social/american-horror-story/` **sigue completa con las 12 temporadas** — el recorte es solo para esta publicación en Zernio, no se tocó el archivo.
- Esta regla (contar TODO el post, incluida la ficha, contra el límite de 10, y documentar qué se sacó y por qué) queda escrita en `plugin/post-studio/skills/publicar-contenido/SKILL.md`, sección 5C, punto 5 — aplica a cualquier pieza futura con más de 10 imágenes.

## Cómo se programó

Vía la API de Zernio (MCP), no por navegador — ver `plugin/post-studio/skills/publicar-contenido/SKILL.md` sección 5C. Las imágenes se sirvieron desde `https://raw.githubusercontent.com/fabian7593/TauroClaudeCodeMarketing/main/...` (repo público, imágenes ya versionadas en `POST/social/`). Cada pieza programada tiene su `pieza.json` actualizado con `publicado.programado` (fecha, plataformas, `via: "zernio"`) — `publicado.hecho` se deja en `false` hasta confirmar que salió en vivo.

## Lote extra (relleno de esta semana, 2026-09-03)

Antes de que arrancara el lote de 6 semanas (que empieza el martes 8, primer día "limpio"), se programaron 3 piezas más para llenar lo que quedaba de esta semana, con horario ajustado al mismo patrón (jueves/viernes/sábado):

- 2026-09-03 (jue, 19:00) — Cómo Conocí a Tu Madre
- 2026-09-04 (vie, 20:00) — Dahmer - Monstruo: La Historia de Jeffrey Dahmer
- 2026-09-05 (sáb, 18:00) — Dark

## Piezas programadas en este lote

1. 2026-09-08 (mar) — Le Temes a la Oscuridad?
2. 2026-09-10 (jue) — ¿Quién Es Erin Carter?
3. 2026-09-11 (vie) — La Purga (saga completa)
4. 2026-09-12 (sáb) — 1899
5. 2026-09-15 (mar) — Adolescencia
6. 2026-09-17 (jue) — Ahsoka
7. 2026-09-18 (vie) — Alien: Planeta Tierra
8. 2026-09-19 (sáb) — Amor y Muerte
9. 2026-09-22 (mar) — Andor
10. 2026-09-24 (jue) — Animal Kingdom
11. 2026-09-25 (vie) — Arcane
12. 2026-09-26 (sáb) — Avatar: La Leyenda de Aang
13. 2026-09-29 (mar) — Bandidos de Hoy
14. 2026-10-01 (jue) — Barry
15. 2026-10-02 (vie) — Berlín
16. 2026-10-03 (sáb) — Berlín y la Dama del Armiño
17. 2026-10-06 (mar) — Better Call Saul
18. 2026-10-08 (jue) — Black Mirror
19. 2026-10-09 (vie) — Breaking Bad
20. 2026-10-10 (sáb) — Bruja Escarlata y Visión
21. 2026-10-13 (mar) — Caballero Luna
22. 2026-10-15 (jue) — Chernobyl
23. 2026-10-16 (vie) — Chespirito: Sin Querer Queriendo
24. 2026-10-17 (sáb) — Cobra Kai
25. 2026-10-20 (mar, extra) — American Horror Story (carrusel recortado a 10)

## Incidente 2026-09-04/05: reorganización de carpetas rompió los 53 posts ya programados

El 2026-09-04 se reorganizó `POST/social/` en `social/<categoria>/<slug>/` (series vs. películas). Zernio **no guarda la imagen al programar** — guarda una URL de `raw.githubusercontent.com` y la va a buscar recién al momento de publicar. Al mover los archivos, esa URL quedó apuntando a una ruta que ya no existe → todo lo programado (51 piezas) y lo que le tocó salir en el medio (Dahmer) falló con "Image not found".

`posts_update` de Zernio no permite cambiar la imagen de un post existente, así que no hubo forma de "arreglar" los posts rotos — el usuario los borró todos manualmente y se volvieron a crear desde cero el 2026-09-05, con las URLs ya corregidas a la ruta nueva. Lección permanente: **antes de reorganizar rutas de archivos que Zernio ya tiene programados, hay que asumir que se rompe todo lo pendiente** — no hay forma de parchear en caliente, solo recrear.

## Ronda Halloween 2026-10 (recreación completa, 2026-09-05)

Al recrear el calendario roto, el usuario pidió además: (a) orden random real (ya no alfabético — el bug de origen de esta regla, ver `siguiente_lote_zernio.py`), y (b) tener en cuenta las columnas de `epoca` del catálogo para fechas como Halloween, no solo "Cualquier Momento". Regla nueva, ver `siguiente_lote_zernio.py` regla 5: una época se cubre con contenido **cerca** de la fecha real (no exacta), y acercándose a una época marcada hay que revisar activamente el catálogo con `--incluir-epoca` y **producir piezas nuevas si el volumen ya hecho no alcanza** (el usuario fijó "al menos 5" para Halloween).

Piezas Halloween producidas exclusivamente para esta ronda: **Pesadilla en la Calle del Infierno** (saga completa, 7 películas — VTX-1093/1094/1095/1096/1097/1098/1024, época Halloween) y **El Resplandor** (VTX-0552, época Halloween). Se sumaron a Stranger Things (ya producida, época Halloween), American Horror Story y La Purga (ambas "Cualquier Momento" pero de género terror, ya en el calendario) para llegar a 5, todas ubicadas entre el 22 y el 31 de octubre.

Nota de pósters: 6 de las 7 películas de "Pesadilla en la Calle del Infierno" solo tenían candidato TMDB `es` en la variante de España ("Pesadilla en Elm Street", no coincide con `tituloEs` del catálogo que es la forma LATAM "...Calle del Infierno") — se descartaron todas y se usó inglés, nunca castellano, siguiendo la regla de `crear-imagen` 0.1.

Calendario final random (34 piezas, Dahmer como catch-up inmediato + 33 en fechas mar/jue/vie/sáb hasta el 31-oct): ver `pieza.json` de cada slug (`publicado.programado`) para la fecha exacta asignada — no se repite la tabla acá porque el orden es random y no aporta como referencia futura (a diferencia del primer lote, que sí seguía un criterio fijo de selección).
