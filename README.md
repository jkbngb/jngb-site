# jngb.online

The personal site of Jakob Neugebauer — independent builder of AI systems and data
infrastructure, based in Vienna.

**Live:** [jngb.online](https://jngb.online)

The interesting part is the [Notes](https://jngb.online/notes): first-person write-ups of
real experiments — a MacBook Air against rented H100s, with the exact bills, runtimes, and
failures left in. No tutorials, no hot takes. Real numbers or it didn't happen.

## Stack

A deliberately small static site. One dependency.

- [Astro 4](https://astro.build) — static output, Markdown content collections, no UI framework
- Plain CSS, a few lines of vanilla JS (a scroll-to-top handler and a table-of-contents builder)
- TypeScript in strict mode

## Structure

```
src/
├── pages/
│   ├── index.astro            # Home — profile and intro
│   ├── notes/
│   │   ├── index.astro        # Notes listing (newest first)
│   │   └── [...slug].astro     # A page per Markdown note
│   ├── lets-talk.astro        # Services and featured work
│   ├── impressum.astro        # Legal notice (Austrian ECG / Mediengesetz)
│   └── privacy.astro          # Datenschutzerklärung
├── layouts/BaseLayout.astro   # Shared HTML shell
├── components/                # Header, Footer
├── content/
│   ├── config.ts              # Zod schema for the notes collection
│   └── notes/                 # The articles, as 01-…, 02-…, Markdown
└── styles/global.css          # The entire design system

public/                        # Static assets served as-is
├── images/articles/<nn-slug>/ # Screenshots and diagrams, one folder per note
├── images/site/               # Site chrome (headshot, etc.)
├── reg-radar/                 # Standalone interactive demo (Regulation Radar)
├── data/                      # Datasets backing the demos
└── *.txt                      # The exact prompts used in the experiments
```

## Development

```bash
npm install
npm run dev        # http://localhost:4321
npm run build      # static build to dist/
npm run preview    # serve the build locally
```

## Adding a note

Drop a Markdown file into `src/content/notes/` (named `NN-slug.md`). The frontmatter:

```yaml
---
title: "Hook: Plain descriptive subtitle"
summary: "Teaser shown on the listing page. HTML allowed."
date: "March 2026"
tags: ["local-llm", "privacy"]        # optional
stack: ["Astro", "Llama:8B", "vLLM"]  # optional, rendered as tags
---
```

Astro's content collection picks it up automatically; the slug is the filename.

## Deployment

`npm run build` produces a fully static `dist/`, deployed to Azure Static Web Apps behind the
custom domain. No CI pipeline — deploys are manual.

## License

Code is MIT (see [LICENSE](LICENSE)). The article text and images are © Jakob Neugebauer,
all rights reserved.
