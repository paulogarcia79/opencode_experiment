# [Slice 4] Tag Search Integration

**GitHub Issue:** #009e
**Labels:** needs-triage
**State:** open

## Parent

PRD: Article Tags (`PRD-article-tags.md`)

## What to build

Include tags in the full-text search index. Update `build_search_text()` to concatenate tag names alongside title, description, and content. Ensure `update_article` rebuilds `search_text` when tags are changed. Verify that the existing `GET /api/articles/search?q=term` endpoint finds articles tagged with the search term even if the word doesn't appear in the article body. Tag matches should rank below title/description matches in the relevance heuristic.

## Acceptance criteria

- [ ] `build_search_text()` includes tag names in the searchable text
- [ ] Updating an article's tags triggers a `search_text` rebuild
- [ ] Searching for a tag name finds articles tagged with that name even if the word is not in title/description/content
- [ ] Tag matches rank below title/description matches in SQLite relevance scoring
- [ ] Backend tests verify search finds articles by tag
- [ ] Backend tests verify tag matches rank below title matches

## Blocked by

- #009a ([Slice 1a] Tag Schema and Basic Article Tagging) — needs tag model and article tagging
