---
name: motion-prompt
description: Analiza una imagen existente (foto/arte/producto) y genera un prompt de movimiento (image-to-video) para Kling AI, describiendo cómo animar los sujetos y el fondo de ESA imagen puntual. Úsalo cuando el usuario pida "un prompt para animar/mover esta imagen en Kling", o pase una imagen de assets/posters/ pidiendo movimiento.
---

# motion-prompt — prompt de movimiento para Kling AI

Este skill NO genera un prompt de texto-a-imagen (eso lo cubre `post-copy` para teasers genéricos, si el proyecto lo necesita). Genera un prompt de **imagen-a-video**: el usuario ya tiene la imagen y la va a subir directo a Kling AI como referencia — el prompt de texto solo tiene que describir **qué se mueve y cómo**, no volver a describir el contenido de la imagen.

Es intencionalmente específico de Kling AI (la sintaxis y el estilo de prompt están tuneados para esa herramienta) — no es un generador de prompts genérico para cualquier tool de video.

## 1. Conseguir la imagen
- Si el usuario menciona un archivo, buscalo en `<contentRoot>/assets/posters/` (`contentRoot` sale de `brand.config.json`, default `POST/`), o donde lo indique.
- Si no especifica cuál, preguntá o listá lo que hay en esa carpeta y pedí que elija.
- **Mirá la imagen con la tool `Read`** antes de escribir nada — el prompt tiene que basarse en lo que realmente hay en esa imagen puntual (composición, poses, capas), no en generalidades del producto/franquicia.

## 2. Analizar la composición (mentalmente, antes de escribir el prompt)
Esto tiene que funcionar para **cualquier tipo de sujeto** que aparezca en la imagen — personas, personajes, animales, objetos/producto, lo que sea. No asumas un tipo de sujeto fijo: mirá la imagen y describí lo que hay de verdad.

Fijate en:
- **Capas de profundidad**: qué está en primer plano, plano medio, fondo (cielo, partículas, texto/logo, patrón). Define qué mover con parallax.
- **Cada sujeto por separado** (ver 2.1) — no los trates como un bloque único.
- **Dirección de la "acción" implícita**: si algo mira/apunta/se mueve hacia un lado, el movimiento de cámara suele acompañar esa dirección.
- **Mood/género**: acción, calma, misterio, festivo — define partículas/atmósfera y velocidad del movimiento.
- **Elementos de fondo animables**: nubes, luces, destellos, humo, niebla, patrones, follaje.
- **Dónde están el logo/título/texto** de la imagen (si ya trae uno impreso) — necesario para el negative prompt (3.2).

### 2.1 Analizar cada sujeto individualmente
Identificá **cada sujeto visible por separado** (no los agrupes) y para cada uno anotá, en 1 línea:
- Qué es (genérico: "el sujeto central", "el elemento a la izquierda" — sin describir apariencia/diseño con detalle protegido por derechos de autor, ver regla de la sección 3).
- Su pose/estado actual.
- Qué animación puntual le corresponde, coherente con esa pose — nunca una acción nueva que la contradiga.
- Reforzar que la cara/rostro (si aplica) se mantiene estable — esto también va en el negative prompt.

## 3. Escribir el prompt

### 3.1 Prompt principal (positivo)
Reglas duras:
- **En inglés** (Kling responde mejor en inglés).
- **Corto**: unas pocas oraciones, no un párrafo largo.
- **Solo movimiento, nunca apariencia**: no describas quién es cada sujeto, su diseño, colores, etc. — eso ya está en la imagen de referencia. Describir apariencia es redundante y además evita reproducir descripciones de contenido con derechos de autor en texto.
- Cubrí, en este orden:
  1. **Movimiento de cámara**: push-in lento, pan lateral, órbita sutil, zoom out — elegido según la composición.
  2. **Movimiento de cada sujeto** (usando 2.1): una cláusula corta por sujeto relevante, aclarando que el rostro se mantiene estable/consistente si aplica.
  3. **Movimiento de fondo**: parallax de capas, partículas, luces/destellos, nubes.
  4. **Estilo/atmósfera**: 1-2 palabras clave de cierre (ej. "cinematic, subtle loop").

### 3.2 Negative prompt (obligatorio, siempre incluido)
Armá SIEMPRE uno, combinando esta base fija con lo específico de la imagen:

```
distorted logo, warped text, blurry letters, melting text, garbled title, warped face,
deformed face, asymmetrical eyes, morphing face, face swapping between characters,
extra limbs, extra fingers, fused limbs, unnatural body warping, disfigured anatomy,
flickering, glitch artifacts, jittery motion, low quality, blurry, distorted watermark
```

Agregale algo puntual de la imagen si aplica (ej. "no distortion in the top-left logo area").

## 4. Entrega
Mostrá, en este orden:
1. El análisis sujeto por sujeto (2.1), breve, en español.
2. El prompt principal (positivo) en un bloque de código, en inglés.
3. El negative prompt en otro bloque de código separado.
4. Qué archivo de imagen usar como referencia (ruta completa).
5. Una recomendación breve de configuración de Kling: modo image-to-video, duración corta (5s default más seguro), "motion strength" media-baja si la imagen tiene mucho detalle/texto/logo, media-alta si es una escena de acción clara.

Este skill solo produce el texto del prompt (positivo + negativo) para que el usuario lo pegue él mismo en Kling — no genera la imagen ni llama a ninguna API, y no guarda el prompt como archivo del proyecto (se muestra en el chat; si el usuario lo quiere guardar, que lo pida explícitamente).
