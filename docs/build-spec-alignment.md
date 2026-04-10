# Build Spec Alignment

This file maps the Mar 15, 2026 build spec against the current repo so future work stays honest.

## What already aligns

- Jekyll on GitHub Pages is already in place.
- The repo is already based on Chirpy and deploys through GitHub Actions.
- Posts are already in `_posts/`.
- Static onboarding/about page source files already exist in `_tabs/`; their public routes are `/start-here/`, `/about/`, and `/telos/`.
- Legacy post redirects are already working through `jekyll-redirect-from`.
- SEO basics are already improved: canonical URLs, sitemap, feed, social preview images.
- The site now has reusable post `Notes` support.
- The repo is already prepared for a future custom-domain cutover with `_config.production.yml`.

## What partially aligns

- The build spec assumes a more hand-built Jekyll structure with custom `_layouts/`, `_includes/`, `_pages/`, and CSS files.
- This repo currently preserves the Chirpy structure instead:
  - `_tabs/` instead of `_pages/`
  - theme-driven layouts and navigation
  - Chirpy-provided reading time, TOC, related posts, search hooks, and share UI
- The build spec calls for a simpler nav and a `/welcome/` front door. The current site uses a Chirpy sidebar and a `Start Here` page.

These are not bugs. They are implementation differences.

## What does not align yet

- `scripts/notion-sync.py` does not exist yet.
- `requirements.txt` for the Notion bridge does not exist yet.
- `.env.example` for Notion does not exist yet.
- `.github/workflows/notion-sync.yml` does not exist yet.
- There is no `/welcome/` page with `/start-here/` redirect.
- There is no automated Notion -> Markdown -> GitHub Pages publishing path yet.

## Recommended interpretation

Treat the build spec as the product/operations target and this repo as the implementation reality.

That means:

- keep the existing Chirpy-based structure unless Jorge explicitly asks for a visual/structural redesign
- implement the Notion bridge to fit this repo, not a hypothetical custom Jekyll theme
- preserve working URLs, redirects, and metadata instead of forcing the repo to mirror the spec literally

## Practical decisions for future work

1. Use Notion property names exactly as given in the build spec.
2. Emit front matter that matches this repo's current conventions.
3. Avoid template or navigation rewrites unless explicitly requested.
4. Build the Notion bridge first; revisit `/welcome/` and nav simplification later as separate decisions.
