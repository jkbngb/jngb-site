# jngb.online

Personal site for Jakob Neugebauer. Built with [Astro 4](https://astro.build), deployed on [Azure Static Web Apps](https://azure.microsoft.com/en-us/products/app-service/static).

**Live:** [www.jngb.online](https://www.jngb.online)

## Project Structure

```
site/
├── astro.config.mjs          # Astro config (site URL)
├── tsconfig.json              # TypeScript strict mode
├── package.json               # Single dependency: Astro ^4.16.0
│
├── src/
│   ├── pages/
│   │   ├── index.astro             # Home — profile, bio, links
│   │   ├── notes/
│   │   │   ├── index.astro         # Notes listing (sorted by date)
│   │   │   └── [...slug].astro     # Dynamic note pages from content collection
│   │   ├── lets-talk.astro         # Services & featured projects
│   │   ├── privacy.astro           # Datenschutzerklärung (German privacy policy)
│   │   └── impressum.astro         # Legal impressum (ECG & Mediengesetz)
│   │
│   ├── layouts/
│   │   └── BaseLayout.astro        # Shared HTML wrapper (title, description, activePage)
│   │
│   ├── components/
│   │   ├── Header.astro            # Navigation with active-state detection
│   │   └── Footer.astro            # Copyright, Impressum/Privacy links
│   │
│   ├── content/
│   │   ├── config.ts               # Zod schema for notes collection
│   │   └── notes/                  # Markdown articles
│   │       ├── privacy-first-contract-analysis.md
│   │       └── better-call-saullm.md
│   │
│   ├── styles/
│   │   └── global.css              # Design system, all component styles, responsive rules
│   │
│   └── env.d.ts                    # Astro type references
│
├── public/
│   ├── images/                     # Article screenshots, headshot, diagrams
│   ├── favicon.svg
│   ├── robots.txt
│   └── classification-prompt.txt   # Prompt used in the LLM experiments
│
└── dist/                           # Build output (gitignored)
```

## Design

| Property      | Value                                          |
|---------------|------------------------------------------------|
| Typography    | Inter (sans), JetBrains Mono (mono)            |
| Background    | Warm off-white `#F8F7F4`                       |
| Accent        | Cognac `#8C6239`                               |
| Text          | Dark `#1C1C1C`                                 |
| Max width     | 740px                                          |
| Responsive    | Down to 375px (breakpoint at 600px)            |
| Client JS     | None beyond a single scroll-to-top handler     |

## Development

```bash
npm install
npm run dev           # Dev server at localhost:4321
npm run build         # Static build to dist/
npm run preview       # Preview the build locally
```

## Deployment

The site is hosted on **Azure Static Web Apps** (resource: `<static-web-app>` in resource group `<resource-group>`).

### Prerequisites

- [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) (`az`)
- [SWA CLI](https://azure.github.io/static-web-apps-cli/) (`swa`)
- Access to the `<resource-group>` resource group

### Deploy

```bash
# 1. Build
npm run build

# 2. Get the deployment token (requires Azure CLI login)
az login
TOKEN=$(az staticwebapp secrets list \
  --name <static-web-app> \
  --resource-group <resource-group> \
  --query "properties.apiKey" -o tsv)

# 3. Deploy
swa deploy ./dist --deployment-token "$TOKEN" --env production
```

The site is served at the Azure default hostname and mapped to the custom domain `jngb.online` / `www.jngb.online`.

### Azure Resources

| Resource               | Type                 | Resource Group          |
|------------------------|----------------------|-------------------------|
| `<static-web-app>`         | Static Web App       | `<resource-group>`   |

### Custom Domain

The domain `jngb.online` is mapped to the Static Web App. DNS configuration points to `<azure-hostname>`.

## Content

Articles live in `src/content/notes/` as Markdown files with YAML frontmatter:

```yaml
---
title: "Article Title"
summary: "HTML-enabled summary shown on the notes listing page."
date: "March 2026"
tags: ["local-llm", "privacy"]          # optional
stack: ["Python", "Ollama", "vLLM"]     # optional, shown as tech tags
---
```

To add a new note, create a `.md` file in `src/content/notes/`. Astro's content collection picks it up automatically via the dynamic `[...slug].astro` route.

## Git & GitHub

- **Repository:** [github.com/jkbngb/jngb-site](https://github.com/jkbngb/jngb-site)
- **Branch:** `main` (single-branch workflow)
- **No CI/CD pipeline** — deployment is manual via SWA CLI
