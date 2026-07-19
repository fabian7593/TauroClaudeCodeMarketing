# Cómo usar este kit

1. Descomprimí este zip directamente dentro de tu carpeta de proyecto (por ejemplo `TauroTV-Marketing/`). Debe quedar así:

```
TauroTV-Marketing/
├── CLAUDE.md
└── .claude/
    ├── skills/
    │   └── post-instagram/
    │       └── SKILL.md
    └── commands/
        └── post.md
```

2. Abrí esa carpeta como proyecto en Claude Code (Desktop app o terminal).

3. Para generar un post, simplemente escribí en el chat de Claude Code:

```
/post Frieren, anime, drama y fantasía
```

O directamente en lenguaje natural: "Hazme un post de entretenimiento para la serie Frieren."

4. Claude va a preguntar lo que le falte (audios, subtítulos, tipo de post) y te va a entregar el texto, el guion corto (si aplica) y el prompt para Kling AI, todo siguiendo tus reglas de marca automáticamente.

5. Subís el post manualmente a cada red (por ahora) — copiá y pegá.

## Para escalar después (fase 2)
Cuando quieras ir más allá de un solo comando, se pueden crear subagentes especializados (ej. uno que solo revisa que no rompas las reglas de marca antes de publicar, otro que arma el calendario semanal completo). Se agregan como archivos nuevos en `.claude/agents/`. Avisame cuando quieras armar eso y seguimos.
