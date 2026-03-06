# Cloudflare Pages Setup Guide

This guide walks you through connecting your Hugo site to Cloudflare Pages (takes about 15-20 minutes).

## Prerequisites

- GitHub account (free): https://github.com
- Cloudflare account (free): https://www.cloudflare.com
- Your domain registrar login (to update DNS)

## Step 1: Push to GitHub

First, you'll need a GitHub repository. The migration is already committed locally, so now push it:

```bash
cd /Users/jorgearenivar/DispatchesFromDischargeHell

# Create a repo on GitHub at github.com/new
# Name it: DispatchesFromDischargeHell
# Make it Private (you can make it public later if you want)

# Then push the local repo to GitHub:
git remote add origin https://github.com/YOUR_USERNAME/DispatchesFromDischargeHell.git
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

## Step 2: Create Cloudflare Pages Project

1. Go to **https://dash.cloudflare.com**
2. Login with your Cloudflare account
3. Left sidebar: Click **Workers & Pages**
4. Click **Create application**
5. Click **Pages** tab
6. Click **Connect to Git**
7. Authorize GitHub (if prompted)
8. Select your GitHub account
9. Search for and select `DispatchesFromDischargeHell` repo
10. Click **Begin setup**

## Step 3: Configure Build Settings

On the "Create your Cloudflare Pages project" page:

- **Project name**: `dispatchesfromdischargehell` (must be lowercase)
- **Production branch**: `main`
- **Framework preset**: Hugo
- **Build command**: `hugo --gc --minify`
- **Build output directory**: `hugo/public`
- **Root directory**: (leave blank)

Click **Save and Deploy**

(First deploy will take 2-3 minutes)

## Step 4: Add Custom Domain

1. After deployment completes, you'll see a Cloudflare Pages URL like `https://dispatchesfromdischargehell.pages.dev`
2. Click **Custom domain**
3. Enter: `dispatchesfromdischargehell.com`
4. Cloudflare will check DNS
5. Cloudflare will provide nameservers

## Step 5: Update Domain DNS

Your domain is currently pointing to Hostinger. Update it to point to Cloudflare:

1. Go to your domain registrar (wherever you bought the domain)
2. Find "DNS settings" or "Nameservers"
3. Replace the nameservers with Cloudflare's (Cloudflare Pages will tell you which ones)
4. Save

**This usually takes 15 minutes to 2 hours to propagate.**

## Step 6: Verify SSL Certificate

Once DNS propagates, Cloudflare auto-generates an SSL certificate. You should see:
- ✅ Green "Active" status on the custom domain
- HTTPS working at `https://dispatchesfromdischargehell.com`

## Testing

After DNS propagates:

1. Visit `https://dispatchesfromdischargehell.com` in your browser
2. Verify homepage loads
3. Click through a few posts
4. Test dark mode toggle
5. Check mobile responsiveness

## Deployment Workflow

Now that Cloudflare Pages is set up:

Every `git push` to `main`:
- GitHub detects the push
- Cloudflare Pages auto-builds (`hugo --gc --minify`)
- Site deploys within 2-3 minutes
- New content goes live

## Publishing a New Post

```bash
cd /Users/jorgearenivar/DispatchesFromDischargeHell

# Create new post
hugo new hugo/content/blog/posts/YYYY-MM-DD-my-post-title.md

# Edit the file (update front matter, add content)
# nano hugo/content/blog/posts/YYYY-MM-DD-my-post-title.md

# Test locally
cd hugo && hugo server
# Visit http://localhost:1313 and verify post looks good
# Press Ctrl+C to stop

# Commit and push
git add hugo/content/blog/posts/YYYY-MM-DD-my-post-title.md
git commit -m "Publish: My Post Title"
git push

# Site redeploys automatically in 2-3 minutes!
```

## Environment Variables (Optional)

If using the GitHub Actions workflow for more control:

1. Go to your GitHub repo settings
2. Click **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add:
   - `CLOUDFLARE_API_TOKEN`: Get from Cloudflare Dashboard
   - `CLOUDFLARE_ACCOUNT_ID`: Get from Cloudflare Dashboard

Not required for basic setup, but enables direct API deployment.

## Troubleshooting

### Deploy fails in Cloudflare Pages

1. Check the **Deployments** tab in Cloudflare Pages
2. Click the failed deployment
3. Scroll to **Build summary** to see error logs
4. Common issues:
   - Wrong build command
   - Wrong output directory
   - Hugo version incompatibility

### Site looks broken after deploy

1. Hard refresh browser: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
2. Check CSS is loading: Inspect → Network tab, look for 404s
3. Check Cloudflare cache: **Caching** → **Purge cache** → Clear everything

### New post not showing up

1. Check filename: `YYYY-MM-DD-slug.md`
2. Check `draft: false` (or remove `draft` line)
3. Check date is not in the future
4. Wait 2-3 minutes for deploy to finish

## Cancel Hostinger

Once you confirm the Cloudflare site is fully live and working:

1. Log into Hostinger
2. Go to **Billing**
3. Find the hosting plan
4. Click **Cancel** or **Do not renew**
5. Choose a date (can keep it running until billing cycle ends)

No rush to do this immediately. The site can run on both for a while to ensure smooth transition.

## Next Steps

See `HUGO_MIGRATION.md` for post-migration enhancements like:
- Category filtering UI
- Reading time estimates
- Series navigation
- Table of contents
- Search functionality
