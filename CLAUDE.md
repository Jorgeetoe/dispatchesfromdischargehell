# Site Guardrails

This repository is a content-first Jekyll site built on the Chirpy theme.

Default posture:
- Preserve the current site structure, information architecture, navigation, styling direction, and Chirpy-based template.
- Make the smallest change that solves the requested problem.
- Do not redesign, restructure, or replace the theme unless the user explicitly asks.

Do not change these without explicit instruction:
- Chirpy theme choice, site layout, and overall presentation
- `_config.yml` structure, permalink patterns, `url`, `baseurl`, tabs, categories, and navigation order
- `index.html`, `_tabs/`, `_includes/`, `_plugins/`, deployment workflow, and shared templates
- Post filenames, URLs, redirects, and content organization

Theme integrity rule:
- Use Chirpy's built-in configuration, data, front matter, and content hooks before touching shared theme includes or layouts.
- Avoid one-off template overrides when the same fix can be made through normal Chirpy extension points.
- Ask before changing a shared include or layout.

Allowed without extra confirmation when directly relevant:
- Fix broken links, redirects, metadata, accessibility, build issues, or deployment issues
- Make requested content edits to posts and pages
- Apply small technical fixes that preserve the existing design and structure

Ask first before:
- Moving files or reorganizing content
- Adding or removing navigation items, tabs, categories, or collections
- Changing layouts, CSS, shared templates, or the site’s visual design
- Altering permalink strategy, canonical URL behavior, or page hierarchy for non-bug reasons

When uncertain, preserve the current site and ask before making structural or visual changes.
