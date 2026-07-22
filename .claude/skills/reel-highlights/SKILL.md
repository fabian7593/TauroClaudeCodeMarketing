---
name: reel-highlights
description: Analiza un video existente (1-15 min) de POST/assets/videos/ y arma un reel corto (15-30s) con los mejores momentos, priorizando lo visual (acción/emoción/suspenso) sobre el audio, con transiciones, fade de audio, marca de agua "taurotv.lat", y una elección explícita de qué audio usar (el del video, uno de POST/assets/audio/, o mudo). Usa ffmpeg. Úsalo cuando el usuario pida "sacame un reel/clip/highlight de este video", o pase un video pidiendo que se recorte a lo mejor.
---

# Generador de reel de highlights — TauroTV

## 0. Honestidad sobre el método (leer antes de prometer nada al usuario)
Esto es un método **heurístico** guiado por revisión visual de frames (vos, Claude, mirando imágenes), no un modelo de IA entrenado específicamente para detectar "el mejor momento" narrativo (como sí lo hacen CapCut u OpusClip). El criterio principal es **visual**: acción, expresividad, composición, cambios dramáticos de luz/color — el audio es secundario, solo se usa como pista de apoyo cuando el video conserva su propio audio. Si el usuario pide algo mejor que esto, recordale que existen herramientas especializadas gratuitas (CapCut, OpusClip).

## 1. Ubicaciones fijas del proyecto
- **Videos de origen**: `POST/assets/videos/` — buscá ahí el archivo si el usuario no lo especifica, o preguntá si hay más de uno.
- **Audio opcional**: `POST/assets/audio/` — pistas de música/sonido que el usuario puede querer usar en vez del audio original.
- **Logo de marca**: `POST/assets/logo/TauroTV_Logo_trimmed.png` (mismo logo recortado que usa el sistema de imágenes).
- **Salida**: `POST/social/<slug>/reels/<slug>-reel.mp4` — si ya existe un reel previo para ese slug y el usuario pide otra versión, no lo sobrescribas: guardalo como `<slug>-reel-v2.mp4`, `-v3.mp4`, etc. (mirá qué archivos ya hay en esa carpeta antes de nombrar el nuevo).
- **Marca**: el ícono del logo + el texto "taurotv.lat" (con sombra, no caja de fondo — ver paso 13), abajo a la derecha.

## ⚠️ Regla dura de ffmpeg: `-ss` SIEMPRE antes de `-i`
Nunca pongas `-ss`/`-to`/`-t` DESPUÉS de `-i` en un comando que además use un filtro de audio con marcas de tiempo propias (`afade`, etc.) — un bug real de esta skill: `-ss` después de `-i` no resetea el reloj interno de los filtros, entonces `afade`'s `st=` sigue refiriéndose a la línea de tiempo del archivo ORIGINAL completo, no del tramo recortado. Resultado real que pasó: un `afade=t=out:st=14.4` diseñado para el final de un recorte de 15s en realidad se aplicó al segundo 14.4 del archivo ORIGINAL (mucho antes del tramo elegido), dejando el audio final en silencio total aunque el track "existía" en el contenedor. Siempre escribí `ffmpeg -ss START -t DURACION -i "INPUT" ...` (con `-ss` antes de `-i`), nunca al revés, en CUALQUIER corte de audio o video de esta skill.

## 2. Verificar herramientas
```bash
ffmpeg -version
ffprobe -version
```
Si falta alguna, avisale al usuario — no instales ffmpeg sin que te lo pida.

## 3. Preguntá SIEMPRE qué audio usar (nunca asumas)
Antes de tocar nada, preguntá con `AskUserQuestion` (siempre, en cada corrida — no reutilices una respuesta de una corrida anterior salvo que el usuario diga "igual que la vez pasada"):

- **Audio del video original**: se conserva y se recorta junto con la imagen.
- **Audio de `POST/assets/audio/`**: le mostrás la lista de archivos de esa carpeta y elige uno (si está vacía, avisale y ofrecé que suba un archivo ahí, o que elija otra opción).
- **Mudo**: el video final sale sin audio, para que el usuario le ponga música/voz después él mismo (edición manual).

Esta elección define qué pasa en el paso 9 (armado de audio) — guardala, no la vuelvas a preguntar dentro de la misma corrida.

## 4. Metadata del video
```bash
ffprobe -v quiet -print_format json -show_format -show_streams "INPUT"
```
Sacá: duración total, resolución, fps, si tiene pista de audio. Si la duración no está entre 1 y 15 minutos, avisale igual al usuario (no es un bloqueo duro) y seguí.

## 5. Escaneo visual grueso (contact sheets, no frame por frame)
Para cubrir todo el video sin gastar una llamada de `Read` por cada segundo, armá **hojas de contacto** (grillas de miniaturas) con ffmpeg en vez de mirar frame por frame:

