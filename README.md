# Dispatches from Discharge Hell

Astro blog for catastrophic discharge planning content.

## Tech Stack

- **Framework**: Astro 4.0+
- **Deployment**: Vercel (static output)
- **Content**: Markdown with frontmatter
- **Styling**: Plain CSS (no framework dependencies)

## Project Structure

```
/src
  /pages
    /blog
      /[...slug].astro     # Dynamic blog post routes
      /index.astro         # Blog index
    /about
      /index.astro
    /telos
      /index.astro
    /index.astro           # Homepage
  /content
    /blog                  # Blog posts (Markdown)
      /config.ts           # Content collection schema
package.json
astro.config.mjs
tsconfig.json
vercel.json               # Vercel redirects
```

## Blog Post Format

Create Markdown files in `src/content/blog/` using the naming convention `YYYY-MM-DD-slug.md`:

```markdown
---
title: Post Title
description: Brief description for preview
pubDate: 2026-03-08
tags: ['Dispatches', 'Field Notes', 'The Machine', 'Case Files', 'Persona']
---

# Your content here

Markdown syntax supported.
```

**Available tags**: Dispatches, Field Notes, The Machine, Case Files, Persona

## Local Development

```bash
npm install
npm run dev
```

Open http://localhost:3000 to preview.

## Build for Production

```bash
npm run build
```

Output goes to `dist/` directory.

## Deployment

Connected to Vercel. Push to `main` branch to deploy automatically.

### DNS Configuration

Already configured at Cloudflare:
- A record: @ → 216.198.79.1 (DNS only)
- www → 301 redirect to apex domain

### URL Redirects

`vercel.json` handles 301 redirects for legacy URLs:
- `/about.html` → `/about/`
- `/telos.html` → `/telos/`
- `/blog/posts/YYYY-MM-DD-slug.html` → `/blog/YYYY-MM-DD-slug/`

## Routes

- `/` - Homepage (recent posts)
- `/blog/` - Blog index (all posts)
- `/blog/YYYY-MM-DD-slug/` - Individual post
- `/about/` - About page
- `/telos/` - Telos (mission/goals)

## Adding New Posts

1. Create `src/content/blog/YYYY-MM-DD-slug.md`
2. Add frontmatter with title, description, pubDate, tags
3. Write content in Markdown
4. Push to GitHub → Vercel auto-deploys

## Customization

- **Styling**: Edit `src/pages/*.astro` (inline CSS)
- **Layout**: Modify header/nav/footer in `src/pages/*.astro`
- **Site metadata**: Update title/description in individual pages

---

**Domain**: dispatchesfromdischargehell.com
**Status**: Deployed to Vercel
**Last updated**: 2026-03-08
