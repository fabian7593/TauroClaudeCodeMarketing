#!/usr/bin/env bash
# Une 2+ clips de video con transición xfade encadenada, calculando los offsets
# acumulados automáticamente a partir de la duración real de cada clip (ffprobe).
# Reemplaza el cálculo manual de "offset = duración_acumulada - duración_transición".
#
# Uso: join_xfade.sh DURACION_TRANSICION OUTPUT CLIP1 CLIP2 [CLIP3 ...]
#   DURACION_TRANSICION - en segundos, ej. 0.35 (default recomendado) o 0.15-0.2 para
#                          contenido rápido/acción (ver SKILL.md paso H-6)
#   OUTPUT               - archivo de video unido (sin audio)
#   CLIP1, CLIP2, ...     - al menos 2 clips, en el orden en que van en el reel
#
# Si solo tenés 1 clip, no uses este script — usalo directo como video_sin_audio.mp4.

set -e

XFADE_DUR="$1"
OUTPUT="$2"
shift 2
CLIPS=("$@")
N=${#CLIPS[@]}

if [ -z "$XFADE_DUR" ] || [ -z "$OUTPUT" ] || [ "$N" -lt 2 ]; then
  echo "Uso: join_xfade.sh DURACION_TRANSICION OUTPUT CLIP1 CLIP2 [CLIP3 ...]" >&2
  echo "Se necesitan al menos 2 clips." >&2
  exit 1
fi

INPUT_ARGS=()
DURS=()
for c in "${CLIPS[@]}"; do
  INPUT_ARGS+=(-i "$c")
  d=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$c")
  DURS+=("$d")
done

FILTER=""
PREV="[0:v]"
CUM="${DURS[0]}"
for ((i = 1; i < N; i++)); do
  OFFSET=$(awk "BEGIN{printf \"%.6f\", ${CUM} - ${XFADE_DUR}}")
  if [ "$i" -eq $((N - 1)) ]; then
    OUT_LABEL="[vout]"
  else
    OUT_LABEL="[j${i}]"
  fi
  FILTER+="${PREV}[${i}:v]xfade=transition=fade:duration=${XFADE_DUR}:offset=${OFFSET}${OUT_LABEL};"
  PREV="[j${i}]"
  CUM=$(awk "BEGIN{printf \"%.6f\", ${CUM} + ${DURS[$i]} - ${XFADE_DUR}}")
done
FILTER="${FILTER%;}"

ffmpeg -y "${INPUT_ARGS[@]}" -filter_complex "$FILTER" -map "[vout]" \
  -c:v libx264 -crf 20 -preset veryfast "$OUTPUT" \
  -hide_banner -loglevel error

FINAL_DUR=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$OUTPUT")
echo "OK: $OUTPUT generado con ${N} clips, transición=${XFADE_DUR}s. Duración final: ${FINAL_DUR}s (esperada ~${CUM}s)."