```bash
ffmpeg -i "INPUT" -vf "fps=1/N,scale=320:-1,tile=6x6" -frames:v N_GRID "sheet_%02d.jpg"
```
`N` = intervalo en segundos entre miniaturas, elegido para que el total de miniaturas ronde 60-100 (ej. video de 5 min → N≈5s → 60 miniaturas → ~2 hojas de 6x6; video de 15 min → N≈15s).

Mirá cada hoja con `Read`. Marcá qué celdas (= qué rango de tiempo aproximado) se ven visualmente interesantes: acción, movimiento, expresiones faciales claras, composición dramática, cambios de luz/color, momentos de tensión o sorpresa. Descartá tramos estáticos, pantallas negras, créditos, planos fijos sin nada pasando.

## 6. Escaneo visual fino (sobre las zonas candidatas)
Para cada zona prometedora del paso 5 (elegí entre 4 y 8 candidatas), sacá una grilla más densa solo de esa ventana (~15-20s) para ubicar el corte exacto:
```bash
ffmpeg -ss ZONA_INICIO -i "INPUT" -t 20 -vf "fps=1,scale=320:-1,tile=5x4" -frames:v 1 "zoom_NN.jpg"
```
Mirá cada una y anotá el timestamp preciso de inicio/fin más fuerte dentro de esa zona (no hace falta usar los 15-20s completos, solo la mejor sub-ventana de esa zona).

## 7. Armar el arco emocional del reel
El objetivo no es solo "mostrar buenos momentos" — es que **den ganas de ver hasta el final**. Ordená los mejores 2-4 candidatos del paso 6 pensando en un arco:
1. **Gancho** (primeros 2-4s): el plano más llamativo o intrigante que tengas — lo que para el scroll.
2. **Desarrollo/acción**: 1-2 momentos de movimiento, tensión o emoción creciente.
3. **Clímax o cierre fuerte**: el momento más impactante, al final — para que la última impresión sea la más fuerte, no la más floja.

El total final tiene que quedar entre **15 y 30 segundos** — ajustá la duración de cada sub-clip para caer en ese rango (podés usar un solo clip continuo si un tramo natural ya tiene ese arco dentro de 15-30s, pero lo más común va a ser una compilación de sub-clips).

## 8. Cortar los sub-clips
```bash
ffmpeg -ss START -to END -i "INPUT" -c:v libx264 -crf 20 -preset medium -an "clipNN_video.mp4"
```
(`-ss` antes de `-i` — ver regla dura arriba.)
Cortá el video **sin audio acá** (`-an`) — el audio se arma aparte en el paso 9 según lo que eligió el usuario en el paso 3, para no arrastrar el audio original si no corresponde.

## 9. Unir con transiciones (video) según el arco
Unir los sub-clips con un corte seco es válido para contenido rápido/acción, pero por default usá una transición corta tipo *crossfade* entre sub-clips para que se sienta más fluido y emocional (no aplica si es un solo clip continuo):
```bash
ffmpeg -i clip01_video.mp4 -i clip02_video.mp4 -filter_complex \
"[0:v][1:v]xfade=transition=fade:duration=0.35:offset=DUR1_MENOS_0.35[v01]" \
-map "[v01]" -c:v libx264 -crf 20 -preset medium "join_01.mp4"
```
Encadená `xfade` de a pares para 3+ clips (la salida de un `xfade` es la entrada del siguiente). Si el contenido es muy rápido/acción y una transición se siente floja, usá `transition=fade` con `duration=0.15-0.2` (casi un corte seco con un respiro mínimo) en vez de sacar la transición del todo — mantiene consistencia visual en todos los reels.

Resultado de este paso: `video_sin_audio.mp4` (con o sin transiciones, según haya 1 o varios sub-clips).

## 10. Armar el audio (según lo elegido en el paso 3)
- **Audio del video original**: extraé el audio de los mismos rangos (`START`/`END` de cada sub-clip) del video original, unílo con concat (mismo orden que los sub-clips de video), y aplicá fade.
- **Audio de `POST/assets/audio/<archivo>`**: recortá esa pista a la duración total del reel (si es más larga, elegí el tramo que mejor acompañe el arco — ej. que un swell/subida de energía caiga cerca del clímax del paso 7). Para encontrar ese tramo, escaneá el volumen en ventanas de ~15s a lo largo de todo el archivo (`ffmpeg -ss T -t 15 -i AUDIO -af volumedetect -f null -` por cada `T`) y elegí la ventana con `max_volume` más alto.
- **Mudo**: saltá este paso entero, no hay pista de audio.

En cualquiera de los dos primeros casos, el corte + fade se hace **en un solo comando, con `-ss`/`-t` antes de `-i`** (ver regla dura arriba — nunca después):
```bash
ffmpeg -ss START -t DURACION_TOTAL -i "AUDIO_ORIGEN" -vn -af "afade=t=in:st=0:d=0.4,afade=t=out:st=DURACION_TOTAL_MENOS_0.6:d=0.6" -c:a aac -b:a 192k "audio_final.m4a"
```
`-vn` es necesario si la fuente de audio tiene una carátula/imagen embebida (mp3 con cover art) — si no, ffmpeg puede fallar tratando de mezclar esa imagen como si fuera video de salida.

