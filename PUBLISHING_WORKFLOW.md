# Publishing Workflow — Dispatches from Discharge Hell

**How to publish a new post to dispatchesfromdischargehell.com**

## Quick Checklist

- [ ] Write finished draft (Notion/Plasticity AI)
- [ ] Create markdown file in `hugo/content/posts/`
- [ ] Add required front matter (see template below)
- [ ] `git add`, `git commit`, `git push` to main
- [ ] Cloudflare Pages auto-deploys (1-2 min)
- [ ] Verify post live at dispatchesfromdischargehell.com/blog/

---

## File Structure

```
hugo/content/posts/
├── YYYY-MM-DD-slug-part-1.md
├── YYYY-MM-DD-slug-part-2.md
└── ... (all markdown files here)
```

**Example filename:**
- `2026-03-07-permission-to-rest.md`
- `2026-02-21-insurance-denial-playbook.md`

---

## Markdown Template

Copy this template for every new post:

```yaml
---
title: "Post Title Here"
description: "150-160 character meta description for SEO"
date: 2026-03-07
draft: false
categories: ["Dispatches"]
---

Your post content starts here. First paragraph should include your target keyword naturally.

## Section Heading

More content...
```

**Required fields:**
- `title` — The post title
- `description` — Short SEO summary (searches use this)
- `date` — Publication date (YYYY-MM-DD format)
- `categories` — One category: `Dispatches`, `Field Notes`, `The Machine`, `Case Files`, or `Persona`

**Optional:**
- `draft: true` — Hides post from site (remove or set to `false` to publish)

---

## Git Commands (Terminal)

**From the repo root:**

```bash
# 1. Create your file
touch hugo/content/posts/2026-03-07-your-slug.md

# 2. Edit it with content + front matter

# 3. Stage and commit
git add hugo/content/posts/2026-03-07-your-slug.md
git commit -m "Add post: Your Post Title"

# 4. Push to GitHub (triggers automatic deployment)
git push origin main

# 5. Wait 1-2 minutes
# Check: https://dispatchesfromdischargehell.com/blog/
```

---

## What Happens After Push

1. GitHub detects change on `main` branch
2. Triggers Cloudflare Pages build
3. Build runs: `git submodule init && git submodule update && hugo --gc --minify`
4. Hugo generates static HTML from your markdown
5. Site deploys to dispatchesfromdischargehell.com
6. Post appears in blog listing (newest first)

---

## Troubleshooting

**Post not appearing after 5 minutes?**
- Check `draft: false` in front matter
- Check category is valid (spelled correctly, capitalized)
- Verify commit was pushed: `git log` should show your commit
- Check Cloudflare Pages dashboard for build errors

**Post has formatting issues?**
- Hugo uses standard markdown
- Headers: `# H1`, `## H2`, `### H3`
- Bold: `**text**` | Italic: `*text*`
- Links: `[link text](https://url)`
- Lists: `- item` or `1. item`

**Want to unpublish a post?**
- Set `draft: true` in the markdown front matter
- Push to main
- Post hides but file remains in git history

---

## Examples of Live Posts

Check these for formatting reference:
- https://dispatchesfromdischargehell.com/blog/posts/2026-02-26-she-knew-and-she-didnt-say-anything/
- https://dispatchesfromdischargehell.com/blog/posts/2026-02-18-everybody-has-a-plan-until-they-get-punched-in-the-face/

---

## Next: Create Your First Post

Ready to test the workflow? Create a simple dispatch and push it. You'll have it live in 2 minutes.
