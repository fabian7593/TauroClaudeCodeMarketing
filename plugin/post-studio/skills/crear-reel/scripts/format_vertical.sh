#!/usr/bin/env bash
# Convierte un video a formato vertical 9:16 con fondo desenfocado (sin recortar el sujeto).
# Misma técnica que usa post-template.html en el layout full_bleed (consistencia visual).
#
# Uso: format_vertical.sh INPUT OUTPUT [ANCHO] [ALTO]
#   INPUT   - video de origen (puede ser cualquier aspect ratio)
#   OUTPUT  - archivo de salida
#   ANCHO   - opcional, default 1080
#   ALTO    - opcional, default 1920
#
# Si el video de entrada ya es ~9:16, no hace falta correr este script.

set -e

INPUT="$1"
OUTPUT="$2"
W="${3:-1080}"
H="${4:-1920}"

if [ -z "$INPUT" ] || [ -z "$OUTPUT" ]; then
  echo "Uso: format_vertical.sh INPUT OUTPUT [ANCHO] [ALTO]" >&2
  exit 1
fi

ffmpeg -y -i "$INPUT" -filter_complex "\
[0:v]scale=${W}:${H}:force_original_aspect_ratio=increase,crop=${W}:${H},gblur=sigma=30,eq=brightness=-0.12[bg];\
[0:v]scale=${W}:${H}:force_original_aspect_ratio=decrease[fg];\
[bg][fg]overlay=(W-w)/2:(H-h)/2[vout]" \
-map "[vout]" -map 0:a? -c:v libx264 -crf 20 -preset veryfast -c:a aac "$OUTPUT" \
-hide_banner -loglevel error

DUR=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$OUTPUT")
DIMS=$(ffprobe -v quiet -show_entries stream=width,height -of csv=p=0:s=x "$OUTPUT" | head -1)
echo "OK: $OUTPUT generado (${DUR}s, ${DIMS})"