**Verificación obligatoria antes de seguir** (esto detecta el bug de la regla dura si volviera a pasar):
```bash
ffmpeg -i "audio_final.m4a" -af volumedetect -f null - 2>&1 | grep -E "mean_volume|max_volume"
```
Si `mean_volume` da por debajo de ~-50dB, el audio quedó silencioso — no sigas, revisá el orden de `-ss`/`-i` antes de continuar.

## 11. Combinar video + audio
```bash
ffmpeg -i video_sin_audio.mp4 -i audio_final.m4a -c:v copy -c:a aac -shortest "raw.mp4"
```
Si es mudo, `raw.mp4` = el `video_sin_audio.mp4` del paso 9, tal cual (sin pista de audio en el archivo final — no le agregues silencio artificial).

## 12. Formato vertical (Reels/TikTok/Shorts)
Si el video de origen no es ~9:16, aplicá la misma técnica de fondo desenfocado que usa `post-template.html` en el layout `full_bleed` (consistencia de marca — se ve todo, sin recortar el sujeto, relleno con una copia borrosa en vez de barras negras):
```bash
ffmpeg -i "raw.mp4" -filter_complex "\
[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=30,eq=brightness=-0.12[bg];\
[0:v]scale=1080:1920:force_original_aspect_ratio=decrease[fg];\
[bg][fg]overlay=(W-w)/2:(H-h)/2[vout]" \
-map "[vout]" -map 0:a? -c:v libx264 -crf 20 -preset medium -c:a aac "vertical.mp4"
```
Si ya es vertical, saltá este paso y usá `raw.mp4` directo en el paso 13.

## 13. Marca de agua (logo + "taurotv.lat", abajo a la derecha)
Logo real (ícono) + texto con **sombra** (no caja de fondo semitransparente — se lee mejor sobre contenido variado). Diseño: ícono a la izquierda, texto a la derecha, ambos anclados al mismo margen inferior/derecho:
```bash
ffmpeg -i "vertical.mp4" -i "POST/assets/logo/TauroTV_Logo_trimmed.png" -filter_complex "\
[1:v]scale=58:-1[logo]; \
[0:v][logo]overlay=W-230:H-100[withlogo]; \
[withlogo]drawtext=fontfile='C\:/Windows/Fonts/arialbd.ttf':text='taurotv.lat':fontsize=38:fontcolor=white:shadowcolor=black@0.85:shadowx=2:shadowy=2:x=W-165:y=H-78" \
-c:v libx264 -crf 20 -preset medium -c:a copy "FINAL.mp4"
```
Nota Windows: en `fontfile`, los dos puntos de la ruta (`C:`) van escapados como `C\:`. Las coordenadas (`W-230`, `W-165`, etc.) están calibradas para 1080x1920 — si el video final tiene otra resolución, escalalas proporcionalmente. **Después de generar el archivo, sacá un frame y miralo con `Read`** para confirmar que el logo y el texto no se superponen ni quedan cortados — ajustá las coordenadas y volvé a correr este paso si hace falta, antes de dar el resultado por bueno.

## 14. Verificar antes de entregar
- `ffprobe` sobre `FINAL.mp4`: confirmá que la duración quedó dentro de lo pedido (15-30s por default, o lo que haya especificado el usuario).
- Sacá 2-3 frames del resultado final (de distintos puntos: inicio, medio, cerca del final) y miralos con `Read` — confirmá que el logo + texto de marca se leen bien y no se superponen, que las transiciones no quedaron raras, y que el arco (gancho → desarrollo → cierre) se siente coherente.
- Si eligió audio (original o de assets): no podés escuchar el resultado, así que **corré `volumedetect` sobre el `FINAL.mp4`** (no solo sobre `audio_final.m4a` — verificá el archivo final entero, después de todos los pasos de combinación) y confirmá que `mean_volume` no está por debajo de ~-50dB. Esto es obligatorio, no opcional — es la única forma de detectar un audio silencioso sin poder oírlo.
- Guardá el resultado en `POST/social/<slug>/reels/<slug>-reel.mp4` (o `-v2.mp4`/`-v3.mp4` si ya existe una versión previa — ver paso 1).

## 15. Entrega
Mostrale al usuario el video final (o la ruta si no se puede adjuntar). Contale en 2-3 líneas: qué segmento(s) se usaron (con timestamps), qué arco armaste (gancho/desarrollo/cierre), y qué audio quedó (original/pista de assets/mudo). Recordá la limitación de la sección 0 si el usuario pregunta por qué no es "perfecto".

## 16. Limpieza
Borrá archivos temporales (`sheet_*.jpg`, `zoom_*.jpg`, `clip*_video.mp4`, `join_*.mp4`, `audio_final.m4a`, `raw.mp4`, `vertical.mp4`) del scratchpad — dejá en el proyecto únicamente el `FINAL.mp4` ya movido a su carpeta definitiva.
