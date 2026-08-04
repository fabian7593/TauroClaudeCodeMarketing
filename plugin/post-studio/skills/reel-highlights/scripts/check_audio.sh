#!/usr/bin/env bash
# Verifica que un archivo (audio o video con audio) no haya quedado en silencio.
# Reemplaza la lectura manual del output de volumedetect por un veredicto PASS/FAIL explícito.
#
# Uso: check_audio.sh ARCHIVO [UMBRAL_DB]
#   ARCHIVO    - .m4a, .mp3, .mp4, cualquier archivo con pista de audio
#   UMBRAL_DB  - opcional, default -50 (si mean_volume da por debajo de esto, FAIL)
#
# Salida: imprime mean_volume/max_volume, y termina con exit 0 (PASS) o exit 1 (FAIL).
# Si da FAIL, no sigas: revisá el orden de -ss/-t antes de -i (regla dura, ver SKILL.md).

set -e

FILE="$1"
THRESHOLD="${2:--50}"

if [ -z "$FILE" ]; then
  echo "Uso: check_audio.sh ARCHIVO [UMBRAL_DB]" >&2
  exit 1
fi

RESULT=$(ffmpeg -i "$FILE" -af volumedetect -f null - 2>&1 | grep -E "mean_volume|max_volume" || true)
echo "$RESULT"

MEAN=$(echo "$RESULT" | grep mean_volume | grep -oE '\-?[0-9]+\.[0-9]+' | head -1)

if [ -z "$MEAN" ]; then
  echo "FAIL: no se pudo leer mean_volume — ¿el archivo tiene pista de audio?"
  exit 1
fi

BELOW=$(awk "BEGIN{print (${MEAN} < ${THRESHOLD}) ? 1 : 0}")
if [ "$BELOW" -eq 1 ]; then
  echo "FAIL: mean_volume=${MEAN}dB está por debajo del umbral de ${THRESHOLD}dB — el audio puede estar en silencio."
  exit 1
else
  echo "PASS: mean_volume=${MEAN}dB (umbral: ${THRESHOLD}dB)"
fi
