# jngb.online

Personal website of Jakob Neugebauer. A static site built with Astro.

Live at https://jngb.online

## What it is

A small personal site. Pages:

- Home: short profile and intro.
- Notes: write-ups of personal AI and LLM experiments, each with the setup, results, and costs.
- Let's Talk: services and selected projects.
- Impressum and Privacy: Austrian legal pages.

## Stack

- Astro 4 (static output, Markdown content collections)
- Plain CSS, with a small amount of vanilla JavaScript
- TypeScript (strict mode)
- One runtime dependency: astro

## Structure

```
src/
  pages/
    index.astro          Home
    notes/
      index.astro        Notes listing
      [...slug].astro    One page per note
    lets-talk.astro      Services and projects
    impressum.astro      Legal notice
    privacy.astro        Privacy policy
  layouts/BaseLayout.astro
  components/            Header, Footer
  content/
    config.ts            Schema for the notes collection
    notes/               The articles, as Markdown (01-..., 02-..., ...)
  styles/global.css      Styles for the whole site

public/
  images/articles/<nn-slug>/   Images per note
  images/site/                 Site images (headshot, etc.)
  reg-radar/                   Standalone interactive demo
  data/                        Datasets for the demos
  *.txt                        Prompts used in the experiments
  favicon.svg, robots.txt
```

## Development

```bash
npm install
npm run dev        # http://localhost:4321
npm run build      # static build to dist/
npm run preview    # serve the build locally
```

## Hosting and deployment

Hosted on Azure Static Web Apps, with the custom domain jngb.online.
`npm run build` produces a static `dist/`, which is deployed manually. There is no CI pipeline.

## Adding a note

Add a Markdown file to `src/content/notes/` named `NN-slug.md`. Frontmatter:

```yaml
---
title: "Title"
summary: "Teaser shown on the listing page. HTML allowed."
date: "March 2026"
tags: ["tag1", "tag2"]          # optional
stack: ["Astro", "vLLM"]        # optional, shown as tags
---
```

The slug is the filename. Astro's content collection picks the file up automatically.

## Reading and reuse

Code is MIT (see LICENSE).

The writing is licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Quote it, excerpt it, argue with it –
that is what it is for. The single condition is attribution: name the author
and link to the original. Reproducing a piece wholesale, or running the text
out under someone else's byline, is not covered.
