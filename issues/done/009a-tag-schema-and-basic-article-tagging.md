# [Slice 1a] Tag Schema and Basic Article Tagging

**GitHub Issue:** #009a
**Labels:** needs-triage
**State:** open

## Parent

PRD: Article Tags (`PRD-article-tags.md`)

## What to build

The foundational schema and basic tagging flow. Create `tags` and `article_tags` tables via Alembic migration. Add `Tag` model with SQLModel `Relationship` on `Article`. Build tag service with case-insensitive `get_or_create_tags()` and auto-generated slugs. Wire article create/update endpoints to accept `tag_names`. Eager-load tags on all article GET responses. On the frontend, add a simple comma-separated tag input to the article edit form, and display tag names as plain-text badges on the article detail page.

## Acceptance criteria

- [ ] Alembic migration adds `tags` table (id, name, slug, created_at) and `article_tags` link table (article_id, tag_id, composite PK)
- [ ] `Tag` model uses SQLModel `Relationship(link_model=ArticleTag)` — first use of this pattern in the codebase
- [ ] `get_or_create_tags(session, names)` is case-insensitive and auto-generates slugs
- [ ] Creating an article with `tag_names: ["docker", "vue"]` returns the article with `tags: [{name, slug}]` in response
- [ ] Updating an article replaces existing tags with the new set
- [ ] Article detail page shows tag names as plain-text badges below the metadata row
- [ ] Backend tests verify tag creation, case-insensitive deduplication, and slug generation
- [ ] Frontend tests verify tag badges render on article detail page

## Blocked by

None - can start immediately
