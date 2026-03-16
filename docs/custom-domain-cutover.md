# Custom Domain Cutover

This repo currently publishes a staging site at:

- `https://jorgeetoe.github.io/dispatchesfromdischargehell/`

It is prepared for a future production launch at:

- `https://dispatchesfromdischargehell.com/`

## How the repo is set up

- [_config.yml](/Users/jorgearenivar/dispatchesfromdischargehell-chirpy/_config.yml) keeps the staging GitHub Pages values.
- [_config.production.yml](/Users/jorgearenivar/dispatchesfromdischargehell-chirpy/_config.production.yml) overrides `url` and `baseurl` for the production domain.
- The Pages workflow switches to the production config automatically when a `CNAME` file exists in the repo root.

## Preview production locally

Run either of these from the repo root:

```bash
bash tools/run.sh -c "_config.yml,_config.production.yml"
```

```bash
bash tools/test.sh -c "_config.yml,_config.production.yml"
```

## Launch steps

1. Add a root-level `CNAME` file containing:

```text
dispatchesfromdischargehell.com
```

2. In GitHub Pages settings for the repo, set the custom domain to:

```text
dispatchesfromdischargehell.com
```

3. Point DNS at GitHub Pages.

For the apex domain, GitHub Pages currently documents using A/AAAA records for GitHub's Pages endpoints. Check GitHub's current docs at launch time before editing DNS.

4. Push the `CNAME` commit.

Once `CNAME` exists, the workflow will build with:

```text
_config.yml,_config.production.yml
```

so canonicals, social metadata, and asset URLs will shift to the production domain automatically.

## Post-launch verification

Check these URLs:

- `https://dispatchesfromdischargehell.com/`
- `https://dispatchesfromdischargehell.com/start-here/`
- `https://dispatchesfromdischargehell.com/telos/`
- `https://dispatchesfromdischargehell.com/blog/posts/2026-01-03-flex-for-me-not-for-thee/`
- `https://dispatchesfromdischargehell.com/sitemap.xml`
- `https://dispatchesfromdischargehell.com/feed.xml`

Confirm:

- canonical URLs use `dispatchesfromdischargehell.com`
- `og:url` and `og:image` point at the production domain
- redirect pages still resolve
- no links retain `/dispatchesfromdischargehell` in production
