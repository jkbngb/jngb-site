# Content

Astro [content collections](https://docs.astro.build/en/guides/content-collections/) for structured markdown content.

## Notes

Technical articles in `notes/`. Each `.md` file becomes a page at `/notes/<slug>`.

### Frontmatter schema

```yaml
title: string       # Article title
summary: string     # HTML string shown on the notes index (supports <strong>, <br>)
date: string        # "YYYY-MM" format
tags: string[]      # Categorization (e.g. "local-llm", "pipeline-architecture")
stack: string[]     # Technologies used (e.g. "Python", "Ollama")
```

### Adding a new note

1. Create `src/content/notes/<slug>.md` with the frontmatter above
2. Write the article body in markdown
3. It will automatically appear on `/notes` sorted by date (newest first)

Images referenced in notes go in `public/images/`.
