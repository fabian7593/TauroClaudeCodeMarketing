# Guía de uso — post-studio

Guía simple, pensada para alguien que no escribió el plugin: qué es cada cosa, cómo se activa, y qué esperar como resultado. Para la referencia técnica completa (arquitectura, diagrama, schema de `brand.config.json`, requisitos), ver el [`README.md`](../README.md) del plugin.

## 1. Qué es esto
**post-studio** es un plugin de Claude Code para crear y publicar contenido en redes sociales (Instagram, Facebook, TikTok, X, YouTube Shorts): escribe el texto del post, arma la imagen o el reel con tu marca (logo + colores), y lo publica o programa. No está atado a ningún negocio — funciona para cualquier marca que configures en el proyecto donde lo instales.

Dos tipos de piezas, y es importante no confundirlas:
- **Comandos** (`/cmd-algo`): vos los tipeás a propósito. Siempre empiezan con `cmd-` para que se note que son un atajo explícito, no magia.
- **Skills**: hacen el trabajo real. Se activan solos cuando Claude entiende que tu pedido calza con lo que hacen — no hace falta tipear nada especial, alcanza con pedirlo en lenguaje natural ("hacéme un post de tal cosa"). Los comandos, por dentro, simplemente invocan uno o más skills.

## 2. Instalación en una PC/proyecto nuevo
Una sola vez por máquina:
```
/plugin marketplace add .
/plugin install post-studio@post-studio-marketplace
```
(corré esto desde la raíz del repo que tiene la carpeta `plugin/post-studio/`). Después:
```
/cmd-setup
```
Esto valida y prepara todo lo demás — ver sección 6. Si algo falta (una carpeta, un programa, el logo, un conector), te lo va a decir con instrucciones concretas de qué hacer, nunca falla en silencio.

## 3. Comandos — qué hacen, cuándo usarlos, qué queda al final

| Comando | Cuándo usarlo | Qué dispara | Resultado esperado |
|---|---|---|---|
| `/cmd-post <tema>` | Post de una sola imagen (el caso más común) | `crear-texto` + `crear-imagen` (+ `crear-reel` si pedís reel también) | `post.txt` (texto listo para pegar) + `images/01-....png` en `<contentRoot>/social/<categoria>/<slug>/` |
| `/cmd-carousel <coleccion>` | Un post con varias imágenes deslizables | `crear-carrusel` (que a su vez usa `crear-imagen` N veces + `crear-texto`) | `post.txt` + `images/01..NN-....png` |
| `/cmd-reel <video(s)>` | Convertir video(s) en un reel vertical con marca de agua | `crear-reel` | `reels/<slug>-reel.mp4` |
| `/cmd-motion <imagen>` | Necesitás animar una imagen en Kling AI | `generar-prompt-movimiento` | Un prompt (texto) mostrado en el chat — no se guarda archivo |
| `/cmd-publish <contenido>` | Ya tenés el post armado y lo querés publicar/programar | `publicar-contenido` | Publicación real (o programada) en Instagram/Facebook/X |
| `/cmd-setup` | Primera vez en una PC, o cambiaste de marca/logo | `preparar-entorno` | Carpetas creadas, `brand.config.json` al día, software y conectores verificados |
| `/cmd-catalogo` | Actualizaste el catálogo, o querés saber qué falta producir | `sincronizar-catalogo` | `catalogo.json` al día, o el listado de lo que buscaste / lo pendiente |
| `/cmd-contenido <título>` | El pedido nace del catálogo (lo más común hoy) | `planear-contenido` + todos los de creación | La pieza completa: ficha `00` + artes `01..NN` + `post.txt` + `pieza.json` |

`<contentRoot>` es la carpeta de contenido del proyecto (`brand.config.json` → `contentRoot`; en este proyecto es `POST/`).

## 4. Skills — qué hacen y cómo se activan

| Skill | Se activa cuando... | Qué hace |
|---|---|---|
| `preparar-entorno` | corrés `/cmd-setup`, o otro skill detecta que falta algo | Preflight completo: carpetas, `brand.config.json`, logo, software, conectores |
| `crear-texto` | pedís crear/redactar el texto de un post | Escribe caption + hashtags siguiendo el tono y reglas de marca del proyecto |
| `crear-imagen` | hay que generar el arte (PNG) de un post | Renderiza la imagen final a partir del template + logo + colores de marca |
| `crear-carrusel` | pedís un post con varias imágenes / mencionás una carpeta de colección | Orquesta `crear-imagen` N veces + `crear-texto` en modo carrusel |
| `generar-prompt-movimiento` | pedís animar una imagen puntual en Kling AI | Genera el prompt de movimiento (positivo + negativo) para esa imagen |
| `crear-reel` | pedís un reel/clip/highlight a partir de video(s) | Recorta lo mejor (o mantiene el video completo) y le pone formato vertical + marca de agua |
| `publicar-contenido` | pedís publicar/programar/subir algo a redes | Publica vía Zernio o upload-post.com, con verificación de marca obligatoria antes de publicar |
| `sincronizar-catalogo` | hay que actualizar o consultar el catálogo maestro | Lo baja a `catalogo.json` y lo consulta por script, sin quemar contexto |
| `planear-contenido` | el pedido nace de un título/colección del catálogo | Decide qué piezas armar (imagen sola / carrusel de películas / de temporadas / dos piezas) y lleva el estado de producción |
| `crear-sinopsis` | se produce cualquier pieza de contenido | La ficha explicativa con texto largo + tira de pósters + % de aprobación (imagen `00`, siempre) |

