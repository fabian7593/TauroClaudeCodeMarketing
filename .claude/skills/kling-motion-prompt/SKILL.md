---
name: kling-motion-prompt
description: Analiza una imagen existente (póster/key art) y genera un prompt de movimiento (image-to-video) para Kling AI, describiendo cómo animar los personajes y el fondo de ESA imagen puntual. Úsalo cuando el usuario pida "un prompt para animar/mover esta imagen en Kling", o pase una imagen de POST/assets/posters/ pidiendo movimiento.
---

# Generador de prompt de movimiento para Kling AI — TauroTV

Este skill NO genera un prompt de texto-a-imagen (eso es distinto y ya lo cubre `post-instagram` para teasers genéricos). Genera un prompt de **imagen-a-video**: el usuario ya tiene la imagen y la va a subir directo a Kling AI como referencia — el prompt de texto solo tiene que describir **qué se mueve y cómo**, no volver a describir el contenido de la imagen.

## 1. Conseguir la imagen
- Si el usuario menciona un archivo, buscalo en `POST/assets/posters/` (o donde lo indique).
- Si no especifica cuál, preguntá o listá lo que hay en `POST/assets/posters/` y pedí que elija.
- **Mirá la imagen con la tool `Read`** antes de escribir nada — el prompt tiene que basarse en lo que realmente hay en esa imagen puntual (composición, poses, capas), no en generalidades del personaje/franquicia.

## 2. Analizar la composición (mentalmente, antes de escribir el prompt)
Esto tiene que funcionar para **cualquier tipo de sujeto** que aparezca en el póster — personajes de anime, personas reales, animales, zombies, dinosaurios, monstruos, robots, lo que sea. No asumas que es siempre "un personaje anime": mirá la imagen y describí lo que hay de verdad.

Fijate en:
- **Capas de profundidad**: qué está en primer plano, qué en plano medio, qué en el fondo (cielo, partículas, texto/logo, patrón). Esto define qué mover con parallax.
- **Cada sujeto por separado** (ver sección 2.1 abajo) — no los trates como un bloque único.
- **Dirección de la "acción" implícita**: si alguien/algo mira/apunta/se mueve hacia un lado, el movimiento de cámara suele acompañar esa dirección en vez de contradecirla.
- **Mood/género**: acción, calma, misterio, terror, festivo — define el tipo de partículas/atmósfera y la velocidad del movimiento (rápido y con corte para acción, lento y suave para calma/nostalgia).
- **Elementos de fondo animables**: nubes, luces, destellos, humo, niebla, patrones de grilla/energía, follaje.
- **Dónde están el logo/título/texto** de la imagen (si el póster ya trae uno impreso) — necesitás esa ubicación para el negative prompt de la sección 3.2.

### 2.1 Analizar cada sujeto individualmente
Identificá **cada personaje/animal/criatura visible por separado** (no los agrupes) y para cada uno anotá, en 1 línea:
- Qué es (genérico: "el personaje central", "el animal a la izquierda", "la criatura de fondo" — sin describir apariencia/diseño, ver regla de la sección 3).
- Su pose actual (quieto, a mitad de salto, gruñendo, mirando a cámara, etc.)
- Qué animación puntual le corresponde, coherente con esa pose — nunca una acción nueva que contradiga la pose congelada.
- Reforzar que la cara/rostro se mantiene estable (esto también va reforzado en el negative prompt).

Esta lista de sujeto por sujeto es la que después se resume en el prompt principal (sección 3) — sirve para no olvidarte de animar a nadie y para no inventar movimientos que no correspondan a la pose real de cada uno.

## 3. Escribir el prompt

### 3.1 Prompt principal (positivo)
Reglas duras:
- **En inglés** (Kling responde mejor en inglés).
- **Corto**: unas pocas oraciones, no un párrafo largo — Kling funciona mejor con instrucciones concisas y específicas que con descripciones floridas.
- **Solo movimiento, nunca apariencia**: no describas quién es cada sujeto, su diseño, especie, colores, etc. — eso ya está en la imagen de referencia. Describir apariencia en el prompt es redundante y además evita que reproduzcas descripciones de personajes con derechos de autor en texto.
- Cubrí, en este orden:
  1. **Movimiento de cámara**: push-in lento, pan lateral, órbita sutil, ligero zoom out — elegido según la composición.
  2. **Movimiento de cada sujeto** (usando el análisis de 2.1): una cláusula corta por sujeto relevante, mencionando qué se mueve (respiración, parpadeo, pelo/pelaje/ropa con viento, un miembro que termina el gesto ya empezado) — siempre aclarando que el rostro se mantiene estable/consistente.
  3. **Movimiento de fondo**: parallax de las capas, partículas (chispas/polvo/nieve/niebla/sangre según el mood), luces o destellos parpadeando, nubes desplazándose.
  4. **Estilo/atmósfera**: 1-2 palabras clave de cierre (ej. "cinematic, subtle loop", "dynamic action energy").

### 3.2 Negative prompt (obligatorio, siempre incluido)
Kling acepta un campo de negative prompt aparte — armá SIEMPRE uno, combinando esta base fija con lo específico de la imagen:

Base fija (usar siempre, sin importar el póster):
```
distorted logo, warped text, blurry letters, melting text, garbled title, warped face,
deformed face, asymmetrical eyes, morphing face, face swapping between characters,
extra limbs, extra fingers, fused limbs, unnatural body warping, disfigured anatomy,
flickering, glitch artifacts, jittery motion, low quality, blurry, distorted watermark
```

Agregale algo puntual de la imagen si aplica (ej. si el logo está en una esquina específica: "no distortion in the top-left logo area"; si hay texto del título en la parte de abajo: "title text at the bottom stays sharp and undistorted").

## 4. Entrega
Mostrá, en este orden:
1. El análisis sujeto por sujeto (2.1), breve, en español, para que el usuario vea el razonamiento.
2. El prompt principal (positivo) en un bloque de código, en inglés, listo para copiar y pegar.
3. El negative prompt en otro bloque de código separado.
4. Qué archivo de imagen usar como referencia (ruta completa).
5. Una recomendación breve de configuración de Kling: modo image-to-video, duración corta (5s es el default más seguro), "motion strength" media-baja si la imagen tiene mucho detalle o texto/logo (para no distorsionarlo), media-alta si es una escena de acción clara.

No generes la imagen ni llames a ninguna API de Kling — este skill solo produce el texto del prompt (positivo + negativo) para que el usuario lo pegue él mismo.
