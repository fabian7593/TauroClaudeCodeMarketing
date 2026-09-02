#!/usr/bin/env bash
# Aplica marca de agua de marca: logo centrado arriba de un texto (sitio/handle) con sombra,
# abajo a la derecha. Calibrado para video vertical 1080x1920.
#
# Uso: apply_watermark.sh INPUT LOGO OUTPUT TEXTO [FONTSIZE] [LOGO_ANCHO] [TEXT_W] [FONT_PATH]
#   INPUT      - video vertical ya formateado (salida de format_vertical.sh)
#   LOGO       - ruta al PNG/JPG del logo de la marca (si el logo original es .svg, rasterizalo
#                a PNG antes de llamar a este script — ffmpeg no decodifica SVG)
#   OUTPUT     - archivo final
#   TEXTO      - obligatorio, sale de brand.config.json -> website (no hay default: es dato
#                de marca, no se asume ningún sitio ajeno)
#   FONTSIZE   - opcional, default 40
#   LOGO_ANCHO - opcional, default 96 (px de ancho del logo ya escalado)
#   TEXT_W     - opcional. Si no se pasa, este script MIDE el ancho real del texto renderizado
#                con la fuente/tamaño elegidos (ver "Medir TEXT_W" abajo) en vez de asumir un
#                número fijo — así funciona igual de bien con un texto largo o corto sin que
#                haya que recalibrar nada a mano.
#   FONT_PATH  - opcional. Si no se pasa, se autodetecta una fuente bold instalada según el SO
#                (ver "Resolver fuente" abajo). Pasalo explícito si la autodetección no encuentra
#                nada en tu máquina.

set -e

INPUT="$1"
LOGO="$2"
OUTPUT="$3"
TEXT="$4"
FONTSIZE="${5:-40}"
LOGO_W="${6:-96}"
TEXT_W="$7"
FONT_PATH="$8"
RIGHT_PAD=55

if [ -z "$INPUT" ] || [ -z "$LOGO" ] || [ -z "$OUTPUT" ] || [ -z "$TEXT" ]; then
  echo "Uso: apply_watermark.sh INPUT LOGO OUTPUT TEXTO [FONTSIZE] [LOGO_ANCHO] [TEXT_W] [FONT_PATH]" >&2
  echo "TEXTO es obligatorio (viene de brand.config.json -> website) — no hay marca por default." >&2
  exit 1
fi

# --- Resolver fuente: probar rutas típicas por SO, en orden, hasta encontrar una que exista ---
# NOTA: se probó font='...' vía fontconfig como alternativa portable y en Windows sin
# fontconfig.conf configurado directamente hace *segfault* (confirmado en esta build de ffmpeg
# con --enable-fontconfig) — por eso se usa fontfile= con ruta real detectada, no font=.
if [ -z "$FONT_PATH" ]; then
  case "$(uname -s 2>/dev/null)" in
    MINGW*|MSYS*|CYGWIN*)
      CANDIDATES=("C:/Windows/Fonts/arialbd.ttf" "C:/Windows/Fonts/segoeuib.ttf") ;;
    Darwin*)
      CANDIDATES=("/System/Library/Fonts/Supplemental/Arial Bold.ttf" "/Library/Fonts/Arial Bold.ttf" "/System/Library/Fonts/Helvetica.ttc") ;;
    *)
      CANDIDATES=("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf") ;;
  esac
  for c in "${CANDIDATES[@]}"; do
    if [ -f "$c" ]; then FONT_PATH="$c"; break; fi
  done
fi

if [ -z "$FONT_PATH" ] || [ ! -f "$FONT_PATH" ]; then
  echo "ERROR: no se encontró una fuente bold instalada en las rutas conocidas para este sistema operativo." >&2
  echo "Pasá una ruta explícita como 8vo argumento (FONT_PATH), o instalá una fuente sans-serif bold." >&2
  exit 1
fi
# ffmpeg necesita los ':' de rutas Windows escapados dentro del filtro drawtext
FONT_PATH_ESCAPED="${FONT_PATH//:/\\:}"

# --- Medir TEXT_W si no se pasó explícito: renderizar el texto real y medir su bounding box ---
if [ -z "$TEXT_W" ]; then
  MEASURE_LINE=$(ffmpeg -f lavfi -i "color=c=black:s=600x150:d=1" \
    -vf "drawtext=fontfile='${FONT_PATH_ESCAPED}':text='${TEXT}':fontsize=${FONTSIZE}:fontcolor=white:x=10:y=10,cropdetect=24:2:0" \
    -f null - -loglevel verbose 2>&1 | grep -o "crop=[0-9]*:[0-9]*:[0-9]*:[0-9]*" | tail -1)
  if [ -z "$MEASURE_LINE" ]; then
    echo "ERROR: no se pudo medir el ancho del texto '${TEXT}' automáticamente. Pasá TEXT_W a mano (7mo argumento)." >&2
    exit 1
  fi
  # MEASURE_LINE tiene la forma "crop=W:H:X:Y" — el ancho es lo que queda entre "=" y el primer ":"
  TEXT_W=$(echo "$MEASURE_LINE" | sed 's/crop=//' | cut -d: -f1)
fi

LOGO_X_OFFSET=$((RIGHT_PAD + TEXT_W / 2))

ffmpeg -y -i "$INPUT" -i "$LOGO" -filter_complex "\
[1:v]scale=${LOGO_W}:-1[logo]; \
[0:v][logo]overlay=x=W-${LOGO_X_OFFSET}-w/2:y=H-84-h[withlogo]; \
[withlogo]drawtext=fontfile='${FONT_PATH_ESCAPED}':text='${TEXT}':fontsize=${FONTSIZE}:fontcolor=white:shadowcolor=black@0.85:shadowx=2:shadowy=2:x=W-tw-${RIGHT_PAD}:y=H-70" \
-c:v libx264 -crf 20 -preset veryfast -c:a copy "$OUTPUT" \
-hide_banner -loglevel error

echo "OK: $OUTPUT generado con marca de agua (texto='${TEXT}', logo=${LOGO_W}px, text_w=${TEXT_W}px medido, fuente=${FONT_PATH})."
echo "Recordá sacar un frame y mirarlo con Read para confirmar que no se superponen ni tocan el borde."