Todos leen `CLAUDE.md` y `brand.config.json` del proyecto donde estén instalados — nunca asumen una marca fija.

## 5. Ejemplo paso a paso (post simple)

Pedido: *"Hacéme un post de la serie Nombre de Ejemplo, es de terror."*

1. **Claude activa `crear-texto`** (sin que tipees nada) y pregunta lo que falte: audios/subtítulos disponibles, tipo de post (entretenimiento/producto/prueba social), plataforma.
2. Contestás. Claude escribe el caption completo (hook + CTA + descripción + pregunta + hashtags) y te lo muestra.
3. **Se activa `crear-imagen`**: pregunta el layout (`full_bleed` por default, o `panel_lateral`) y qué imagen fuente usar de `POST/assets/posters/`.
4. Claude renderiza el PNG y te lo muestra antes de guardarlo.
5. **Resultado final en disco**:
   ```
   POST/social/<series|peliculas>/nombre-de-ejemplo/
   ├── post.txt
   └── images/
       └── 01-nombre-de-ejemplo.png
   ```
6. Si querés publicarlo ya: `/cmd-publish nombre-de-ejemplo` — Claude te va a confirmar la marca/cuenta, la fecha/hora real, y te va a pedir que arrastres el archivo al navegador cuando corresponda (esa parte todavía es manual, ver sección 8).

## 6. Configurar tu marca la primera vez
`/cmd-setup` te va a pedir (si `brand.config.json` no existe todavía): nombre de marca, sitio/handle, CTA fijo, tono, menciones prohibidas (competidores que no querés mostrar), reclamos que no podés prometer, y zona horaria. Si ya tenés un `CLAUDE.md` con reglas de marca, Claude propone los valores leyéndolo de ahí y solo te pregunta lo que falte.

El logo tiene que estar en `<contentRoot>/assets/logo/` (PNG, JPG o SVG). Si tiene mucho margen/padding alrededor, Claude te ofrece recortarlo automáticamente sin tocar el original.

## 7. Si algo falla
Corré `/cmd-setup` — es la herramienta de diagnóstico. Te va a decir puntualmente qué falta:
- Carpeta faltante → te ofrece crearla.
- Programa faltante (`ffmpeg`, Python, Chrome) → te da el comando de instalación para tu sistema operativo.
- Logo faltante o ambiguo → te pide que lo subas o que elijas cuál es el correcto.
- Conector de Chrome no conectado → te dice exactamente dónde conectarlo (Settings → Connectors → Chrome) antes de intentar publicar.

Ningún skill de este plugin debería fallar "en silencio" — si algo no anda, tiene que decírtelo con la causa concreta, no inventar un resultado.

## 8. Limitación conocida: publicar todavía necesita una persona presente
`publicar-contenido` no puede adjuntar el archivo de imagen/video por vos — es una restricción de la herramienta de navegador (no puede leer archivos del proyecto), no del plugin. Por eso, cuando llega ese paso, Claude te va a pedir que arrastres el archivo a la ventana del navegador. Por la misma razón, todavía no hay scheduling nativo/desatendido (tipo "publicá esto todos los martes") — si en el futuro se agrega una forma de publicar por API/curl sin ese paso manual, ahí tiene sentido revisar esto de nuevo.

## 9. Agregar un skill nuevo más adelante
El plugin está pensado para crecer sin romper lo que ya funciona:
1. Usá el skill `skill-creator` (viene con Claude Code) para armar el `SKILL.md` nuevo con el formato correcto.
2. Seguí el mismo contrato que ya usan los demás: leer `CLAUDE.md`/`brand.config.json` del proyecto (nunca asumir una marca fija), guardar lo que genere dentro de `<contentRoot>/social/<categoria>/<slug>/...` (`categoria` = `series` o `peliculas`), y si depende de algo externo (software, conector, carpeta), avisar igual que `preparar-entorno` — remitir a ese skill en vez de duplicar los chequeos.
3. Colocalo en `plugin/post-studio/skills/<nombre-nuevo>/SKILL.md`. Si querés que además tenga un atajo de comando, agregá `plugin/post-studio/commands/cmd-<nombre>.md` (mismo prefijo `cmd-`, corto, sin ambigüedad).
4. No hace falta declarar nada en `plugin.json` — los skills y commands se autodescubren por carpeta.
5. Un skill nuevo puede sumarse a un flujo ya existente (ej. un nuevo formato de imagen dentro de `crear-imagen`) o abrir uno propio (ej. soporte para una red nueva) — las dos formas son válidas, seguí el criterio de qué tan relacionado está con lo que ya existe.

## 10. Lo que queda afuera a propósito (roadmap)
- **Scheduling nativo** (cron de Claude): bloqueado hasta que publicar no dependa de arrastrar el archivo a mano — ver sección 8.
- **Theming de marca completo** (más allá del logo + color dominante automático + color manual opcional): hoy alcanza para la mayoría de los casos; una paleta de marca más rica (tipografía, múltiples plantillas visuales) queda para cuando haga falta.
- **Publicar vía API/curl directo** en vez de automatización de navegador: eliminaría la restricción de la sección 8, pero depende de que Zernio/upload-post.com (u otra herramienta) ofrezcan esa vía.
