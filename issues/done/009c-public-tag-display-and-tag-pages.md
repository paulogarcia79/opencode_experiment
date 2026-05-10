# [Slice 2] Public Tag Display and Tag Pages

**GitHub Issue:** #009c
**Labels:** needs-triage
**State:** open

## Parent

PRD: Article Tags (`PRD-article-tags.md`)

## What to build

Make tags discoverable for readers. Tag badges on the article detail page become clickable `RouterLink`s to `/tags/:slug`. Add public endpoints `GET /api/tags/{slug}` and `GET /api/tags/{slug}/articles` that return the tag and its published articles (eager-loaded with tags). Build a new `TagArticlesView` at `/tags/:slug` showing a tag header with article count and a list of article cards reusing the homepage card styling.

## Acceptance criteria

- [ ] Tag badges on `ArticleView` are clickable and navigate to `/tags/:slug`
- [ ] `GET /api/tags/{slug}` returns the tag with its articles
- [ ] `GET /api/tags/{slug}/articles` returns only published articles for that tag
- [ ] `/tags/docker` renders a page with tag name, article count, and article cards
- [ ] Tag page shows empty state when no published articles match
- [ ] Unknown tag slug returns 404
- [ ] Backend tests verify tag page endpoints
- [ ] Frontend tests verify tag badges link correctly and tag page renders articles

## Blocked by

- #009a ([Slice 1a] Tag Schema and Basic Article Tagging) — needs tag model and article tagging
