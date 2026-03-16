# Build Spec

Canonical spec for this repo as of Mar 16, 2026.

This file is the primary implementation spec going forward.

## Core direction

- Platform: Jekyll
- Theme base: `jekyll-theme-chirpy`
- Hosting: GitHub Pages
- Deployment: Git push -> GitHub Actions -> GitHub Pages
- CMS direction: Notion via API bridge
- Publishing source of truth: this Git repo
- Domain strategy:
  - staging: `https://jorgeetoe.github.io/dispatchesfromdischargehell/`
  - future production: `https://dispatchesfromdischargehell.com/`

## Non-negotiables

- Preserve the current Chirpy-based site structure unless Jorge explicitly requests a redesign.
- Do not replace the theme with a custom hand-built Jekyll architecture.
- Keep URL stability and existing redirects intact.
- Keep Git as the audit trail and rollback mechanism.
- Keep Notion integrated through a bridge, not as a direct live renderer.

## Current repo structure

This repo uses the existing Chirpy conventions, not the earlier hypothetical custom structure.

Key paths:

- `_config.yml`
- `_config.production.yml`
- `_posts/`
- `_tabs/`
- `_layouts/`
- `_data/`
- `assets/`
- `tools/`
- `scripts/`
- `.github/workflows/`

Important implementation note:

- static pages live in `_tabs/`, not `_pages/`
- the site currently uses `Start Here`, `About`, `Telos`, `Categories`, `Tags`, and `Archives`
- current navigation, layout rhythm, and theme behavior are preserved

## Content model

Posts live in:

- `_posts/YYYY-MM-DD-slug.md`

Current front matter conventions:

```yaml
---
layout: post
title: "Post title"
date: 2026-03-15
categories: [field-notes]
description: "Meta description"
redirect_from:
  - /blog/posts/2026-03-15-post-title.html
toc: true
---
```

Notes support now exists for research-backed posts:

```yaml
notes:
  - "Source note one"
  - "Source note two"
```

## Taxonomy

Current public categories:

- `dispatches`
- `field-notes`
- `the-machine`
- `when-it-breaks`
- `persona`

Current rule:

- one effective public category per post
- represented in this repo as `categories: [slug]`

## URL structure

Current permalink target:

- posts: `/blog/posts/YYYY-MM-DD-slug/`

Current behavior to preserve:

- legacy `.html` post URLs redirect to the slash URL
- staging uses `baseurl: /dispatchesfromdischargehell`
- production override clears `baseurl`

## SEO and metadata

Already in place and should be preserved:

- canonical URLs
- sitemap
- feed
- social preview images
- per-post `og:image` support
- working redirect pages
- nonblank page titles

Current SEO direction:

- use `notes:` on research-heavy evergreen posts
- keep evergreen intros and excerpts sharp
- improve trust and clarity through content structure rather than template cloning

## Notion bridge

This is the current implementation target.

### Goal

Build a bridge that pulls published articles from Notion into `_posts/` while preserving this repo's current conventions.

### Inputs

Use the Master Content Pipeline in Notion.

Exact properties to support:

- `Content Title`
- `Content Status`
- `Content Type`
- `Content Category`
- `Publication Date`
- `Content Summary`
- `SEO Keywords`
- `last_edited_time`

### Filters

Sync only pages where:

- `Content Status = Published`
- `Content Type = Article`

### Category mapping

Map Notion categories into the current site categories:

- `Satirical` -> `dispatches`
- `Educational` -> `field-notes`
- `Caregiver Resource` -> `field-notes`
- `Policy Analysis` -> `the-machine`
- `Clinical Insight` -> `the-machine`
- `Personal Reflection` -> `persona`
- default -> `dispatches`

### Output

The bridge should emit Markdown posts into `_posts/` using current repo conventions:

- `layout: post`
- `categories: [slug]`
- `description`
- `keywords` when available
- `toc: true`
- `redirect_from` using the old `.html` form

### Image handling

Notion file URLs expire, so the bridge must:

1. download images locally
2. save them under `assets/img/posts/{slug}/`
3. rewrite Markdown to local image paths
4. continue syncing even if an image download fails

### Sync behavior

- support dry-run mode
- support incremental sync via `.last_sync`
- do not auto-delete posts if content is unpublished in Notion
- do overwrite synced content when a published page changes

### Workflow direction

Local script:

- `scripts/notion-sync.py`

Dependencies:

- `requirements.txt`
- `.env.example`

GitHub Actions:

- manual trigger first via `workflow_dispatch`
- scheduled sync only after manual testing is stable

## Custom domain strategy

The repo is already prepared for the future domain cutover.

Use:

- `_config.yml` for staging
- `_config.production.yml` for production

The Pages workflow should continue to:

- build staging normally now
- switch to production-domain config when a root `CNAME` is added

## Visual direction

Preserve the current site presentation.

What that means in practice:

- keep Chirpy as the visual base
- keep current page chrome and nav structure unless Jorge explicitly asks otherwise
- borrow editorial patterns from reference sites only at the content level
- avoid template changes unless clearly requested

## Explicitly not part of the current direction

These were part of earlier planning but are not the current default direction:

- replacing Chirpy with a fully custom Jekyll layout system
- moving static pages into `_pages/`
- introducing a `/welcome/` page by default
- redesigning nav to match another site
- rebuilding the homepage template from scratch

Any of those can still happen later, but only as explicit design decisions.

## Immediate priority

Current priority is Phase 2:

- finish and validate the Notion bridge
- test against a small set of published posts
- verify output, metadata, images, and deploy behavior
