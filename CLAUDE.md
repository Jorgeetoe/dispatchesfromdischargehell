# CLAUDE.md — Dispatches from Discharge Hell

## What This Project Is

Static HTML/CSS blog at dispatchesfromdischargehell.com, hosted on Hostinger.
Content is written by Jorge Arenivar (RN, BSN, CCM, CRRN) — 20+ years in catastrophic neurorehabilitation case management.
Blog tagline: "What actually happens when insurance runs out and the hospital needs your bed."

## Your Role

You are the final step in a content pipeline. You receive **finished, reviewed drafts** from Plasticity (Notion AI). Your job:

1. Apply SEO optimization (title tag, meta description, target keyword, schema markup)
2. Generate publish-ready HTML matching the site's existing design
3. Deploy to Hostinger via FTP

You do NOT draft content. You do NOT revise voice or tone. The draft arrives ready. You format and publish.

## Site Structure

```
DispatchesFromDischargeHell/
├── site/                          # All web-facing files (deployed to Hostinger)
│   ├── index.html                 # Homepage
│   ├── blog/
│   │   ├── index.html             # Blog listing page
│   │   ├── posts/                 # Published post HTML files
│   │   │   ├── 2026-02-15-what-doc-rehab-actually-does.html
│   │   │   ├── 2026-01-03-flex-for-me-not-for-thee.html
│   │   │   └── ... (more posts)
│   │   └── post-template.html     # HTML template for new posts
│   ├── about/
│   │   └── index.html
│   ├── telos/
│   │   └── index.html
│   ├── subscribe/
│   │   └── index.html
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   ├── assets/                    # Images, icons
│   ├── robots.txt
│   └── sitemap.xml
├── config/                        # Configuration & policy docs (NOT deployed)
│   ├── voice_guide.md
│   ├── editorial_policy.md
│   └── telos.md
├── .claude/
│   └── commands/                  # Slash command implementations
│       ├── stage.md
│       ├── publish.md
│       └── end-session.md
├── published/                     # Archive of published markdown drafts
├── drafts/                        # Raw incoming drafts
├── raw/                           # Raw notes (NOT deployed)
├── processed/                     # Processed but not yet published
├── intel/                         # Research & analysis (NOT deployed)
├── logs/                          # Pipeline logs
├── CLAUDE.md                      # This file
└── deploy.sh                      # Deployment script
```

## Blog URL Pattern

`/blog/posts/YYYY-MM-DD-slug-part-N.html`

Examples:
- `/blog/posts/2026-02-21-permission-to-rest.html`
- `/blog/posts/2024-01-03-family-readiness-mismatch-part-1.html`

The blog listing page is at `site/blog/index.html`. The homepage is at `site/index.html`.

## Content Categories (5)

| Category | Icon | Description |
|---|---|---|
| Dispatches | — | Dark humor, satire about system absurdity |
| Field Notes | — | Practical guidance for families and clinicians |
| The Machine | — | Institutional mechanics, payer games, system analysis |
| Case Files | — | De-identified pattern stories from 20 years |
| Persona | — | Off-duty reflections |

## What Jorge Pastes In

When Jorge opens Claude Code, he pastes a block that includes:
- The full article text (finished draft)
- SEO metadata: title tag, meta description, target keyword
- Content category (Dispatches, Field Notes, The Machine, Case Files, or Persona)
- Publication date

If any of these are missing, ask for them before proceeding. Do not guess the category or keyword.

## Slash Commands

| Command | What it does |
|---|---|
| `/stage` | Takes pasted draft → applies SEO → generates HTML matching site design → saves to site/blog/posts/ |
| `/publish` | Deploys site to Hostinger via FTP using deploy.sh |
| `/end-session` | Saves current project state to this file under Session State below |

## FTP Deploy

Environment variables required:
- `DISPATCHES_FTP_HOST`
- `DISPATCHES_FTP_USER`
- `DISPATCHES_FTP_PASS`

If these aren't set, remind Jorge to configure them from Hostinger hpanel → Advanced → FTP Accounts.

## HTML Generation Rules

- Match existing site's HTML/CSS structure exactly. Reference any recently published post in `site/blog/posts/` as your template.
- Static HTML only. No JavaScript frameworks, no build tools, no dependencies.
- Include Open Graph meta tags (og:title, og:description, og:type, og:url).
- Include article schema markup (JSON-LD).
- Add the post to `site/blog/index.html` in the correct chronological position (newest first).
- Update `site/index.html` if it references recent posts.
- Preserve the existing navigation, header, footer, and CSS classes.

## SEO Checklist (applied during /stage)

- [ ] Title tag: Under 60 characters, includes target keyword
- [ ] Meta description: 150-160 characters, compelling, includes keyword
- [ ] H1: One per page, matches or closely reflects title tag
- [ ] Target keyword appears in: title, meta description, H1, first paragraph, at least one subheading
- [ ] Internal links: Link to 2-3 related posts where natural (to other `site/blog/posts/` URLs)
- [ ] URL slug: Lowercase, hyphenated, keyword-relevant, saved as `site/blog/posts/YYYY-MM-DD-slug.html`
- [ ] Open Graph tags: title, description, type (article), url
- [ ] Schema markup: Article type, author (Jorge Arenivar), datePublished, description
- [ ] Image alt text: Descriptive, keyword-relevant (if images present)
- [ ] Update `site/sitemap.xml` with new post URL

## HIPAA — Non-Negotiable

- No patient names, MRNs, DOBs, addresses, or identifiable details — ever
- Content uses composite scenarios and de-identified patterns only
- If anything in a pasted draft looks like PHI, STOP and flag it before generating HTML

## Session State

(Updated automatically by /end-session)

Last session: [not yet recorded]
Last published: [not yet recorded]
Total published posts: ~35
Current focus: Blog only until 100 posts. No LinkedIn content yet.
Volume goal: 350-500 posts by year-end 2026.