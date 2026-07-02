# Build Spec — Jekyll + GitHub Pages + Notion CMS (Canonical)

> 🎯 **Purpose:** Canonical build spec for Dispatches from Discharge Hell. This Notion page and `docs/build-spec.md` in the repo are the two authoritative sources. When they conflict, reconcile — do not assume either is stale without checking.

> 📌 **Current Implementation Direction (Mar 16, 2026)**
>
> - **Static site generator:** Jekyll on GitHub Pages
> - **Theme base:** `jekyll-theme-chirpy` (v7.5.0, gem-based)
> - **CMS:** Notion via API bridge (`scripts/notion-sync.py`)
> - **Source of truth for publishing:** Git repo
> - **Staging domain:** `https://jorgeetoe.github.io/dispatchesfromdischargehell/`
> - **Future production domain:** `https://dispatchesfromdischargehell.com/`

> 📋 **Progress — Mar 16, 2026**
>
> - ✅ Phase 0: Scaffold — Chirpy installed from `chirpy-starter`, configured, Ruby 3.2.0 via rbenv
> - ✅ Phase 1: Content Migration — 24 posts in `_posts/`, static pages in `_tabs/` (About, Telos, Start Here)
> - ✅ Phase 3: Deploy — Force-pushed to GitHub, GitHub Actions building, site live at staging URL
> - ✅ Visual fixes — Homepage post cards, avatar, "When It Breaks" category, favicon, copyright, dark/light toggle
> - ✅ Notion integration created, `.env` configured, credentials validated
> - ✅ Dry run successful — 25 published articles found (24 + "Flex for Me, Not for Thee" after Publication Date fix)
> - ✅ Repo Slug property added to Content Pipeline — 17 matched posts populated via Notion API
> - ✅ `notion-sync.py` updated — reads `Repo Slug`, falls back to generated slug, supports targeted test + `--no-state-update`
> - ✅ Controlled write test PASSED — 3 existing files overwritten correctly, 2 new files created, repo-only front matter preserved, `jekyll build` passes
> - ✅ Phase 5: Full local write — 25 Notion-synced posts written, 1 orphan deleted, 6 repo-only posts retained, `jekyll build` passes
> - ✅ Committed and pushed — full sync live on staging
> - ✅ Import 6 repo-only orphans into Notion — 31 Published Articles confirmed, commit `8d7e691` pushed
> - ✅ Sync safeguard added — metadata-only Notion pages preserve existing Markdown bodies
> - ✅ Verify staging site — all 31 posts return 200, nav works, 4 of 5 categories confirmed
> - ✅ `categories/when-it-breaks/` resolves in Chirpy; the public category exists in the site taxonomy
> - 🔶 Sync `docs/build-spec.md` — blocked: Build Spec page not shared with Jekyll Sync integration
> - ⬜ Phase 6: Slash Commands
> **Immediate priority:** Verify staging site → DNS cutover → email subscribe form.

---

## Why This Stack

- **Jekyll is GitHub Pages' native engine.** Zero build config. Push markdown, site builds automatically.
- **Chirpy is a mature, maintained theme.** Provides dark mode, TOC, categories, tags, archives, search, and responsive layout out of the box. No need to hand-build these.
- **24 posts already exist as Markdown.** Minimal front matter tweaks needed for Chirpy conventions.
- **Notion is already the CMS.** The Master Content Pipeline database has structured properties. The API bridge formalizes what's already happening manually.
- **Git version history** prevents another incident where changes can't be rolled back.
- **Free hosting.** GitHub Pages is free for public repos. Custom domain with HTTPS included.
---

## What Happened Before (Context)

| Attempt | What broke | What we keep |
| --- | --- | --- |
| **Static HTML + Hostinger + FTP** | Doesn't scale. No shared templates. FTP flaky. | Original design, typography, color palette |
| **Hugo + Cloudflare Pages** | Devin suggestions broke visual balance. No Git history to roll back. | 46 Markdown posts with YAML front matter |
| **WordPress + Hostinger + Kadence** | Not built. Adds maintenance overhead (PHP, MySQL, plugins, security). | Category taxonomy, URL structure, redirect map |
| **Jekyll + GitHub Pages + Notion CMS** | *This is the current plan.* | Everything above, minus the complexity |

---

## Site Architecture

### Platform

- **Static site generator:** Jekyll
- **Theme:** `jekyll-theme-chirpy` v7.5.0 (gem-based via `chirpy-starter`)
- **Hosting:** GitHub Pages (free)
- **Deployment:** `git push` to GitHub → GitHub Actions builds and deploys
- **CMS:** Notion (via API bridge script)
- **Staging domain:** `https://jorgeetoe.github.io/dispatchesfromdischargehell/`
- **Production domain:** `https://dispatchesfromdischargehell.com/` (pending DNS cutover)
### Repository Structure (Actual)

