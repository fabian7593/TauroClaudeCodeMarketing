---
name: reel-highlights
description: Convierte uno o varios videos existentes de assets/videos/ a formato reel para redes sociales, en tres modos posibles — (1) Highlights: analiza y recorta un solo video a los mejores 15-30s con transiciones y elección de audio, (2) Video completo: mantiene un solo video entero sin cortar ni editar nada, solo le da formato/tamaño vertical de redes y marca de agua, o (3) Fusión de varios videos: combina los mejores momentos de 2+ videos distintos en un único reel corto. Usa ffmpeg. Úsalo cuando el usuario pida "sacame un reel/clip/highlight de este video", "convertime este video en reel", "unime/fusioná estos videos y sacame un reel", o pase uno o más videos pidiendo que se recorten a lo mejor o que se les dé formato de reel tal cual están.
---

# Generador de reels (highlights, video completo, o fusión de varios videos)

## 0. Elegí el modo — SIEMPRE preguntar primero, no asumas
Antes de tocar nada, preguntá con `AskUserQuestion` (salvo que el usuario ya lo haya dejado clarísimo en su pedido, ej. "convertime este video completo a reel, sin cortar nada", o "fusioná estos 3 videos en un reel"). Si el usuario ya pasó/nombró **más de un video**, el modo "Fusión de varios videos" pasa a ser el default implícito — igual confirmá con una pregunta rápida si hay ambigüedad sobre qué querés que salga de ahí (reel corto vs. mantenerlos todos completos uno atrás del otro, esto último no está cubierto por esta skill, avisale al usuario si lo pide).

- **Highlights**: analizás UN video, elegís los mejores momentos, y armás un reel corto de 15-30s con cortes y transiciones. Instrucciones completas en `modo-highlights.md` (pasos H-0 a H-9) — abrilo y seguilo cuando llegues ahí.
- **Video completo**: mantenés UN video entero, de punta a punta, sin sacar frames, sin cortar nada, sin editar el contenido — lo único que hacés es darle el formato/tamaño de redes sociales (vertical 9:16) y ponerle la marca de agua. El audio original se conserva tal cual salvo que el usuario pida explícitamente cambiarlo por otra canción. Instrucciones completas en `modo-video-completo.md` (pasos VC-1 a VC-2).
- **Fusión de varios videos**: el usuario da 2 o más videos de origen. Analizás los mejores momentos de TODOS ellos (no solo de uno) y armás un único reel corto (algunos segundos, 15-30s por default salvo que pida otra duración) combinando los mejores clips sin importar de qué video original venga cada uno — es el mismo proceso que Highlights (usa también `modo-highlights.md`), pero escaneando cada video de origen por separado antes de armar el arco. Este modo NO sirve para pegar los videos completos uno detrás del otro sin cortar — si el usuario quiere eso literal (concatenar videos enteros sin resumir), avisale que esta skill no lo hace tal cual y confirmá si igual quiere que se lo arme como una excepción simple (concat directo, sin escaneo ni arco).

Esta elección define todo el resto del flujo — guardala y no la vuelvas a preguntar dentro de la misma corrida.

## 0.1 Honestidad sobre el método (aplica al modo Highlights)
El modo Highlights es un método **heurístico** guiado por revisión visual de frames (vos, Claude, mirando imágenes), no un modelo de IA entrenado específicamente para detectar "el mejor momento" narrativo (como sí lo hacen CapCut u OpusClip). El criterio principal es **visual**: acción, expresividad, composición, cambios dramáticos de luz/color — el audio es secundario, solo se usa como pista de apoyo cuando el video conserva su propio audio. Si el usuario pide algo mejor que esto, recordale que existen herramientas especializadas gratuitas (CapCut, OpusClip). El modo Video completo no tiene esta limitación porque no analiza ni recorta nada — es una conversión de formato pura.

## 1. Antes de arrancar: entorno
Si no corriste `content-setup` en esta sesión (o `brand.config.json` no existe todavía en la raíz del proyecto), corrélo primero — de ahí sale `contentRoot`, el logo resuelto, y el texto de marca (`website`) que usa el paso 13. Además, confirmá vos mismo acá lo específico de este skill (no lo cubre `content-setup` por defecto):
```bash
ffmpeg -version
ffprobe -version
```
Si falta alguna, avisale al usuario — no instales ffmpeg sin que te lo pida.

