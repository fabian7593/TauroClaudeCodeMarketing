# Cómo usar este kit

Este proyecto usa el plugin **post-studio** (vive en [`plugin/post-studio/`](plugin/post-studio/)) para crear y publicar contenido de TauroTV en redes sociales. El plugin es genérico — no tiene nada de TauroTV escrito adentro — y todo lo específico de esta marca (logo, tono, CTA, reglas) vive en [`CLAUDE.md`](CLAUDE.md) y [`brand.config.json`](brand.config.json), en este mismo repo.

## 0. Instalación (una sola vez por PC)
Si es la primera vez que abrís este repo en esta máquina, corré esto en el chat de Claude Code:
```
/plugin marketplace add .
/plugin install post-studio@post-studio-marketplace
```
Después corré `/cmd-setup` una vez — valida (y crea si falta) las carpetas de `POST/`, confirma el logo y `brand.config.json`, revisa que tengas `ffmpeg`/Python/Chrome instalados, y te avisa si falta conectar el navegador Chrome real en Claude. Si algo falta, te va a decir exactamente qué hacer — no vas a tener que adivinar.

Guía completa, con explicación de cada comando/skill y ejemplos paso a paso: [`plugin/post-studio/docs/GUIA-DE-USO.md`](plugin/post-studio/docs/GUIA-DE-USO.md).

## Comandos disponibles
Todos empiezan con `cmd-` a propósito — así se distinguen a simple vista de los skills (que se activan solos, sin que los tipees).

| Comando | Qué hace |
|---|---|
| `/cmd-post <show>` | Post completo de 1 imagen: texto + arte, listo para IG/Facebook. Pregunta layout y si querés reel también. |
| `/cmd-carousel <coleccion>` | Post de varias imágenes en carrusel (1 solo texto), desde una subcarpeta de `POST/assets/posters/`. |
| `/cmd-reel <video>` | Reel (highlights, video completo, o fusión de varios) con marca de agua, desde video(s) en `POST/assets/videos/`. |
| `/cmd-motion <imagen>` | Prompt de movimiento para animar un póster en Kling AI. |
| `/cmd-publish <contenido>` | Publica o programa en redes sociales un contenido ya generado. |
| `/cmd-setup` | Chequea/prepara el entorno (carpetas, software, marca, conectores). Corré esto primero en una PC nueva. |

También podés pedirlo en lenguaje natural ("hacéme un post de Frieren") — los skills detrás de estos comandos se activan solos con la descripción, no hace falta tipear el comando exacto.

Ejemplo:
```
/cmd-post Frieren, anime, drama y fantasía
```
Claude va a preguntar lo que le falte (audios, subtítulos, tipo de post, layout) y va a entregar todo guardado en `POST/social/[nombre-del-show]/`, siguiendo las reglas de marca de `CLAUDE.md`/`brand.config.json` automáticamente.

## Publicación
`/cmd-publish` publica o programa directo en redes usando Zernio primero, upload-post.com como respaldo. Hoy ese paso necesita que alguien arrastre el archivo a la ventana del navegador cuando Claude lo pida (limitación de la herramienta, no del plugin) — por eso todavía no hay scheduling 100% desatendido.

## Para escalar después
El plugin está armado para crecer: agregar un skill nuevo (otro tipo de pieza, otra plataforma, otro formato) no rompe lo que ya existe — ver la sección "Agregar un skill nuevo" en la guía completa. También se pueden sumar subagentes especializados en `.claude/agents/` (ej. uno que audite reglas de marca antes de publicar). Avisame cuando quieras armar alguna de estas y seguimos.