```javascript
dispatchesfromdischargehell/
├── _config.yml                    # Jekyll + Chirpy config (staging)
├── _config.production.yml         # Production overrides (clears baseurl)
├── _posts/                        # Blog posts (Markdown)
│   └── YYYY-MM-DD-slug.md
├── _tabs/                         # Static pages (Chirpy convention)
│   ├── about.md                   # About page
│   ├── telos.md                   # Telos page
│   ├── start-here.md              # Start Here page
│   ├── categories.md              # Category index
│   ├── tags.md                    # Tag index
│   └── archives.md                # Archives page
├── _layouts/                      # Layout overrides (only if customizing Chirpy)
├── _data/                         # Site data files
├── assets/                        # Images, CSS overrides, favicons
│   └── img/
│       └── posts/                 # Post images (synced from Notion)
├── scripts/
│   └── notion-sync.py             # Notion API → Markdown bridge
├── tools/                         # Chirpy build tools
├── docs/                          # Project documentation
│   ├── build-spec.md              # Canonical repo spec (mirrors this page)
│   ├── notion-integration-prep.md # Notion bridge planning
│   ├── build-spec-alignment.md    # Spec alignment notes
│   ├── editorial-audit.md         # Content audit
│   └── custom-domain-cutover.md   # DNS cutover plan
├── .github/
│   └── workflows/
│       ├── pages-deploy.yml       # Chirpy GitHub Pages deploy
│       └── notion-sync.yml        # Notion sync (manual trigger)
├── CNAME                          # Custom domain (added when ready)
├── requirements.txt               # Python deps for notion-sync
├── .env.example                   # Environment variable template
└── CLAUDE.md                      # Claude Code project context
```

**Key Chirpy conventions:**

- Static pages live in `_tabs/`, not `_pages/`
- Current nav pages: Start Here, About, Telos, Categories, Tags, Archives
- Theme layouts and includes come from the gem — only override in `_layouts/` or `_includes/` when necessary
- Chirpy provides dark mode, TOC, search, and responsive layout automatically
---

## Content Taxonomy

### Categories

| Category | Slug | Description |
| --- | --- | --- |
| Dispatches | `dispatches` | Satirical/dark humor about system absurdity |
| Field Notes | `field-notes` | Educational, practical content for families |
| The Machine | `the-machine` | Institutional mechanics, payer games, system analysis |
| When It Breaks | `when-it-breaks` | De-identified pattern stories from 20 years |
| Persona | `persona` | Off-duty reflections |

### Category Rules

- **One effective public category per post** — represented as `categories: [slug]` in front matter
- Revisit multi-category assignment around 150–200 posts
- "When It Breaks" replaces the more clinical-sounding "Case Files" in public-facing nav
- Tags can be added later if needed
---

## Content and Front Matter Conventions

### Standard Post Front Matter

```yaml
---
layout: post
title: "Post title"
date: 2026-03-15
categories: [field-notes]
description: "Meta description"
keywords: "comma, separated, keywords"
redirect_from:
> - /blog/posts/2026-03-15-post-title.html
toc: true
---
```

### Optional Front Matter

```yaml
notes:
> - "Source note one"
> - "Source note two"
```

---

## URL Structure

### Current Implementation

- **Posts:** `/blog/posts/YYYY-MM-DD-slug/`
- **Legacy **`.html`** URLs:** redirect to slash URLs via `redirect_from` in front matter
- **Staging:** uses `/dispatchesfromdischargehell` as `baseurl`
- **Production:** `_config.production.yml` clears `baseurl` for root domain
### Config Files

- **`_config.yml`** — staging config with `baseurl: /dispatchesfromdischargehell`
- **`_config.production.yml`** — production overrides, clears baseurl
- Pages workflow switches to production config when a root CNAME is added
---

## Notion CMS Bridge (The Core New Piece)

### Write Test Results (Mar 16, 2026)

> 🧪 **5-post controlled write test completed.** All 5 outputs were **new files**, not overwrites of existing posts. This confirms the filename mismatch risk: Notion-generated filenames differ from existing repo filenames for most posts.

**Test posts and results:**

| Notion Post | Notion Output Filename | Existing Repo Filename | Mismatches |
| --- | --- | --- | --- |
| Series Intro | `2025-01-01-dispatches-from-discharge-hell-a-25-part-series-on-the-patterns-nobody-warns-you-about.md` | `2024-01-01-dispatches-from-discharge-hell-25-part-series.md` | Date, slug, category |
| Home Health Illusion (Part 5) | `2026-02-22-dispatches-from-discharge-hell-part-5-the-home-health-illusion.md` | `2024-01-15-home-health-illusion-part-5.md` | Date, title format, slug, category |
| The P2P Playbook™ | `2026-02-15-the-p2p-playbooktm-your-professional-guide-to-medical-gaslighting.md` | `2025-09-01-the-p2p-playbook-launch.md` (not same post) | Date, slug (different post entirely) |
| She Knew and She Didn't Say Anything | `2026-02-26-she-knew-and-she-didnt-say-anything-when-payer-case-managers-weaponize-silence.md` | *(no existing counterpart)* | New post — no conflict |
| Flex for Me, Not for Thee | `2026-02-21-flex-for-me-not-for-thee.md` | `2026-01-03-flex-for-me-not-for-thee.md` | Date differs |

**Other observations:**

- `to_do` blocks preserved as HTML comments with warnings ✅
- Repo-only front matter keys (`notes:`, `excerpt:`) preserved during sync ✅
- Targeted test mode added to `scripts/notion-sync.py` (sync selected pages, skip state updates)
**⚠️ Decision needed before full sync:**

