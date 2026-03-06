# /stage — Verify, Format & Stage New Post

## What This Does

Takes a pasted draft and:
1. Verifies required metadata
2. HIPAA scan
3. Voice consistency check
4. Checks template for recent changes
5. Backs up existing files if re-staging
6. Generates HTML + updates site indexes
7. Updates post-index.json
8. Regenerates RSS feed
9. Reports what was staged

**Does NOT deploy.** Wait for `/publish`.

## Step 1: Verify Input

Ask Jorge for any missing fields:
- Article text (full draft)
- Title tag (under 60 characters, includes keyword)
- Meta description (150-160 characters, keyword-included)
- Target keyword
- Category (Dispatches / Field Notes / The Machine / Case Files / Persona)
- Publication date (YYYY-MM-DD format)

Stop and ask if anything is missing.

## Step 2: HIPAA Scan

Check for:
- Patient names, MRNs, DOBs, addresses, medical record numbers
- Facility names (unless clearly fictional)
- Insurance company names (unless pattern/systemic reference)
- Any specific identifiers

**If PHI found:** Flag it, STOP, do not proceed. Report to Jorge.

## Step 3: Voice Verification

Against `config/voice_guide.md`:
- Does it use collective "we" in narratives? (Or justified "I" in anecdotes?)
- Em dashes used sparingly?
- Common language or over-polished?
- Any banned phrases: unlock, streamline, optimize, leverage, robust, comprehensive solution?
- Reads like AI or like a case manager?

**Flag issues (don't fix them).** Report findings.

## Step 4: Check Template for Changes

Compare `site/blog/post-template.html` modification date with the most recent post in `site/blog/posts/`:
- If template is newer: Note the change in the report (e.g., "Template updated since last post — review section XYZ")
- Include in final report so Jorge can decide if older posts need updating
- Do NOT modify older posts unless Jorge explicitly requests it

## Step 5: Check for Existing File & Backup

Before writing the new post file, check if `site/blog/posts/YYYY-MM-DD-slug.html` already exists:

**If file exists:**
1. Create `site/blog/posts/.backup/` directory if it doesn't exist
2. Copy the existing file to: `site/blog/posts/.backup/YYYY-MM-DD-slug.TIMESTAMP.html`
   - TIMESTAMP format: `YYYYMMDD-HHMMSS` (e.g., `20260301-183045`)
3. Note in the final report: "Backup created: `.backup/YYYY-MM-DD-slug.TIMESTAMP.html`"

**If file doesn't exist:**
- Proceed normally (new post)

This protects against accidental overwrites when re-staging a post.

## Step 6: Generate HTML

1. Use `site/blog/post-template.html` as base structure
2. Look at most recent post in `site/blog/posts/` for formatting patterns
3. Generate slug from title/keyword: `YYYY-MM-DD-slug-part-N.html` (lowercase, hyphens)
4. Populate template fields:
   - `<title>` tag: "TITLE | Dispatches from Discharge Hell"
   - `<meta name="description">`
   - `<meta property="og:*">` tags (title, description, url, type=article)
   - `<meta name="twitter:*">` tags
   - `<link rel="canonical">` tag pointing to full absolute URL: `https://dispatchesfromdischargehell.com/blog/posts/YYYY-MM-DD-slug.html`
   - JSON-LD Article schema: headline, description, datePublished, author (Jorge Arenivar), mainEntityOfPage
   - JSON-LD BreadcrumbList schema (separate from Article schema):
     - Home: `https://dispatchesfromdischargehell.com/`
     - Writing: `https://dispatchesfromdischargehell.com/blog/`
     - [Category]: `https://dispatchesfromdischargehell.com/blog/#[category-slug]` (or category landing page if exists)
     - [Post Title]: `https://dispatchesfromdischargehell.com/blog/posts/YYYY-MM-DD-slug.html`
   - Category tag (span.category-tag)
   - H1: matches title
   - Post date (both `datetime` attribute and display text)
   - Full article content in `<div class="article-content">`
   - Internal links to 2-3 related posts where natural
     - Read `config/post-index.json` to find related posts by category/keyword
     - Link format: `/blog/posts/filename` (use `url_path` from post-index)
   - Visible breadcrumb navigation (HTML, near top of post, before article content):
     ```html
     <nav aria-label="breadcrumbs" class="breadcrumb">
       <a href="/">Home</a> /
       <a href="/blog/">Writing</a> /
       <a href="/blog/#category-slug">[Category]</a> /
       <span>[Post Title]</span>
     </nav>
     ```
   - Previous/Next post navigation (at bottom of post, after article content):
     - Read `config/post-index.json` and sort by date to find chronological neighbors
     - For each post, find the post with next-newer date (Previous) and next-older date (Next)
     - Use post title and filename from post-index to build links
     - **If newest post:** Only show "← Previous [Post Title]" link
     - **If oldest post:** Only show "Next [Post Title] →" link
     - **If middle post:** Show both "← Previous..." and "Next..." links
     - Link format: `/blog/posts/[filename]` (use `url_path` from post-index)
     - HTML structure (use class `post-nav` to match existing site CSS):
       ```html
       <nav class="post-nav">
         <a href="/blog/posts/PREVIOUS-SLUG.html" class="prev">← Previous Post Title</a>
         <a href="/blog/posts/NEXT-SLUG.html" class="next">Next Post Title →</a>
       </nav>
       ```
     - If only Previous exists: `<a href="..." class="prev">← Previous Post Title</a>`
     - If only Next exists: `<a href="..." class="next">Next Post Title →</a>`

5. Save to: `site/blog/posts/YYYY-MM-DD-slug.html`

### BreadcrumbList JSON-LD Format

Include this as a separate `<script type="application/ld+json">` block in `<head>` (after the Article schema):

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "Home",
      "item": "https://dispatchesfromdischargehell.com/"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "Writing",
      "item": "https://dispatchesfromdischargehell.com/blog/"
    },
    {
      "@type": "ListItem",
      "position": 3,
      "name": "[Category]",
      "item": "https://dispatchesfromdischargehell.com/blog/#[category-slug]"
    },
    {
      "@type": "ListItem",
      "position": 4,
      "name": "[Post Title]",
      "item": "https://dispatchesfromdischargehell.com/blog/posts/YYYY-MM-DD-slug.html"
    }
  ]
}
```

Replace `[Category]` with actual category (Dispatches, Field Notes, The Machine, Case Files, Persona) and `[Post Title]` with the actual post title.

## Step 7: Update Blog Indexes

**Update `site/blog/index.html`:**
- Add new post entry to list (newest first)
- Keep existing format/structure

**Update `site/index.html`:**
- If homepage lists recent posts, update it

## Step 8: Update Sitemap

**Update `site/sitemap.xml`:**
- Add new URL: `https://dispatchesfromdischargehell.com/blog/posts/YYYY-MM-DD-slug.html`
- Maintain XML structure