## 2. Ubicaciones fijas del proyecto
`contentRoot` sale de `brand.config.json` (default `POST/`).
- **Videos de origen**: `<contentRoot>/assets/videos/` — buscá ahí el/los archivo(s) si el usuario no los especifica, o preguntá cuáles usar si hay ambigüedad. En modo Fusión, todos los videos de origen suelen salir de esta misma carpeta, pero el usuario puede indicarte otra ruta.
- **Audio opcional**: `<contentRoot>/assets/audio/` — pistas de música/sonido que el usuario puede querer usar en vez del audio original.
- **Logo de marca**: el resuelto por `content-setup` (`brand.config.json` → `logoFolder`+`logoFile`). Si el logo es `.svg`, rasterizalo una vez a PNG (por ejemplo con el mismo Chrome headless que usa `post-image`) y cacheá esa versión — ffmpeg no decodifica SVG directo; reusala mientras el SVG original no cambie.
- **Salida**: `<contentRoot>/social/<slug>/reels/<slug>-reel.mp4` — si ya existe un reel previo para ese slug y el usuario pide otra versión, no lo sobrescribas: guardalo como `<slug>-reel-v2.mp4`, `-v3.mp4`, etc. (mirá qué archivos ya hay en esa carpeta antes de nombrar el nuevo). Esto aplica igual en los tres modos. En modo Fusión, si no hay un slug obvio de un solo item/carpeta (porque los videos son de cosas distintas), preguntale al usuario qué nombre de carpeta/slug usar para el resultado.
- **Marca**: el logo + el texto de `brand.config.json` → `website` (con sombra, no caja de fondo — ver paso 13), abajo a la derecha.
- **Scripts de esta skill**: `${CLAUDE_PLUGIN_ROOT}/skills/reel-highlights/scripts/` — usalos para los pasos mecánicos (formato vertical, marca de agua, unir clips con transición, verificar audio) en vez de reescribir los comandos de ffmpeg a mano; ver pasos 12, 13, H-6 y la verificación de audio. Corré cada uno con `bash`, ej. `bash "${CLAUDE_PLUGIN_ROOT}/skills/reel-highlights/scripts/check_audio.sh" archivo.mp4`.

## 2.1 Revisá SIEMPRE si el video de origen trae la marca de otra plataforma/competidor quemada en la imagen
Muchos videos de `<contentRoot>/assets/videos/` pueden ser material de terceros (trailers, clips bajados de otra plataforma, contenido con marca ajena) — es común que traigan un logo pequeño de esa fuente quemado en una esquina (normalmente abajo a la derecha, persistente en casi todos los frames) y/o tarjetas de marca a pantalla completa superpuestas sobre la acción. Si `brand.config.json` tiene `forbiddenMentions` (competidores u otras marcas que el proyecto no quiere mostrar), aplicá esto — y si tenés dudas de si algo cuenta, preguntale al usuario en vez de asumir. Publicar eso tal cual viola esa regla — no alcanza con no mencionarlo en el texto del post, si se VE en el video hay que resolverlo:

1. **Logo pequeño persistente en una esquina**: sacá un frame de muestra, hacé zoom en esa esquina para medir la posición/tamaño exacto (`ffmpeg -vf "crop=W:H:X:Y"`), y tapalo con un blur localizado ANTES de cortar/formatear nada más — no un recorte ni una caja de color sólido (se nota más), un `boxblur` fuerte sobre esa región nada más, superpuesto de vuelta sobre el frame original:
```bash
ffmpeg ... -filter_complex "[0:v]crop=W:H:X:Y,boxblur=25:2[blur];[0:v][blur]overlay=X:Y[out]" -map "[out]" ...
```
Metelo en el mismo filtro que ya uses para cortar cada sub-clip (en modo Highlights/Fusión) o para el paso 12 (en modo Video completo) — no hace falta un paso aparte. Verificá el resultado con un frame antes de seguir: el blur tiene que tapar el logo sin quedar como un parche obvio en escenas claras.
2. **Tarjetas de marca a pantalla completa** (ej. tarjetas de "producido por X", tarjetas de "suscribite"/precio, tarjetas de créditos): estas NO se tapan con blur, se **evitan por completo** al elegir los rangos de corte — no forman parte de ningún clip del reel, ni siquiera de fondo.

