# Graph Report - .  (2026-07-21)

## Corpus Check
- Large corpus: 46 files · ~888,060 words. Semantic extraction will be expensive (many Claude tokens). Consider running on a subfolder.

## Summary
- 35 nodes · 52 edges · 8 communities (5 shown, 3 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 6 edges (avg confidence: 0.92)
- Token cost: 174,877 input · 0 output

## Community Hubs (Navigation)
- Integraciones MCP Externas
- Motor de Imagen del Post
- Comandos y Skills de Posts
- Piezas del Carrusel Digimon
- Reglas de Marca TauroTV
- Estructura Fija de Post
- Post de Obsession
- Coleccion Digimon

## God Nodes (most connected - your core abstractions)
1. `post-template.html (plantilla canónica)` - 10 edges
2. `post-instagram skill` - 9 edges
3. `CLAUDE.md — Contexto de Marca TauroTV` - 8 edges
4. `digimon/post.txt (caption del carrusel)` - 7 edges
5. `post-image skill` - 6 edges
6. `/post command` - 5 edges
7. `MCP-SETUP.md — conexión de herramientas externas` - 4 edges
8. `CTA fijo de cierre` - 4 edges
9. `Estructura fija de post (6 pasos)` - 4 edges
10. `kling-motion-prompt skill` - 3 edges

## Surprising Connections (you probably didn't know these)
- `post-instagram skill` --references--> `Regla de dispositivos compatibles / no-cast`  [EXTRACTED]
  .claude/skills/post-instagram/SKILL.md → CLAUDE.md
- `digimon/post.txt (caption del carrusel)` --conceptually_related_to--> `Estructura fija de post (6 pasos)`  [INFERRED]
  POST/social/digimon/post.txt → CLAUDE.md
- `/post command` --references--> `CLAUDE.md — Contexto de Marca TauroTV`  [EXTRACTED]
  .claude/commands/post.md → CLAUDE.md
- `Color del panel calculado en runtime desde el color dominante (sin PNGs externos)` --rationale_for--> `post-image skill`  [EXTRACTED]
  POST/_template/post-template.html → .claude/skills/post-image/SKILL.md
- `Medir alturas reales en el DOM en vez de adivinar porcentajes` --rationale_for--> `post-image skill`  [EXTRACTED]
  POST/_template/post-template.html → .claude/skills/post-image/SKILL.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Carrusel Digimon (4 imágenes + texto único + hashtags)** — post_social_digimon_01_digimon_adventure_02, post_social_digimon_02_digimon_tamers, post_social_digimon_03_digimon_adventure_2020, post_social_digimon_04_digimon_beatbreak, post_social_digimon_post, post_social_digimon_hashtags, claude_skills_post_carousel_skill [INFERRED 0.85]
- **Pipeline de generación de post simple (comando -> skills -> template)** — claude_commands_post, claude_skills_post_instagram_skill, claude_skills_post_image_skill, post__template_post_template [EXTRACTED 1.00]
- **Stack de MCP recomendado para el pipeline de marketing** — mcp_setup_md_google_drive, mcp_setup_md_figma, mcp_setup_md_kling_ai, mcp_setup_md_blotato [EXTRACTED 1.00]

## Communities (8 total, 3 thin omitted)

### Community 0 - "Integraciones MCP Externas"
Cohesion: 0.29
Nodes (7): /kling-motion command, kling-motion-prompt skill, MCP-SETUP.md — conexión de herramientas externas, Blotato MCP (publicación automática), Figma MCP, Google Drive MCP, Kling AI MCP

### Community 1 - "Motor de Imagen del Post"
Cohesion: 0.47
Nodes (4): post-image skill, post-template.html (plantilla canónica), Color del panel calculado en runtime desde el color dominante (sin PNGs externos), Medir alturas reales en el DOM en vez de adivinar porcentajes

### Community 2 - "Comandos y Skills de Posts"
Cohesion: 0.60
Nodes (5): /post command, /post-carousel command, post-carousel skill, post-instagram skill, LEEME.md — guía de uso del kit

### Community 4 - "Reglas de Marca TauroTV"
Cohesion: 0.50
Nodes (4): CLAUDE.md — Contexto de Marca TauroTV, Mix de contenido 70/20/10, Regla de dispositivos compatibles / no-cast, Planes TauroTV (Basic/Standard/Family)

### Community 5 - "Estructura Fija de Post"
Cohesion: 0.67
Nodes (3): CTA fijo de cierre, Estructura fija de post (6 pasos), obsession/post.txt (caption)

## Knowledge Gaps
- **6 isolated node(s):** `/kling-motion command`, `Mix de contenido 70/20/10`, `Planes TauroTV (Basic/Standard/Family)`, `Google Drive MCP`, `Figma MCP` (+1 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `post-instagram skill` connect `Comandos y Skills de Posts` to `Integraciones MCP Externas`, `Motor de Imagen del Post`, `Reglas de Marca TauroTV`, `Estructura Fija de Post`?**
  _High betweenness centrality (0.456) - this node is a cross-community bridge._
- **Why does `kling-motion-prompt skill` connect `Integraciones MCP Externas` to `Comandos y Skills de Posts`?**
  _High betweenness centrality (0.308) - this node is a cross-community bridge._
- **Why does `post-template.html (plantilla canónica)` connect `Motor de Imagen del Post` to `Piezas del Carrusel Digimon`, `Post de Obsession`?**
  _High betweenness centrality (0.275) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `digimon/post.txt (caption del carrusel)` (e.g. with `01-digimon-adventure-02.html` and `02-digimon-tamers.html`) actually correct?**
  _`digimon/post.txt (caption del carrusel)` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `/kling-motion command`, `Mix de contenido 70/20/10`, `Planes TauroTV (Basic/Standard/Family)` to the rest of the system?**
  _6 weakly-connected nodes found - possible documentation gaps or missing edges._