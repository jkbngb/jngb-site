# jngb.online

Personal site for Jakob Neugebauer. Built with [Astro 4](https://astro.build), deployed on [Azure Static Web Apps](https://azure.microsoft.com/en-us/products/app-service/static).

**Live:** [www.jngb.online](https://www.jngb.online)

## Structure

```
src/
  pages/          # Astro pages (routes)
  components/     # Header, Footer
  layouts/        # BaseLayout wrapper
  content/        # Markdown content collection (notes/articles)
  styles/         # Global CSS (design system)
public/           # Static assets (images, favicon, robots.txt)
```

Three sections: **Home** (`/`), **Notes** (`/notes`), **Let's Talk** (`/lets-talk`).

## Development

```bash
npm install
npm run dev       # Dev server at localhost:4321
npm run build     # Static build to dist/
npm run preview   # Preview the build locally
```

## Deployment

Static build deployed via the [SWA CLI](https://azure.github.io/static-web-apps-cli/):

```bash
npm run build
swa deploy ./dist --deployment-token <TOKEN> --env production
```

## Design

- Typography: Inter (sans), JetBrains Mono (mono)
- Palette: warm off-white (`#F8F7F4`), cognac accent (`#8C6239`), dark text (`#1C1C1C`)
- No JavaScript frameworks, no client-side JS beyond a single scroll-to-top handler
- Responsive down to 375px