⚠️ **Cuidado con los fundidos**: estas tarjetas suelen entrar/salir con un fundido (dissolve), no un corte seco — la tarjeta puede seguir visible, semitransparente, superpuesta sobre la acción, varios frames después de donde "parece" haber terminado en un escaneo cada 0.5s. **Antes de dar por bueno el punto de inicio/fin de un clip que viene justo después de evitar una tarjeta de marca, sacá el frame EXACTO en ese timestamp (no confíes en el frame más cercano del escaneo grueso) y confirmá visualmente que no queda nada de la tarjeta** — si hay dudas, dejá 0.3-0.5s extra de margen después de donde "parece" haber terminado.

## ⚠️ Regla dura de ffmpeg: `-ss` SIEMPRE antes de `-i`
Nunca pongas `-ss`/`-to`/`-t` DESPUÉS de `-i` en un comando que además use un filtro de audio con marcas de tiempo propias (`afade`, etc.) — `-ss` después de `-i` no resetea el reloj interno de los filtros, entonces `afade`'s `st=` sigue refiriéndose a la línea de tiempo del archivo ORIGINAL completo, no del tramo recortado (esto puede dejar el audio final en silencio total aunque el track "exista" en el contenedor, sin ningún error visible). Siempre escribí `ffmpeg -ss START -t DURACION -i "INPUT" ...` (con `-ss` antes de `-i`), nunca al revés, en CUALQUIER corte de audio o video de esta skill — esto aplica también en modo Video completo si el usuario pide reemplazar la canción.

## 2.2 Decodificar rápido — usá el decoder más rápido disponible, no necesariamente la GPU
Antes de procesar un video pesado (resolución alta, o códecs modernos como AV1/HEVC), no uses ciegamente el decoder default de ffmpeg:
1. Revisá el códec del video de origen (`ffprobe`, campo `codec_name` del stream de video).
2. Si es **AV1**, agregá `-c:v libdav1d` antes de `-i` en el comando de ffmpeg (decode explícito, software, multi-thread) — mejora real confirmada frente al decoder default.
3. Para otros códecs pesados, podés probar `ffmpeg -hwaccels` y `ffmpeg -decoders | grep <codec>`, pero **no asumas que GPU = más rápido** cuando el resto del pipeline (blur, overlay, drawtext) corre en CPU — los frames decodificados por GPU igual hay que bajarlos a memoria del sistema para esos filtros, y ese viaje de ida y vuelta puede comerse la ganancia de la GPU. Si tenés dudas, hacé una prueba rápida de 15-20s con `-t 20` comparando antes de aplicarlo al video completo.
4. Para el encode final (`libx264`), `-preset veryfast` en vez de `medium` ya da una mejora notable sin tocar GPU ni perder calidad visible para redes sociales — ya viene aplicado por default en los scripts de la carpeta `scripts/`.

## 3. Metadata del/los video(s)
```bash
ffprobe -v quiet -print_format json -show_format -show_streams "INPUT"
```
Corré esto por cada video de origen (en modo Fusión, uno por uno). Sacá: duración total, resolución, fps, si tiene pista de audio. En modo Highlights/Fusión, si algún video no dura entre 1 y 15 minutos, avisale igual al usuario (no es un bloqueo duro) y seguí. En modo Video completo no hay restricción de duración.

---

# Elegí tu rama según el modo (paso 0)

- **Modo Video completo** → abrí y seguí `modo-video-completo.md` completo, y volvé acá al terminar (VC-2 te manda al paso 12 de abajo).
- **Modo Highlights o Fusión de varios videos** → abrí y seguí `modo-highlights.md` completo, y volvé acá al terminar (H-9 te manda al paso 12 de abajo).

---

# Pasos compartidos (los tres modos terminan acá)

