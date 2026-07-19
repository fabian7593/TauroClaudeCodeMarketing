# Conectar herramientas externas a Claude Code (MCP)

MCP es el protocolo que le permite a Claude Code usar herramientas externas (Figma, Kling AI, Google Drive, Blotato) como si fueran parte de él. Cada una se conecta UNA sola vez y después Claude las usa solo cuando las necesita.

## Google Drive
Servidor oficial de Anthropic. En Claude Code corré:
```
/mcp
```
y seguí el flujo de autenticación para agregar Google Drive. Una vez conectado, Claude puede leer tus documentos de brand/contexto directo desde Drive sin que se los pegues manualmente.

## Figma
Servidor oficial remoto (no necesitás tener Figma Desktop abierto):
```
claude mcp add --transport http figma https://mcp.figma.com/mcp
```
Te va a pedir autenticarte con tu cuenta de Figma la primera vez. Con esto Claude puede leer tus templates y estructura de diseño.

**Importante:** el MCP de Figma está pensado sobre todo para leer datos de diseño (tokens, componentes, texto), no para "rellenar automáticamente la plantilla y exportar el PNG final" en un solo paso — eso normalmente necesita un pequeño script adicional usando la API de exportación de imágenes de Figma. Es viable, pero no es un solo comando mágico. Si querés, lo armamos cuando llegues a esa parte.

## Kling AI
Kling tiene soporte MCP propio. Pasos:
1. Entrá a klingai.com/global/dev y creá una cuenta de desarrollador
2. Sacá tu API key desde el dashboard
3. Agregá el servidor a tu configuración de Claude Desktop (`claude_desktop_config.json`) con esa API key

Con esto Claude puede pedirle videos e imágenes a Kling directamente desde el chat, sin que vos copies y pegues el prompt manualmente.

## Blotato (para publicar automáticamente)
Blotato conecta tus cuentas reales de Facebook, Instagram, TikTok, YouTube, etc. UNA vez desde su plataforma, y después expone eso como una herramienta MCP que Claude puede usar para publicar o programar posts.
```
Servidor: mcp.blotato.com/mcp
```
Tiene prueba gratis de 7 días, y planes desde $29/mes. Ver la sección de "Blotato" en la conversación con Claude para el detalle completo de cómo encaja en tu flujo con Cowork.

## Orden recomendado para conectar
1. Google Drive (gratis, inmediato)
2. Figma (gratis, para leer tus templates)
3. Kling AI (según tu plan de Kling)
4. Blotato (cuando quieras pasar de "generar borradores" a "publicar automático")
