# MODO VIDEO COMPLETO

Si el usuario eligió este modo en el paso 0 de `SKILL.md`, seguí esta rama corta y al terminar (VC-2) volvé a `SKILL.md`, sección "Pasos compartidos", paso 12. No hagas escaneo visual, no cortes nada, no arma arco emocional.

## VC-1. Audio — por default se mantiene el original
No preguntes nada de audio salvo que el usuario ya haya pedido explícitamente cambiar la canción (en su pedido inicial, o si contesta que sí cuando se lo confirmás). Si no dijo nada, el audio original del video se conserva tal cual, sin tocarlo.

Si el usuario SÍ pide cambiar la canción:
1. Mostrale los archivos de `<contentRoot>/assets/audio/` y que elija uno (si está vacía, avisale y ofrecé que suba un archivo ahí).
2. La pista elegida tiene que cubrir la duración TOTAL del video (que puede ser mucho más larga que una canción de 3-4 minutos). Si la pista es más corta que el video, hacé loop de la pista con `-stream_loop -1` hasta cubrir la duración total; si es más larga, recortala a la duración exacta del video (con `-ss`/`-t` antes de `-i`, ver regla dura en `SKILL.md`). Aplicá fade in de 0.4s y fade out de 0.6s sobre el resultado final:
```bash
ffmpeg -y -stream_loop -1 -i "AUDIO_ORIGEN" -t DURACION_TOTAL_VIDEO -vn -af "afade=t=in:st=0:d=0.4,afade=t=out:st=DURACION_MENOS_0.6:d=0.6" -c:a aac -b:a 192k "audio_final.m4a"
```
Verificá el resultado antes de combinar:
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/reel-highlights/scripts/check_audio.sh" "audio_final.m4a"
```
3. Combiná con el video (sin re-analizar ni cortar el video, solo reemplazando su pista de audio):
```bash
ffmpeg -i "INPUT" -i "audio_final.m4a" -map 0:v -map 1:a -c:v copy -c:a aac -shortest "raw.mp4"
```
Si NO cambia la canción, `raw.mp4` = el `INPUT` original tal cual (podés usarlo directo en el paso de formato vertical, no hace falta re-encodearlo dos veces — pasale el archivo original directamente al paso 12 de `SKILL.md`).

## VC-2. Seguir a "Pasos compartidos" en SKILL.md
No hay pasos de escaneo, corte, arco ni unión — andá directo al paso 12 de `SKILL.md`, usando como entrada `raw.mp4` (si cambió la canción) o el video original (si no).
