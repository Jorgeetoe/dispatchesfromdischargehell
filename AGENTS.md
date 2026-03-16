# Site Guardrails

This repository is a content-first Jekyll site built on the Chirpy theme.

Default posture:
- Preserve the current site structure, information architecture, navigation, styling direction, and Chirpy-based template.
- Make the smallest change that solves the requested problem.
- Treat visual redesigns, theme swaps, layout rewrites, and structural refactors as out of scope unless the user explicitly asks for them.

Do not change any of the following unless explicitly instructed:
- The Chirpy theme selection and overall look and feel
- `_config.yml` structure, permalink patterns, `url`, `baseurl`, categories, tabs, and navigation order
- `index.html`, `_tabs/`, `_includes/`, `_plugins/`, workflow/deploy structure, and content organization
- Post filenames, post URLs, redirects, and archive/category behavior
- Shared templates, page chrome, sidebar, header, footer, and site-wide assets

Theme integrity rule:
- Prefer Chirpy-supported configuration, data, front matter, and content changes before overriding shared theme includes or layouts.
- Do not add one-off template overrides when the same result can be achieved through Chirpy's built-in settings or data files.
- If a shared include or layout truly must change, stop and ask first.

Allowed without extra confirmation when directly relevant to the request:
- Fix broken links, redirects, metadata, validation issues, accessibility issues, and deployment/build problems
- Edit post content, copy, front matter, or tab-page text that the user asked to change
- Add narrowly scoped includes or config changes required to fix a bug without altering the site design or structure

Ask before doing any of the following:
- Reorganizing content or moving files
- Adding or removing tabs, categories, collections, or navigation items
- Changing layouts, templates, or CSS in a way that affects the site's presentation
- Replacing Chirpy behavior with custom UI or custom architecture
- Altering canonical URLs, permalink strategy, or page hierarchy for non-bug reasons

When in doubt:
- Prefer preserving the existing site and ask before making structural or visual changes.
