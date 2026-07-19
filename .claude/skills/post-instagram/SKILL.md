---
name: post-instagram
description: Genera un post de Instagram/Facebook/TikTok para TauroTV siguiendo la estructura y reglas de marca definidas en CLAUDE.md. Úsalo cuando el usuario pida crear, redactar o armar un post para una serie, película o anuncio de TauroTV.
---

# Generador de Post — TauroTV

Cuando te pidan un post, seguí este proceso:

## 1. Recopilar datos
Si falta información, preguntá:
- Nombre del show/película y género
- Audios disponibles e idiomas de subtítulos
- Tipo de post según el mix 70/20/10: ¿entretenimiento, producto, o prueba social?
- Plataforma de destino (Instagram, Facebook, TikTok, YouTube Shorts) — el texto es similar pero TikTok/Shorts necesitan un guion corto de video además del caption

## 2. Escribir el post
Seguí EXACTAMENTE la estructura de 6 pasos definida en CLAUDE.md (hook → CTA agresivo → info técnica → descripción → pregunta de engagement → hashtags).

Verificaciones obligatorias antes de entregar:
- [ ] El hook es único, nunca reutilizado en posts anteriores de esta cuenta
- [ ] NO se menciona ninguna plataforma de streaming competidora
- [ ] Se incluye el CTA fijo de cierre tal cual está en CLAUDE.md
- [ ] No se promete compatibilidad con dispositivos no soportados

## 3. Hashtags
Generá 5-8 hashtags mezclando: género del show, LATAM/Costa Rica (#CostaRica #TicosEnCasa etc.), y marca (#TauroTV).

## 4. Prompt para Kling AI
Generá también un prompt corto en inglés, listo para pegar en Kling AI, describiendo una escena/imagen tipo teaser genérica inspirada en el tono y género del show (nunca reproduciendo escenas, personajes o arte protegido por derechos de autor de la obra original — mantenelo genérico: mood, colores, atmósfera).

Para TikTok/Shorts, además generá un guion de 15-30 segundos con marcas de tiempo simples (0-3s hook visual, 3-15s desarrollo, 15-30s CTA).

## 5. Guardar en carpetas del proyecto
**Instagram y Facebook están unificados**: son el mismo formato (misma imagen, mismo texto), así que van en una única carpeta `social/` — no dupliques el texto en `instagram/` y `facebook/` por separado. TikTok/Shorts sí son distintos (video, guion propio) y mantienen sus propias carpetas. Creá las carpetas si no existen:

```
POST/
├── social/
│   └── [nombre-serie-o-pelicula]/
│       ├── post.txt          (texto único, se publica igual en IG y Facebook)
│       ├── hashtags.txt
│       ├── kling-prompt.txt  (solo si no se usa post-image con póster real)
│       └── images/
│           └── 01-[slug].png (o más, si es un carrusel — ver skill post-image / post-carousel)
├── tiktok/
│   └── [nombre-serie-o-pelicula]/
│       ├── guion.txt         (guion con marcas de tiempo)
│       └── kling-prompt.txt
└── youtube-shorts/
    └── [nombre-serie-o-pelicula]/
        ├── guion.txt
        └── titulo-descripcion.txt
```

Usá minúsculas y guiones para el nombre de la carpeta de cada show (ej. `frieren`, `dragon-ball-z`). Si el post lleva imagen generada por póster real (no un prompt de Kling AI), usá el skill `post-image` para producirla dentro de `social/[slug]/images/`.

Nota histórica: posts creados antes de esta convención quedaron en carpetas separadas `instagram/` y `facebook/` — no hace falta migrarlos, pero todo post nuevo va en `social/`.

## 6. Confirmación final
Después de guardar los archivos, mostrá en el chat un resumen corto de qué se creó y en qué rutas, más el texto del post principal para que el usuario lo pueda revisar sin tener que abrir cada archivo.