## Step 9: Report

Output:
```
✓ POST STAGED
File: site/blog/posts/YYYY-MM-DD-slug.html
Title: [title]
Category: [category]
Keyword: [keyword]

SEO Applied:
- Title tag (59 chars): ✓
- Meta description (157 chars): ✓
- OG tags: ✓
- Schema (JSON-LD): ✓
- Keyword in title/desc/H1/first-para/subheading: ✓
- Internal links: 3 related posts

Indexes Updated:
- site/blog/index.html ✓
- site/index.html ✓
- site/sitemap.xml ✓

Flags:
[any voice warnings, minor issues]

Template Status:
[If template.html was modified: "Template updated since last post (review X section)"]
[If template unchanged: "Template unchanged"]

Backup Status:
[If file was overwritten: "Backup created: .backup/YYYY-MM-DD-slug.TIMESTAMP.html"]
[If file was new: "New post (no backup needed)"]

Next: Run /publish when ready to deploy.
```

## Step 10: Update Post Index

Update `config/post-index.json`:
- Extract from the newly staged post:
  - filename: `YYYY-MM-DD-slug.html`
  - title: from `<h1>` tag
  - date: from filename (YYYY-MM-DD)
  - category: from `span.category-tag`
  - target_keyword: from meta description or keywords tag
  - url_path: `/blog/posts/YYYY-MM-DD-slug.html`
- Append this entry to `config/post-index.json` (check if post already exists to avoid duplicates)
- This index serves as the source of truth for all posts and enables fast internal link lookups

## Step 11: Regenerate RSS Feed

Regenerate `site/feed.xml`:
- Read updated `config/post-index.json`
- Include the 20 most recent posts (newest first)
- For each post, extract: title, link (full URL), description (target_keyword), pubDate, category, guid
- Valid RSS 2.0 format with proper XML structure
- Feed is automatically discoverable via `<link rel="alternate">` tags in site/index.html and site/blog/index.html

---

**Important:** You receive FINISHED drafts. Do not rewrite. Do not add content. Apply SEO + formatting only.
