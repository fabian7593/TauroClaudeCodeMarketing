---
name: post-copy
description: Escribe el texto (caption + hashtags) de un post de Instagram/Facebook/TikTok/YouTube Shorts para la marca configurada en este proyecto, siguiendo sus reglas de tono y de marca. Úsalo cuando el usuario pida crear, redactar o armar el texto de un post para un producto/show/servicio/anuncio.
---

# post-copy — texto de post para redes sociales

Este skill NO genera imágenes ni videos (eso lo hacen `post-image`, `post-carousel` y `reel-highlights`) — genera únicamente el **texto** del post: caption, hashtags, y (si aplica) guion corto para formatos de video vertical.

## 0. Marca del proyecto
Antes de escribir una sola línea, leé `CLAUDE.md` y `brand.config.json` en la raíz del proyecto (ver skill `content-setup` si `brand.config.json` no existe todavía — corré ese skill primero, no inventes reglas de marca). De ahí sale: tono de voz, CTA fijo de cierre, menciones prohibidas, reclamos que no se pueden prometer, y estructura de post si el proyecto define una propia.

Si el proyecto no tiene ningún archivo de reglas de marca, preguntale al usuario por lo mínimo indispensable antes de escribir: nombre de marca, tono deseado, y si hay un CTA fijo que siempre tiene que aparecer.

## 1. Recopilar datos
Si falta información, preguntá:
- Nombre del producto/show/servicio y categoría/género
- Datos técnicos relevantes si aplican (ej. audios e idiomas de subtítulos disponibles, si la marca es de streaming/video)
- Tipo de post (entretenimiento / producto / prueba social — o el mix que defina el proyecto)
- Plataforma de destino (Instagram, Facebook, TikTok, YouTube Shorts, X) — el texto base es similar entre Instagram/Facebook, pero TikTok/Shorts necesitan además un guion corto de video, y X necesita una versión recortada (ver paso 4).

## 2. Escribir el post
Seguí la estructura de post que defina `CLAUDE.md` del proyecto. Si no define una estructura propia, usá esta por default:
1. Hook emocional (1-2 líneas que paren el scroll)
2. CTA agresivo con la acción que la marca quiera (comprar, escribir al DM, visitar el sitio)
3. Info técnica relevante si aplica
4. Descripción cercana, humana, sin sonar a IA (2-3 líneas)
5. Pregunta de engagement
6. Hashtags (ver paso 3)

Verificaciones obligatorias antes de entregar (mecánicas, no "a ojo" — chequealas una por una contra `brand.config.json`):
- [ ] El hook es único, nunca reutilizado en posts anteriores de esta cuenta
- [ ] No aparece ninguna palabra de `forbiddenMentions`
- [ ] No se promete nada de `unsupportedClaims`
- [ ] Se incluye el `cta` fijo tal cual está en `brand.config.json`
- [ ] El tono coincide con `tone`

## 3. Hashtags — van DENTRO del mismo texto, no aparte
Generá 5-8 hashtags relevantes (categoría/nicho del contenido, geografía si la marca tiene mercado específico, y marca) y ponelos al final del mismo bloque de texto — **no los guardes en un archivo separado**, van pegados abajo del caption porque así es como se pegan en la plataforma real.

## 4. Adaptaciones por plataforma
- **TikTok/Shorts**: además del caption, generá un guion de 15-30 segundos con marcas de tiempo simples (0-3s hook visual, 3-15s desarrollo, 15-30s CTA).
- **X**: además del caption largo, generá una versión corta (hook + CTA, sin todo el desarrollo ni todos los hashtags) — X no tiene espacio para el post completo.

No generes acá un prompt de imagen ni de animación — si el usuario necesita eso, es el skill `motion-prompt` (a partir de una imagen real) el que lo cubre; ese prompt se muestra en el chat, no se guarda como archivo de este post.

## 5. Guardar en la carpeta del proyecto
La raíz de contenido es `contentRoot` de `brand.config.json` (default `POST/` si no está configurado). Instagram y Facebook comparten el mismo texto e imagen — van en una única carpeta, no dupliques contenido en carpetas separadas por plataforma:

```
<contentRoot>/social/[slug]/
├── post.txt          (caption + hashtags juntos, listo para copiar y pegar)
├── images/            (lo produce post-image / post-carousel)
├── reels/              (lo produce reel-highlights, si aplica)
├── tiktok/
│   └── guion.txt        (solo si el post es para TikTok/Shorts)
└── youtube-shorts/
    └── guion.txt
```

`slug` en minúsculas y guiones (ej. `frieren`, `dragon-ball-z`). Si la carpeta `<contentRoot>/social/[slug]/` no existe, creala. Si el post lleva imagen, usá el skill `post-image` (o `post-carousel` si son varias) para producirla dentro de `images/`.

## 6. Confirmación final
Después de guardar `post.txt`, mostrá en el chat un resumen corto de qué se creó y en qué ruta, más el texto completo del post para que el usuario lo revise sin abrir el archivo.
