# MODO HIGHLIGHTS (uno o varios videos de origen)

Si el usuario eligió Highlights o Fusión de varios videos en el paso 0 de `SKILL.md`, seguí todos estos pasos en orden. Son el mismo flujo — la única diferencia es cuántos archivos de origen tenés. Al terminar (H-9), volvé a `SKILL.md`, sección "Pasos compartidos", paso 12.

## H-0. Confirmá la lista de videos de origen (solo relevante si son 2+)
Si es Fusión, listá explícitamente los archivos que vas a usar (nombre + duración de cada uno, sacada con `ffprobe`) y confirmá con el usuario que son los correctos antes de escanear nada — es fácil confundir cuál es cuál si los nombres son parecidos. Asigná una letra o número corto a cada video (ej. `A = video1.mp4`, `B = video2.mp4`) para referenciarlos sin ambigüedad en el resto del proceso.

## H-1. Preguntá SIEMPRE qué audio usar (nunca asumas)
Antes de tocar nada, preguntá con `AskUserQuestion` (siempre, en cada corrida — no reutilices una respuesta de una corrida anterior salvo que el usuario diga "igual que la vez pasada"):

- **Audio del/los video(s) original(es)**: se conserva y se recorta junto con la imagen. Si hay más de un video de origen (Fusión), cada clip lleva el audio de SU PROPIO video de origen (no se mezclan audios de videos distintos) — avisale al usuario que el resultado puede sonar entrecortado entre clips de fuentes distintas si sus audios son muy diferentes en tono/volumen, y ofrecé silenciar u otra pista si prefiere algo más consistente.
- **Audio de `<contentRoot>/assets/audio/`**: le mostrás la lista de archivos de esa carpeta y elige uno (si está vacía, avisale y ofrecé que suba un archivo ahí, o que elija otra opción). Recomendado por default cuando hay Fusión de varios videos, para que el resultado suene unificado en vez de saltar entre audios distintos.
- **Mudo**: el video final sale sin audio, para que el usuario le ponga música/voz después él mismo (edición manual).

Esta elección define qué pasa en el paso H-7 (armado de audio) — guardala, no la vuelvas a preguntar dentro de la misma corrida.

## H-2. Escaneo visual grueso (contact sheets, no frame por frame)
Para cubrir todo el video sin gastar una llamada de `Read` por cada segundo, armá **hojas de contacto** (grillas de miniaturas) con ffmpeg en vez de mirar frame por frame. **Si hay más de un video de origen (Fusión), repetí este paso completo para CADA uno por separado** (nombrá las hojas con el identificador del video, ej. `sheet_A_01.jpg`, `sheet_B_01.jpg`, para no confundir de cuál video salió cada miniatura):

```bash
ffmpeg -i "INPUT" -vf "fps=1/N,scale=320:-1,tile=6x6" -frames:v N_GRID "sheet_%02d.jpg"
```
`N` = intervalo en segundos entre miniaturas, elegido para que el total de miniaturas ronde 60-100 (ej. video de 5 min → N≈5s → 60 miniaturas → ~2 hojas de 6x6; video de 15 min → N≈15s).

Mirá cada hoja con `Read`. Marcá qué celdas (= qué rango de tiempo aproximado, y de qué video de origen si hay varios) se ven visualmente interesantes: acción, movimiento, expresiones faciales claras, composición dramática, cambios de luz/color, momentos de tensión o sorpresa. Descartá tramos estáticos, pantallas negras, créditos, planos fijos sin nada pasando.

## H-3. Escaneo visual fino (sobre las zonas candidatas)
Para cada zona prometedora del paso H-2 (elegí entre 4 y 8 candidatas **en total, sumando todos los videos de origen si hay varios** — no 4-8 por cada video, salvo que el usuario pida un reel más largo), sacá una grilla más densa solo de esa ventana (~15-20s) del video correspondiente para ubicar el corte exacto:
```bash
ffmpeg -ss ZONA_INICIO -i "INPUT_CORRESPONDIENTE" -t 20 -vf "fps=1,scale=320:-1,tile=5x4" -frames:v 1 "zoom_NN.jpg"
```
Mirá cada una y anotá el timestamp preciso de inicio/fin más fuerte dentro de esa zona (no hace falta usar los 15-20s completos, solo la mejor sub-ventana de esa zona), **junto con de qué video de origen viene** si hay varios. Si dos tomas distintas quedan muy cerca en el tiempo, hacé un escaneo todavía más fino (fps=4-5) antes de fijar el corte — a esta resolución (0.5s) es fácil mezclar sin querer el final de una toma con el principio de otra completamente distinta.

## H-4. Armar el arco emocional del reel
El objetivo no es solo "mostrar buenos momentos" — es que **den ganas de ver hasta el final**. Ordená los mejores 2-4 candidatos del paso H-3 pensando en un arco (si hay varios videos de origen, los candidatos se mezclan libremente por calidad visual, sin importar de cuál video vienen — no hace falta "repartir" tiempo equitativo entre videos salvo que el usuario lo pida):
1. **Gancho** (primeros 2-4s): el plano más llamativo o intrigante que tengas — lo que para el scroll.
2. **Desarrollo/acción**: 1-2 momentos de movimiento, tensión o emoción creciente.
3. **Clímax o cierre fuerte**: el momento más impactante, al final — para que la última impresión sea la más fuerte, no la más floja.