The Notion bridge generates filenames from `Publication Date` + `Content Title`. The existing repo posts were created with different dates, shorter slugs, and sometimes different categories. A full sync would create **duplicate posts** (new Notion-generated files alongside old repo files) rather than overwriting.

**Decision: Option 3 — **`Repo Slug`** override property (IMPLEMENTED & VERIFIED)**

A `Repo Slug` text property has been added to the Master Content Pipeline in Notion. 17 of 25 published posts matched to existing repo files and were populated via Notion API. When set, the sync script uses this value as the output filename stem instead of generating one from `Publication Date` + `Content Title`. Format: `YYYY-MM-DD-slug` (no `.md` extension). 8 posts with no existing repo counterpart were left blank — the script generates normally.

**Phase 2–4 Controlled Write Results (Mar 16, 2026):**

✅ **Overwrote existing tracked files (Repo Slug working):**

- `_posts/2024-01-01-dispatches-from-discharge-hell-25-part-series.md` (Series Intro)
- `_posts/2024-01-15-home-health-illusion-part-5.md` (Part 5)
- `_posts/2026-01-03-flex-for-me-not-for-thee.md`
✅ **Created new files as expected (no Repo Slug):**

- `_posts/2026-02-15-the-p2p-playbooktm-your-professional-guide-to-medical-gaslighting.md`
- `_posts/2026-02-26-she-knew-and-she-didnt-say-anything-when-payer-case-managers-weaponize-silence.md`
**Diff:** 3 files changed, 98 insertions, 87 deletions. 2 new files.

**Preserved repo-only front matter:** `excerpt:`, `image:`, `notes:` all retained.

**`redirect_from`** now follows the overridden repo slug on mapped files.

**`to_do`** blocks** in P2P Playbook™ preserved as HTML comments per spec.

**`jekyll build`** passes locally.

**Phase 5 Full Sync Results (Mar 16, 2026):**

✅ **25 Notion-managed posts written to **`_posts/`**:**

- 17 existing files modified (Repo Slug overwrites)
- 8 new files created (auto-generated slugs)
- Diff: 17 files changed, 465 insertions, 519 deletions
- No Notion image downloads triggered (no image blocks in these posts)
- `to_do` block warnings on P2P Playbook™ only (known, preserved as HTML comments)
- `jekyll build` passes locally
✅ **Orphan cleanup:**

- Deleted: `_posts/2025-09-01-the-p2p-playbook-launch.md` (confirmed not a counterpart to any Notion post)
- 6 repo-only posts retained pending Jorge’s review:
> - `2017-11-15-the-book-i-picked-up-as-a-joke-that-rewired-my-entire-life.md`
> - `2025-03-16-preadmission-guidelines-vip-ticket-rehab-reality-show.md`
> - `2025-03-19-when-sarcasm-and-humor-is-the-best-medicine.md`
> - `2025-09-03-moneyball-for-medical-necessity.md`
> - `2026-02-15-rehabilitation-vs-catastrophic-care.md`
> - `2026-02-15-what-doc-rehab-actually-does.md`

**Next steps:**

1. ~~Jorge reviews local output~~ ✅
1. ~~`git add . && git commit && git push`~~ ✅
1. Verify staging site at `https://jorgeetoe.github.io/dispatchesfromdischargehell/`
1. ~~Decide on 6 repo-only orphans~~ → **Import into Notion** (see Codex instructions below)
1. DNS cutover when ready
---

### How It Works

1. A Python script (`scripts/notion-sync.py`) queries the Notion API
1. It pulls posts from the Master Content Pipeline where `Content Status` = "Published" AND `Content Type` in ("Article", "Caregiver Resource")
1. It converts Notion blocks to Jekyll-compatible Markdown with YAML front matter
1. It writes files to `_posts/`
1. It commits and pushes to GitHub
1. GitHub Actions builds and deploys the site
### Notion API Source

**Database:** Master Content Pipeline (Dispatches HQ)

**Property mapping (exact Notion field names):**

| Notion Property | Type | Maps To | Jekyll Front Matter |
| --- | --- | --- | --- |
| `Content Title` | title | Post title | `title` |
| `Content Status` | status | Filter (= "Published") | — |
| `Content Type` | select | Filter (= "Article") | — |
| `Content Category` | multi_select | Category label | `categories: [slug]` |
| `Publication Date` | date | Post date | `date` |
| `Content Summary` | text | Meta description | `description` |
| `SEO Keywords` | text | Comma-separated keywords | `keywords` |
| `Repo Slug` | text | Filename override | — (controls output filename only) |
| `last_edited_time` | system | Incremental sync check | — |

### Category Mapping (Notion → Jekyll)

Map using **first match** in this priority order:

| Notion Content Category | Jekyll Category Slug |
| --- | --- |
| Satirical | `dispatches` |
| Educational | `field-notes` |
| Caregiver Resource | `field-notes` |
| Policy Analysis | `the-machine` |
| Clinical Insight | `the-machine` |
| Personal Reflection | `persona` |
| *(default if none match)* | `dispatches` |

### Output Expectations (Current Repo Conventions)

The sync script must emit files that match the current repo conventions:

