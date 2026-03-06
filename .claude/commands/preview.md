# /preview — Preview Site Locally

## What This Does

Starts a local HTTP server to preview the site before publishing. Use this after `/stage` to verify posts look correct.

## Step 1: Start Local Server

Start Python's built-in HTTP server serving the `site/` directory:

```bash
python3 -m http.server 8000 --directory site/
```

This serves your site exactly as it will appear on Hostinger.

## Step 2: Open in Browser

Navigate to:

**http://localhost:8000**

You can now browse:
- Homepage
- Blog listing
- Individual posts
- Navigation and links
- Responsive layout (check mobile view in dev tools)

## Step 3: Preview Last Staged Post (if applicable)

If you just ran `/stage`, the last post is available at:

**http://localhost:8000/blog/posts/YYYY-MM-DD-slug.html**

(The actual filename will be shown here based on what you just staged)

Check:
- [ ] Title displays correctly
- [ ] Meta tags are in place (inspect in dev tools)
- [ ] Category badge shows
- [ ] Date displays
- [ ] Content formatting looks good
- [ ] Links work (internal and navigation)
- [ ] Responsive design (mobile view)
- [ ] Buy me a coffee button appears

## Step 4: Stop When Done

When you're satisfied with the preview, stop the server:

```
Ctrl+C
```

Then run `/publish` to deploy to Hostinger.

---

**TIP:** Keep the server running in one terminal while you inspect the site in another. This makes it easy to check changes if you need to re-stage.
