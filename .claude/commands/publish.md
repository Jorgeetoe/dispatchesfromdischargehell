# /publish — Publish New Post to Cloudflare Pages

Publish a new blog post to dispatchesfromdischargehell.com via GitHub + Cloudflare Pages.

## Workflow

When you paste a draft article, I will:

1. **Parse the draft** — Extract title, date, category, keywords, description
2. **Create Markdown file** — Generate `hugo/content/blog/posts/YYYY-MM-DD-slug.md` with YAML front matter
3. **Verify locally** — Build with Hugo to check for errors
4. **Commit and push** — Commit to git and push to GitHub
5. **Auto-deploy** — Cloudflare Pages builds and deploys (2-3 minutes)
6. **Report** — Show you the live URL

## Example Flow

```
$ /publish
[Paste article content with metadata]

Processing: "She Knew and She Didn't Say Anything"
Category: Dispatches
Date: February 26, 2026
Keywords: insurance silence, case management, system design

Creating: hugo/content/blog/posts/2026-02-26-she-knew-and-she-didnt-say-anything.md
✓ File created with front matter

Building locally...
✓ Hugo build successful (71 pages)

Committing to git...
✓ Commit: "Publish: She Knew and She Didn't Say Anything"
✓ Pushed to GitHub

Cloudflare Pages is now building...
✓ Build started

Live in ~2-3 minutes at:
https://dispatchesfromdischargehell.com/blog/posts/2026-02-26-she-knew-and-she-didnt-say-anything/
```

## What You Need to Provide

When pasting a draft, include:
- **Full article text** (finished, ready to publish)
- **Title** (SEO optimized, under 60 chars)
- **Category** (Dispatches, Field Notes, The Machine, Case Files, or Persona)
- **Date** (publication date)
- **Meta description** (150-160 chars, keyword-rich)
- **Keywords** (2-4 main topics)

Example:
```
Title: She Knew and She Didn't Say Anything
Date: 2026-02-26
Category: Dispatches
Description: When insurance case managers know the family's plan won't be covered but stay silent anyway.
Keywords: insurance silence, system design, case management

[Article text here...]
```

## No Manual Steps

- ✅ No FTP passwords
- ✅ No manual HTML generation
- ✅ No blog listing updates
- ✅ Fully automated: git → Cloudflare Pages → live