- Output into `_posts/`
- Include `layout: post`
- Emit `categories: [slug]` (array with single slug)
- Include `description` from Content Summary
- Include `keywords` when available from SEO Keywords
- Include `toc: true`
- Include `redirect_from` using old `.html` form: `/blog/posts/YYYY-MM-DD-slug.html`
### Jekyll Front Matter Template

```yaml
---
layout: post
title: "{Content Title}"
date: {Publication Date}
categories: [{mapped category slug}]
description: >-
  {Content Summary — first 160 chars if longer}
keywords: "{SEO Keywords}"
toc: true
redirect_from:
> - /blog/posts/{Publication Date}-{slug}.html
---
```

### Slug Generation

**If **`Repo Slug`** is set:** use it directly as the filename stem. Output: `_posts/{Repo Slug}.md`

**If **`Repo Slug`** is empty:** generate from `Content Title`:

- Lowercase, replace spaces with hyphens, remove special characters except hyphens
- Example: "The Family Readiness Mismatch" → `the-family-readiness-mismatch`
- Filename: `_posts/{Publication Date}-{slug}.md`
### Notion Block → Markdown Conversion

| Notion Block | Markdown Output |
| --- | --- |
| paragraph | Plain text with blank line after |
| heading_1 | `##` (H2 — H1 is reserved for title) |
| heading_2 | `###` |
| heading_3 | `####` |
| bulleted_list_item | `  • item` (indent children with 2 spaces) |
| numbered_list_item | `1. item` (indent children with 3 spaces) |
| quote | `> text` |
| code | Fenced code block with language |
| callout | `> emoji text` (blockquote with emoji prefix) |
| divider | `---` |
| toggle | `<details><summary>title</summary>content</details>` |
| image | `![caption](local_path)` — download image first |

**Rich text formatting:**

| Notion Annotation | Markdown Output |
| --- | --- |
| bold | `**text**` |
| italic | `*text*` |
| strikethrough | `~~text~~` |
| code | `text` |
| link | `[text](url)` |

### Image Handling

**Notion image URLs expire after ~1 hour.** The sync script MUST:

1. Detect image blocks in page content
1. Download the image file to `assets/img/posts/{slug}/`
1. Replace the Notion URL with `/assets/img/posts/{slug}/{filename}` in the Markdown
1. If an image fails to download, log a warning but do NOT skip the post — output the Notion URL as a comment instead
1. Do not fail the whole sync if one image fails
### Incremental Sync

1. Store last sync timestamp in `.last_sync` file (ISO-8601)
1. On each run, query Notion for pages where `last_edited_time` > last sync time
1. Only regenerate changed posts
1. On first run (no `.last_sync`), sync ALL published articles
1. After successful sync, update `.last_sync`
### Conflict Handling

- If a post with the same filename already exists in `_posts/`, **overwrite it** (Notion is the source of truth for published content)
- If a published post is set back to Draft or Archived in Notion, do NOT auto-delete the Jekyll post — log a warning instead

### Validation Guard: Repo Slug & Publication Date Consistency

Before writing any post file, the sync validates the Repo Slug and Publication Date:

**For existing files** (matched by Repo Slug on disk):
- If the front-matter `date:` differs from the Publication Date in Notion, log a warning (indicates a URL move)
- Allow the update with the URL move warning

