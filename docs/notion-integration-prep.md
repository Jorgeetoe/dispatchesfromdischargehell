# Notion Integration Prep

This site should treat Notion as an editorial system first, not as the direct publishing engine, unless and until the publishing workflow is proven safe.

That preserves:

- URL stability
- redirect behavior
- Git-based review history
- the current Jekyll/Chirpy structure

## Recommended rollout

### Phase 1: Notion as editorial workspace

Use Notion for:

- editorial calendar
- draft tracking
- source tracking
- post status
- idea backlog

Keep final publishing in this repo.

This is the safest starting point.

### Phase 2: Notion-assisted export

If you later want tighter integration, export approved Notion content into Markdown that is still reviewed and committed here before publish.

Avoid direct auto-publishing at first.

### Phase 3: Optional sync/automation

Only after the above is stable:

- create pages from repo metadata
- sync status fields
- push selected approved drafts into `_posts/`

## Information we will need from you

- whether the integration is for one private workspace or multiple workspaces
- whether Notion is only for planning or also for draft storage
- whether you want one-way sync into the repo or two-way sync
- whether you want manual export, scheduled sync, or webhook-driven sync
- what metadata must live in Notion: title, slug, date, category, description, image, notes, status, etc.

## Suggested Notion schema

One main editorial database is enough to start.

Suggested properties:

- `Title`
- `Slug`
- `Status`
- `Publish Date`
- `Category`
- `Description`
- `Excerpt`
- `Hero Image`
- `Notes Needed`
- `Canonical Post`
- `Stage` (`idea`, `draft`, `editing`, `ready`, `published`)
- `Repo Path`

Optional:

- `Series`
- `Priority`
- `Source Links`
- `Needs Review`

## Technical notes

- Notion integrations need an integration token and explicit page/database access. See [Notion's getting started guide](https://developers.notion.com/docs/create-a-notion-integration).
- Notion's API changed in September 2025 to introduce first-class data sources under databases. See the [2025-09-03 upgrade guide](https://developers.notion.com/docs/upgrade-guide-2025-09-03).
- Notion also offers [webhooks](https://developers.notion.com/reference/webhooks) if you later want status-driven automation.

## Recommendation

Start with:

1. Notion for planning and source management
2. repo Markdown as the publishing source of truth
3. manual or semi-manual export only

That gives you the benefits of Notion without risking site structure, redirects, or deploy behavior.