El total final tiene que quedar entre **15 y 30 segundos** — ajustá la duración de cada sub-clip para caer en ese rango (podés usar un solo clip continuo si un tramo natural ya tiene ese arco dentro de 15-30s, pero lo más común va a ser una compilación de sub-clips). Si una toma es muy corta pero muy fuerte visualmente (menos de 1s), considerá aplicarle cámara lenta (`setpts=N*PTS` sobre el video, más `fps=30` después para normalizar el frame rate — ver nota técnica en el paso H-5) en vez de descartarla.

## H-5. Cortar los sub-clips
```bash
ffmpeg -ss START -to END -i "INPUT_CORRESPONDIENTE" -c:v libx264 -crf 20 -preset medium -an "clipNN_video.mp4"
```
(`-ss` antes de `-i` — ver regla dura en `SKILL.md`.) Si hay varios videos de origen, `INPUT_CORRESPONDIENTE` es el archivo específico del que sale ESE clip (el que anotaste en H-3) — nunca asumas que todos los clips salen del mismo archivo.
Cortá el video **sin audio acá** (`-an`) — el audio se arma aparte en el paso H-7 según lo que eligió el usuario en el paso H-1, para no arrastrar el audio original si no corresponde.

**Cámara lenta (opcional, para tomas cortas pero impactantes)**: agregá `-vf "setpts=N*PTS,fps=30"` (con N > 1 para ralentizar, ej. `setpts=2.0*PTS` = mitad de velocidad). El `fps=30` después de `setpts` es obligatorio, no cosmético — `setpts` reduce el frame rate real del clip (ej. a 15fps con `2.0*PTS`), y si después lo unís con `xfade` a otro clip a 30fps, ffmpeg tira error de "frame rate do not match" y falla toda la unión.

## H-6. Unir con transiciones (video) según el arco
Unir los sub-clips con un corte seco es válido para contenido rápido/acción, pero por default usá una transición corta tipo *crossfade* entre sub-clips para que se sienta más fluido y emocional (no aplica si es un solo clip continuo).

Usá el script de esta skill en vez de armar el `filter_complex` a mano — calcula los offsets acumulados automáticamente a partir de la duración real de cada clip (`ffprobe`), evitando el error de aritmética manual:
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/reel-highlights/scripts/join_xfade.sh" 0.35 "video_sin_audio.mp4" "clip01_video.mp4" "clip02_video.mp4" "clip03_video.mp4"
```
El primer argumento es la duración de la transición en segundos — por default `0.35`, pero si el contenido es muy rápido/acción y una transición de 0.35 se siente floja, usá `0.15`-`0.2` (casi un corte seco con un respiro mínimo) en vez de sacar la transición del todo, para mantener consistencia visual en todos los reels. El resto de los argumentos son los clips en orden. Si solo tenés 1 sub-clip, no uses este script — usalo directo como `video_sin_audio.mp4`.

Resultado de este paso: `video_sin_audio.mp4`.

## H-7. Armar el audio (según lo elegido en el paso H-1)
- **Audio del/los video(s) original(es)**: extraé el audio de los mismos rangos (`START`/`END` de cada sub-clip) de CADA video de origen correspondiente (no siempre el mismo archivo si hay Fusión — usá el mismo `INPUT_CORRESPONDIENTE` que usaste para cortar ese clip en H-5), unílo con concat (mismo orden que los sub-clips de video), y aplicá fade.
- **Audio de `<contentRoot>/assets/audio/<archivo>`**: recortá esa pista a la duración total del reel (si es más larga, elegí el tramo que mejor acompañe el arco — ej. que un swell/subida de energía caiga cerca del clímax del paso H-4). Para encontrar ese tramo, escaneá el volumen en ventanas de ~15s a lo largo de todo el archivo (`ffmpeg -ss T -t 15 -i AUDIO -af volumedetect -f null -` por cada `T`) y elegí la ventana con `max_volume`/`mean_volume` más alto y que además tenga una progresión ascendente hacia ese punto (que se sienta como un build-up, no un volumen plano).
- **Mudo**: saltá este paso entero, no hay pista de audio.

En cualquiera de los dos primeros casos, el corte + fade se hace **en un solo comando, con `-ss`/`-t` antes de `-i`** (ver regla dura en `SKILL.md` — nunca después):
```bash
ffmpeg -ss START -t DURACION_TOTAL -i "AUDIO_ORIGEN" -vn -af "afade=t=in:st=0:d=0.4,afade=t=out:st=DURACION_TOTAL_MENOS_0.6:d=0.6" -c:a aac -b:a 192k "audio_final.m4a"
```
`-vn` es necesario si la fuente de audio tiene una carátula/imagen embebida (mp3 con cover art) — si no, ffmpeg puede fallar tratando de mezclar esa imagen como si fuera video de salida.

**Verificación recomendada antes de seguir** (detecta temprano el bug de la regla dura si volviera a pasar, en vez de recién en el paso 14 sobre el archivo final):
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/reel-highlights/scripts/check_audio.sh" "audio_final.m4a"
```
Si da `FAIL`, no sigas: revisá el orden de `-ss`/`-i` antes de continuar.

## H-8. Combinar video + audio
```bash
ffmpeg -i video_sin_audio.mp4 -i audio_final.m4a -c:v copy -c:a aac -shortest "raw.mp4"
```
Si es mudo, `raw.mp4` = el `video_sin_audio.mp4` del paso H-6, tal cual (sin pista de audio en el archivo final — no le agregues silencio artificial).

## H-9. Seguir a "Pasos compartidos" en SKILL.md
Usá `raw.mp4` como entrada del paso 12 de `SKILL.md`.