## 12. Formato vertical (Reels/TikTok/Shorts)
Si el video de origen no es ~9:16, usá el script de esta skill (fondo desenfocado en vez de barras negras, consistente con el layout `full_bleed` de `post-image`):
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/reel-highlights/scripts/format_vertical.sh" "raw.mp4" "vertical.mp4"
```
Acepta ancho/alto opcionales como 3er/4to argumento si algún día la salida no es 1080x1920. Si ya es vertical, saltá este paso y usá `raw.mp4` directo en el paso 13. En modo Video completo, si el video de entrada es largo, este paso puede tardar bastante — avisale al usuario que puede tomar un rato.

## 13. Marca de agua (logo arriba, texto de marca abajo, abajo a la derecha)
Usá el script de esta skill — mide el ancho del texto automáticamente (no hace falta recalibrar nada a mano si el sitio/handle de la marca es distinto o cambia de largo) y detecta una fuente bold instalada según el sistema operativo:
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/reel-highlights/scripts/apply_watermark.sh" \
  "vertical.mp4" "<ruta-del-logo-resuelto>" "FINAL.mp4" "<brand.config.json -> website>"
```
El 4to argumento (texto) es obligatorio — sale de `brand.config.json` → `website`, nunca lo hardcodees. Argumentos opcionales (fontsize, ancho de logo, ancho de texto forzado, ruta de fuente forzada) si alguna vez hace falta ajustar la marca — ver comentario dentro del script.

**Después de generar el archivo, sacá un frame y miralo con `Read`** para confirmar que el logo queda arriba del texto (no al costado), que ninguno de los dos toca el borde, y que no se superponen ni quedan cortados — el script no reemplaza esta verificación visual, ajustá los argumentos y volvé a correrlo si hace falta antes de dar el resultado por bueno.

## 14. Verificar antes de entregar
- `ffprobe` sobre `FINAL.mp4`: en modo Highlights/Fusión, confirmá que la duración quedó dentro de lo pedido (15-30s por default, o lo que haya especificado el usuario). En modo Video completo, confirmá que la duración coincide con la del video original.
- Sacá 2-3 frames del resultado final (inicio, medio, cerca del final) y miralos con `Read` — confirmá que el logo + texto de marca se leen bien y no se superponen. En modo Highlights/Fusión, confirmá también que las transiciones no quedaron raras y que el arco (gancho → desarrollo → cierre) se siente coherente, y en Fusión que el salto entre videos de origen distintos no se sienta como un error.
- Si el video de origen tenía marca ajena quemada (ver paso 2.1): sacá el frame exacto del primer y último fotograma del reel final y confirmá que no quede ningún resto de logo o tarjeta de marca ajena.
- Si hay audio (elegido en H-1, o mantenido/reemplazado en VC-1): no podés escuchar el resultado, así que corré el script de verificación sobre el `FINAL.mp4` completo (no solo sobre `audio_final.m4a`):
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/reel-highlights/scripts/check_audio.sh" "FINAL.mp4"
```
Es obligatorio, no opcional. Si devuelve `FAIL`, no entregues: revisá el orden de `-ss`/`-i` antes de continuar.
- Guardá el resultado en `<contentRoot>/social/<slug>/reels/<slug>-reel.mp4` (o `-v2.mp4`/`-v3.mp4` si ya existe una versión previa).

## 15. Entrega
Mostrale al usuario el video final (o la ruta si no se puede adjuntar). Contale en 2-3 líneas qué modo usaste:
- **Highlights**: qué segmento(s) se usaron (con timestamps), qué arco armaste, y qué audio quedó. Recordá la limitación de la sección 0.1 si el usuario pregunta por qué no es "perfecto".
- **Video completo**: que se mantuvo el video entero sin cortes, qué formato/tamaño final tiene, y si el audio quedó igual al original o se reemplazó.
- **Fusión de varios videos**: lo mismo que Highlights, aclarando además de qué video de origen viene cada segmento del arco.

## 16. Limpieza
Borrá archivos temporales (`sheet_*.jpg`, `zoom_*.jpg`, `clip*_video.mp4`, `join_*.mp4`, `audio_final.m4a`, `raw.mp4`, `vertical.mp4`) del scratchpad de la sesión — dejá en el proyecto únicamente el `FINAL.mp4` ya movido a su carpeta definitiva. La carpeta `scripts/` de esta skill NO se toca, es parte de la skill, no del scratch de una corrida.
