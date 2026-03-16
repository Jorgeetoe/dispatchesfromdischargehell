# Notion Integration Prep

This document is aligned to the canonical build spec in [build-spec.md](/Users/jorgearenivar/dispatchesfromdischargehell-chirpy/docs/build-spec.md) and the Mar 15, 2026 planning direction for:

- Jekyll
- GitHub Pages
- Notion as CMS via API bridge
- this repo as the deployment target

The immediate target is Phase 2 from the spec:

- build `scripts/notion-sync.py`
- sync published article pages from Notion into `_posts/`
- keep Git and GitHub Pages as the publishing chain

## Source of truth

Per the build spec:

- Notion is the editorial and CMS source of truth for published article content
- this repo remains the deployment source of truth
- Git history remains mandatory for safety and rollback

That means the sync flow should be:

1. Notion page is marked ready/published
2. sync script pulls content
3. Markdown is generated into `_posts/`
4. changes are committed and pushed
5. GitHub Pages deploys

## Notion database and filters

Database:

- `Master Content Pipeline (Dispatches HQ)`

Pull only rows where:

- `Content Status = Published`
- `Content Type = Article`

## Exact Notion property mapping

These are the property names from the build spec and should be treated as canonical unless Jorge says otherwise.

| Notion Property | Type | Jekyll field / usage |
| --- | --- | --- |
| `Content Title` | title | `title` |
| `Content Status` | status | filter only |
| `Content Type` | select | filter only |
| `Content Category` | multi_select | map to Jekyll category slug |
| `Publication Date` | date | `date` |
| `Content Summary` | text | `description` / excerpt source |
| `SEO Keywords` | text | `keywords` |
| `last_edited_time` | system | incremental sync |

## Category mapping

Map the first matching Notion category to the site's public category slug:

| Notion Category | Site Category |
| --- | --- |
| `Satirical` | `dispatches` |
| `Educational` | `field-notes` |
| `Caregiver Resource` | `field-notes` |
| `Policy Analysis` | `the-machine` |
| `Clinical Insight` | `the-machine` |
| `Personal Reflection` | `persona` |
| default | `dispatches` |

Important repo note:

- this Chirpy repo currently uses `categories: [slug]` in front matter, not `category: slug`
- the Notion sync should therefore emit `categories: [mapped-slug]` to stay consistent with the current site

## Target output

Generated files should land in:

- `_posts/YYYY-MM-DD-slug.md`

Recommended generated front matter for this repo:

```yaml
---
layout: post
title: "Post title"
date: 2026-03-15
categories: [field-notes]
description: >-
  Summary text here
keywords: keyword one, keyword two
toc: true
---
```

If the spec later requires extra fields such as `redirect_from`, `notes`, `image`, or `excerpt`, those can be added as long as they remain compatible with the current site.

## Content conversion rules

The sync script should convert Notion page blocks into Markdown compatible with Jekyll/Chirpy.

Required block coverage:

- paragraph
- heading_1 -> `##`
- heading_2 -> `###`
- heading_3 -> `####`
- bulleted lists
- numbered lists
- quote
- code fences
- callout
- divider
- toggle
- image

Rich text support should preserve:

- bold
- italic
- strikethrough
- inline code
- links

## Image handling

This is the most important reliability rule from the build spec:

- Notion file URLs expire
- the sync script must download images locally before publish

Target pattern:

- save into `assets/img/posts/{slug}/`
- rewrite Markdown image links to local site paths
- if download fails, do not skip the post; emit a warning and keep the sync moving

## Incremental sync rules

Use `.last_sync` as the local checkpoint file.

Behavior:

- first run: sync all eligible published article pages
- later runs: sync only items whose `last_edited_time` is newer than the checkpoint
- after a successful run: update `.last_sync`

Safety rule:

- if content is unpublished in Notion later, do not auto-delete the local post file
- log it for manual review instead

## Operational modes

The script should support:

- `--dry-run`
- normal sync

`--dry-run` should:

- query Notion
- show which posts would be created or updated
- preview generated front matter
- avoid file writes and Git changes

## Environment and secrets

Expected local env file:

```dotenv
NOTION_API_KEY=...
NOTION_DATABASE_ID=...
```

Expected Python dependencies:

```text
notion-client>=2.0.0
requests>=2.28.0
python-dotenv>=1.0.0
```

Expected GitHub secrets:

- `NOTION_API_KEY`
- `NOTION_DATABASE_ID`

## Automation posture

The spec says:

- build a GitHub Actions workflow for Notion sync
- enable `workflow_dispatch` first
- do not enable cron until testing is complete

That is the right rollout order here too.

## Recommendation

Build in this order:

1. local `scripts/notion-sync.py`
2. dry-run validation
3. write a few posts into `_posts/`
4. verify rendered output locally
5. add manual GitHub Action trigger
6. only later consider scheduled sync

## Reference docs

- [Canonical build spec](/Users/jorgearenivar/dispatchesfromdischargehell-chirpy/docs/build-spec.md)
- [Editorial audit](/Users/jorgearenivar/dispatchesfromdischargehell-chirpy/docs/editorial-audit.md)
- [Custom domain cutover](/Users/jorgearenivar/dispatchesfromdischargehell-chirpy/docs/custom-domain-cutover.md)
- [Notion API guide](https://developers.notion.com/docs/create-a-notion-integration)
- [Notion 2025-09-03 upgrade guide](https://developers.notion.com/docs/upgrade-guide-2025-09-03)
- [Notion webhooks reference](https://developers.notion.com/reference/webhooks)
