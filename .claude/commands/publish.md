# /publish — Deploy to Hostinger

Deploy the site to Hostinger via FTP.

## Steps

**1. Check FTP credentials**
Verify these environment variables are set:
- `DISPATCHES_FTP_HOST`
- `DISPATCHES_FTP_USER`
- `DISPATCHES_FTP_PASS`

If any are missing, show how to set them and stop.

**2. Show changes**
List files in `site/` that were modified today or since the last deploy. Give a quick summary of what's going out.

**3. Confirm**
Ask Jorge to confirm before deploying.

**4. Deploy**
Run `config/deploy.sh` to mirror `site/` to `/public_html/` via lftp.

**5. Report**
Show the deploy result — files uploaded, any errors, and the live URL of the most recently staged post.

## Example Flow

```
$ /publish

Checking FTP credentials... ✓
Credentials found.

Changes to deploy (since last deploy):
  ✓ site/blog/posts/2026-02-26-she-knew-and-she-didnt-say-anything.html (modified)
  ✓ site/blog/index.html (modified)
  ✓ site/feed.xml (regenerated)

Ready to deploy 3 files to dispatchesfromdischargehell.com?
Confirm? [y/n]

Deploying...
================================================
Transferring file `blog/posts/2026-02-26-she-knew-and-she-didnt-say-anything.html'
Transferring file `blog/index.html`
Transferring file `feed.xml`
================================================
DEPLOYED ✓

Live URLs:
  Homepage: https://dispatchesfromdischargehell.com
  Latest post: https://dispatchesfromdischargehell.com/blog/posts/2026-02-26-she-knew-and-she-didnt-say-anything.html
```