**For new files** (Repo Slug provided, file doesn't exist):
- The Repo Slug prefix (YYYY-MM-DD) must match the Publication Date
- If they mismatch, skip the row and log a warning instead of creating a duplicate file
- If Repo Slug has no valid date prefix (e.g., `what-happens-if-we-refuse-discharge`), skip and warn

**For auto-generated filenames** (no Repo Slug provided):
- Publication Date must be available to generate a valid Jekyll filename
- If both are missing, skip and warn — never create a file without a date

This guard prevents duplicate files when Repo Slugs are stale, and catches accidental URL moves.

### Dry Run Mode

`python scripts/notion-sync.py --dry-run`

- Queries Notion and shows what posts would be synced
- Shows the generated front matter for each
- Does NOT write any files or commit
### Dependencies

**`requirements.txt`**:**

```javascript
notion-client>=2.0.0
requests>=2.28.0
python-dotenv>=1.0.0
```

**`.env.example`**:**

```javascript
NOTION_API_KEY=your_notion_api_key_here
NOTION_DATABASE_ID=your_database_id_here
```

### GitHub Action

`.github/workflows/notion-sync.yml` — **manual trigger only until testing is stable:**

```yaml
name: Sync from Notion
on:
  # schedule:
  #   - cron: '0 */6 * * *'  # UNCOMMENT AFTER TESTING
  workflow_dispatch:
jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt
      - run: python scripts/notion-sync.py
        env:
          NOTION_API_KEY: $ secrets.NOTION_API_KEY 
          NOTION_DATABASE_ID: $ secrets.NOTION_DATABASE_ID 
      - run: |
          git config user.name "notion-sync"
          git config user.email "sync@dispatchesfromdischargehell.com"
          git add .
          git diff --cached --quiet || git commit -m "Sync from Notion $(date +%Y-%m-%d)"
          git push
```

### Notion API Setup (Jorge does this manually)

1. Go to [notion.so/my-integrations](http://notion.so/my-integrations) → Create new integration → Name: "Jekyll Sync" → Type: Internal
1. Copy the API key
1. In Notion, open Dispatches HQ database → `•••` → Connections → Add "Jekyll Sync"
1. Store secrets:
   - **Local:** `.env` file with `NOTION_API_KEY` and `NOTION_DATABASE_ID`
   - **GitHub:** Repo → Settings → Secrets → `NOTION_API_KEY` and `NOTION_DATABASE_ID`

1. Database ID: Open the Master Content Pipeline → URL contains `notion.so/{workspace}/{DATABASE_ID}?v=...` → copy the 32-char hex string
---

## Custom Domain Setup

### GitHub Repository

- **Repo:** `github.com/Jorgeetoe/dispatchesfromdischargehell`
- **Username:** `Jorgeetoe`
- **Local path:** `~/dispatchesfromdischargehell-chirpy`
- **Latest commit:** 957603b "Clean Chirpy installation with full site configuration"
### Config Strategy

- **`_config.yml`** — staging: `baseurl: /dispatchesfromdischargehell`
- **`_config.production.yml`** — production: clears `baseurl`, sets `url: https://dispatchesfromdischargehell.com`
- Pages workflow switches to production config when root CNAME is added
### DNS Records (at domain registrar)

```javascript
Type    Name    Value
A       @       185.199.108.153
A       @       185.199.109.153
A       @       185.199.110.153
A       @       185.199.111.153
CNAME   www     Jorgeetoe.github.io
```

### Cutover Plan

1. Verify site fully on staging URL first
1. Point DNS only after site is verified
1. Test all redirects
1. Cancel Hostinger when billing cycle ends
---

## Visual Direction

> 🎨 **Preserve current site presentation.** Keep Chirpy as the visual base. Keep current page chrome and navigation unless explicitly changed. Borrow editorial patterns from reference sites only at the content level. Avoid template changes unless clearly requested.

### Reference Sites (content-level inspiration only)

- [danielmiessler.com](http://danielmiessler.com/) — clean layout, category structure
- [craigmod.com](http://craigmod.com/) — writing-forward design
- [themarginalian.org](http://themarginalian.org/) — editorial depth
These are for **content and editorial patterns only** — not for redesigning the Chirpy theme.

### Current Navigation

Start Here · About · Telos · Categories · Tags · Archives

---

## Explicitly Not Part of the Current Direction

> 🚫 These are **out of scope** unless Jorge explicitly requests them:
>
> - Replacing Chirpy with a fully custom Jekyll layout system
> - Moving static pages into `_pages/` (they live in `_tabs/`)
> - Introducing `/welcome/` as a default required page
> - Redesigning nav to match another site's layout
> - Rebuilding the homepage template from scratch
> - Custom `_includes/` / `_layouts/` as the primary architecture
> - Any "recreate templates from existing design" approach

Content-level improvements are preferred over template rewrites. The current Chirpy-based site structure is preserved unless Jorge explicitly asks for a redesign.

---

## Non-Negotiables

1. **Preserve current Chirpy-based site structure** unless explicitly asked to redesign
1. **URL stability and redirects** — legacy `.html` URLs redirect via `redirect_from`
1. **Git as rollback/audit trail** — every change is tracked
1. **Notion integrated through a bridge, not as a direct live renderer** — Notion is editorial, Git is publishing
1. **HIPAA compliance** — No patient names, MRNs, DOBs, addresses, or identifiable details ever. Content uses composite scenarios and de-identified patterns only. If anything looks like PHI, STOP and flag it.
---

## Slash Commands

| Command | What it does |
| --- | --- |
| `/sync-notion` | Pull published posts from Notion, generate Markdown, commit + push |
| `/stage` | Takes a pasted draft → generates Jekyll Markdown with front matter → saves to `_posts/` → does NOT push |
| `/publish` | `git add . && git commit && git push` → GitHub Actions deploys |
| `/end-session` | Auto-update [CLAUDE.md](http://claude.md/) with project state |

---

## Canonical Sources

| Document | Location |
| --- | --- |
| **Canonical spec** | `docs/build-spec.md` in repo + this Notion page |
| Supporting: Notion integration prep | `docs/notion-integration-prep.md` |
| Supporting: Spec alignment | `docs/build-spec-alignment.md` |
| Supporting: Domain cutover | `docs/custom-domain-cutover.md` |
| Supporting: Editorial audit | `docs/editorial-audit.md` |

---

## Enhancement Roadmap (Post-Migration)

| Priority | Enhancement | Notes |
| --- | --- | --- |
| P1 | 25-part series navigation | Custom front matter `series`  • `series_part` → auto-generate nav |
| P1 | Email subscribe form | Service TBD. Add CTA to homepage and post footers. |
| P2 | Reading progress bar | Thin 3px bar at top of viewport |
| P2 | Social sharing buttons | Copy Link, LinkedIn, X/Twitter. Minimal. |
| P3 | Related posts | 2–3 posts from same category at bottom of post |

---

## Codex Instructions: Repo Slug Population + Full Sync

> 🤖 **Codex Task (Mar 16, 2026):** Three-phase job. Do all three in order. Do NOT commit or push until Phase 3 is verified.

### Phase 1: Build the Repo Slug mapping

Scan `_posts/` in the repo and build a mapping of existing filenames (without `.md`) to Notion page titles. Use fuzzy title matching — the Notion titles are often longer or formatted differently than the repo slugs.

**All 25 published Notion articles (ordered by Publication Date):**

```plain text
2025-01-01  Dispatches from Discharge Hell: A 25-Part Series on the Patterns Nobody Warns You About
2025-01-06  Dispatches from Discharge Hell, Part 1: The Family Readiness Mismatch
2025-01-20  Dispatches from Discharge Hell, Part 2: The Payer-Driven Discharge Timeline
2025-02-03  Dispatches from Discharge Hell, Part 3: The Ghost SNF
2025-02-17  Dispatches from Discharge Hell, Part 4: The DME Delivery Black Hole
2025-03-17  Dispatches from Discharge Hell, Part 6: The Faith-Function Tension
2025-03-26  Catastrophic Case Management: Brutal Truths from the Front Lines
2025-03-31  Dispatches from Discharge Hell, Part 7: Funny How That Works
2025-04-14  Dispatches from Discharge Hell, Part 8: The Complexity-Admission Mismatch
2025-04-28  Dispatches from Discharge Hell, Part 9: The Difficult Conversation Industrial Complex
2025-05-04  When 'Affordable' Isn't: The High Stakes of High-Deductible Health Plans In Catastrophic Care
2025-05-12  Dispatches from Discharge Hell, Part 10: Perverse Incentives by Design
2025-05-26  Dispatches from Discharge Hell, Part 11: It Depends on Who Shows Up
2025-06-09  Dispatches from Discharge Hell, Part 12: Not Our Problem Anymore
2025-06-23  Dispatches from Discharge Hell, Part 13: We Don't Do Out-of-Area
2025-09-05  Peer-to-Peer Pathophysiology: The Data They Don't Want You to See
2026-02-15  The P2P Playbook™: Your Professional Guide to Medical Gaslighting
2026-02-19  Everybody Has a Plan Until They Get Punched in the Face
2026-02-19  The Lion and the Kitten: Moral Injury in the Conference Room
2026-02-21  The Other Woman Had a Ramp
2026-02-21  The Permission to Rest
2026-02-21  Flex for Me, Not for Thee
2026-02-21  The Misdiagnosis Tax: 23.5% of DOC Patients Arrive With the Wrong Label
2026-02-22  Dispatches from Discharge Hell, Part 5: The Home Health Illusion
2026-02-26  She Knew and She Didn't Say Anything: When Payer Case Managers Weaponize Silence
```

**Matching rules:**

- For each file in `_posts/`, extract the filename stem (e.g. `2024-01-01-dispatches-from-discharge-hell-25-part-series`)
- Match it to a Notion title using keywords, part numbers, and distinctive phrases
- If a Notion title has NO existing repo file counterpart, leave `Repo Slug` blank (the script will auto-generate)
- If two repo files could match the same Notion page, pick the closer match and flag it for review
- Print the full mapping table before writing anything
### Phase 2: Populate `Repo Slug` in Notion via API

For each matched pair, use the Notion API to set the `Repo Slug` property on that page.

**API call pattern:**

```python
import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()
notion = Client(auth=os.environ["NOTION_API_KEY"])

# For each page that has a repo match:
notion.pages.update(
    page_id="<page_id>",
    properties={
        "Repo Slug": {
            "rich_text": [{
                "type": "text",
                "text": {"content": "2024-01-01-dispatches-from-discharge-hell-25-part-series"}
            }]
        }
    }
)
```

**Important:** The `Repo Slug` value is the filename stem only — no `.md` extension, no `_posts/` prefix.

Pages with no existing repo match should have `Repo Slug` left empty (do not set it).

### Phase 3: Update `notion-sync.py` to use `Repo Slug`

Modify `scripts/notion-sync.py` so that when building the output filename for a page:

1. Read the `Repo Slug` property from the page
1. If `Repo Slug` is non-empty, use it: `filename = f"_posts/{repo_slug}.md"`
1. If `Repo Slug` is empty, generate as before: `filename = f"_posts/{pub_date}-{slugify(title)}.md"`
1. Also read `Repo Slug` in the Notion API query (add it to the property filter/retrieval)
### Phase 4: Verify with dry run + controlled write

1. Run `python scripts/notion-sync.py --dry-run` — confirm all 25 pages are listed, and that pages with `Repo Slug` show the override filename
1. Run a local write on the same 5 test pages as before:
   - Dispatches Series Intro
   - Home Health Illusion (Part 5)
   - The P2P Playbook™
   - She Knew and She Didn't Say Anything
   - Flex for Me, Not for Thee

1. Verify:
   - Files with `Repo Slug` overwrite the existing repo files (not create new ones)
   - Files without `Repo Slug` (like "She Knew") create new files as expected
   - Front matter, body content, and `redirect_from` are correct
   - Repo-only front matter keys (`notes:`, `excerpt:`) are preserved

1. Show a diff summary of what changed
### Phase 5: Full sync (after Phase 4 is verified)

1. Run `python scripts/notion-sync.py` (full write, all 25 pages)
1. Delete any orphan files in `_posts/` that were replaced by Notion-synced versions with different filenames (if any remain after `Repo Slug` mapping)
1. Do NOT commit or push yet — let Jorge review locally first
1. Show the complete list of files written, any files that would be orphaned, and a summary of changes
---

## Codex Instructions: Verify Staging Site + Sync docs/[build-spec.md](http://build-spec.md/)

> 🔍 **Codex Task (Mar 16, 2026):** Two jobs. Do both in order. Commit and push at the end.

**Context:** Commit `8d7e691` was just pushed. The staging site at `https://jorgeetoe.github.io/dispatchesfromdischargehell/` should now have all 31 Notion-managed posts. Also, `docs/build-spec.md` in the repo is stale (ends at line 252) and needs to be regenerated from the Notion Build Spec page via the API.

### Job 1: Verify Staging Site

Check that the GitHub Pages deploy succeeded and all 31 posts are live.

**Phase 1: Check deploy status**

```bash
# Check if GitHub Actions build completed
curl -s -o /dev/null -w "%{http_code}" https://jorgeetoe.github.io/dispatchesfromdischargehell/
# Should return 200
```

**Phase 2: Verify all 31 posts resolve**

For each of the 31 files in `_posts/`, construct the expected URL and check the HTTP status:

```bash
# For each file in _posts/, extract date and slug, build URL, curl it
for f in _posts/*.md; do
  stem=$(basename "$f" .md)
  # Expected URL pattern: /dispatchesfromdischargehell/blog/posts/SLUG/
  url="https://jorgeetoe.github.io/dispatchesfromdischargehell/blog/posts/${stem}/"
  status=$(curl -s -o /dev/null -w "%{http_code}" "$url")
  echo "${status} ${stem}"
done
```

All 31 should return `200`. Flag any that return `404` or other errors.

**Phase 3: Spot-check key pages**

Verify these specific URLs return `200`:

```javascript
https://jorgeetoe.github.io/dispatchesfromdischargehell/
https://jorgeetoe.github.io/dispatchesfromdischargehell/start-here/
https://jorgeetoe.github.io/dispatchesfromdischargehell/about/
https://jorgeetoe.github.io/dispatchesfromdischargehell/telos/
https://jorgeetoe.github.io/dispatchesfromdischargehell/categories/
https://jorgeetoe.github.io/dispatchesfromdischargehell/tags/
https://jorgeetoe.github.io/dispatchesfromdischargehell/archives/
```

**Phase 4: Verify categories**

Check that each of the 5 category pages exists:

```javascript
https://jorgeetoe.github.io/dispatchesfromdischargehell/categories/dispatches/
https://jorgeetoe.github.io/dispatchesfromdischargehell/categories/field-notes/
https://jorgeetoe.github.io/dispatchesfromdischargehell/categories/the-machine/
https://jorgeetoe.github.io/dispatchesfromdischargehell/categories/when-it-breaks/
https://jorgeetoe.github.io/dispatchesfromdischargehell/categories/persona/
```

Report the full results before moving on.

### Job 2: Regenerate docs/[build-spec.md](http://build-spec.md/) from Notion API

The Notion Build Spec page is the canonical source. Read it via the Notion API and write `docs/build-spec.md`.

**Phase 1: Read the Build Spec page from Notion**

```python
import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()
notion = Client(auth=os.environ["NOTION_API_KEY"])

# The Build Spec page ID — extract from the page URL in Notion
# You can find it by searching the database or using the known page
BUILD_SPEC_PAGE_ID = "<page_id>"  # Jorge will provide if needed

# Retrieve all blocks from the page
blocks = []
start_cursor = None
while True:
    kwargs = {"block_id": BUILD_SPEC_PAGE_ID, "page_size": 100}
    if start_cursor:
        kwargs["start_cursor"] = start_cursor
    response = notion.blocks.children.list(**kwargs)
    blocks.extend(response["results"])
    if not response["has_more"]:
        break
    start_cursor = response["next_cursor"]
```

**Phase 2: Convert Notion blocks to Markdown**

Write a converter that handles:

- `heading_1`, `heading_2`, `heading_3` → `#`, `##`, `###`
- `paragraph` → plain text
- `bulleted_list_item` → `- item`
- `numbered_list_item` → `1. item`
- `code` → fenced code blocks with language
- `callout` → `> emoji text`
- `divider` → `---`
- `table` → markdown table
- `quote` → `> text`
- Rich text annotations: bold → `**text**`, italic → `*text*`, code →  `text` , link → `[text](url)`
- Nested children (indented lists, toggle content)
**Important rules:**

- Strip Notion-specific formatting that doesn't translate to plain markdown
- Preserve all code blocks exactly as-is
- Tables should use standard markdown pipe format
- Keep callouts as blockquotes with emoji prefix
- The output should be clean, readable markdown
**Phase 3: Write the file**

```python
with open("docs/build-spec.md", "w") as f:
    f.write(markdown_content)
```

**Phase 4: Verify**

1. Confirm `docs/build-spec.md` is significantly longer than 252 lines (the old stale version)
1. Spot-check that key sections are present: "Why This Stack", "Site Architecture", "Notion CMS Bridge", "Custom Domain Setup", "Phase 5 Full Sync Results", "Import 6 Repo-Only Orphans"
1. Confirm `jekyll build` still passes (the docs folder shouldn't affect the build, but verify)
**Phase 5: Commit and push**

```bash
git add .
git commit -m "Verify staging + regenerate docs/build-spec.md from Notion"
git push
```

**Note about the Build Spec page ID:** If you don't have the page ID, you can find it by searching the Notion database for a page titled "Build Spec" or by checking [CLAUDE.md](http://claude.md/) for any stored page references. Alternatively, Jorge can provide it.

---

## Codex Instructions: Import 6 Repo-Only Orphans into Notion

> 📥 **Codex Task (Mar 16, 2026):** Import 6 repo-only posts into the Notion Master Content Pipeline so they become Notion-managed. Jorge has already committed and pushed the full 25-post sync. Do NOT commit or push until the end.

**Context:** These 6 posts exist in `_posts/` but have no corresponding Notion page. They predate the Notion CMS bridge or were created manually. The goal is to bring them under Notion management so future syncs cover all posts.

### The 6 files

```plain text
_posts/2017-11-15-the-book-i-picked-up-as-a-joke-that-rewired-my-entire-life.md
_posts/2025-03-16-preadmission-guidelines-vip-ticket-rehab-reality-show.md
_posts/2025-03-19-when-sarcasm-and-humor-is-the-best-medicine.md
_posts/2025-09-03-moneyball-for-medical-necessity.md
_posts/2026-02-15-rehabilitation-vs-catastrophic-care.md
_posts/2026-02-15-what-doc-rehab-actually-does.md
```

### Phase 1: Extract front matter from each file

For each of the 6 files, read the YAML front matter and body content. Extract:

- `title` → `Content Title`
- `date` → `Publication Date`
- `categories` → `Content Category` (reverse the category mapping below)
- `description` → `Content Summary`
- `keywords` → `SEO Keywords`
- The filename stem (without `.md`) → `Repo Slug`
**Reverse category mapping (Jekyll → Notion):**

| Jekyll Category | Notion Content Category |
| --- | --- |
| `dispatches` | Satirical |
| `field-notes` | Educational |
| `the-machine` | Clinical Insight |
| `when-it-breaks` | Satirical |
| `persona` | Personal Reflection |
| *(no category or unknown)* | *(leave empty — Jorge will classify)* |

Print a table showing what you extracted from each file before making any API calls.

### Phase 2: Create 6 pages in Notion via API

For each file, create a new page in the Master Content Pipeline database.

**API call pattern:**

```python
import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()
notion = Client(auth=os.environ["NOTION_API_KEY"])
DATABASE_ID = os.environ["NOTION_DATABASE_ID"]

# For each orphan post:
notion.pages.create(
    parent={"database_id": DATABASE_ID},
    properties={
        "Content Title": {
            "title": [{"type": "text", "text": {"content": "<title from front matter>"}}]
        },
        "Content Status": {
            "status": {"name": "Published"}
        },
        "Content Type": {
            "select": {"name": "Article"}
        },
        "Content Category": {
            "multi_select": [{"name": "<mapped category>"}]
        },
        "Publication Date": {
            "date": {"start": "<YYYY-MM-DD from front matter>"}
        },
        "Content Summary": {
            "rich_text": [{"type": "text", "text": {"content": "<description from front matter>"}}]
        },
        "SEO Keywords": {
            "rich_text": [{"type": "text", "text": {"content": "<keywords from front matter>"}}]
        },
        "Repo Slug": {
            "rich_text": [{"type": "text", "text": {"content": "<filename stem, no .md>"}}]
        }
    }
)
```

**Important rules:**

- `Content Status` = "Published" (these are live on the site)
- `Content Type` = "Article"
- `Repo Slug` = the existing filename stem (e.g. `2017-11-15-the-book-i-picked-up-as-a-joke-that-rewired-my-entire-life`). This ensures future syncs overwrite the correct file.
- If `description` or `keywords` are missing from the front matter, leave those properties empty.
- If `categories` is missing or doesn't map, leave `Content Category` empty.
- Do NOT paste the body content into the Notion page — Notion is the metadata layer, the repo file is the source of truth for body content until Jorge edits in Notion.
### Phase 3: Verify

1. Query the Notion database and confirm 31 total Published Articles (25 original + 6 new)
1. Run `python scripts/notion-sync.py --dry-run` — confirm all 31 are listed
1. Run an incremental sync for just the 6 new pages to verify the Repo Slug overwrites the existing files (not creates duplicates)
1. Confirm `jekyll build` still passes
1. Show the results before committing
### Phase 4: Commit and push

```bash
git add .
git commit -m "Add 6 repo-only posts to Notion management"
git push
```

---

## Session Logging Rule

Every coding session must produce a log entry:

```javascript
**Session:** [Brief title]
**Date:** YYYY-MM-DD
**What changed:** [Files modified, created, or deleted]
**Decisions made:** [Choices about design, structure, or approach]
**What's left:** [Incomplete work or next steps]
**Who requested the changes:** [Jorge / Plasticity spec / other]
**Search keywords:** [Filenames, features, tools, concepts]
```
