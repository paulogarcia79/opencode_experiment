## Parent

PRD: [PRD-article-revision-history.md](../prd/PRD-article-revision-history.md)

## What to build

Create the `ArticleRevision` SQLModel and the Alembic migration to add the `article_revisions` table. This is the foundation for the entire revision history feature.

The table stores snapshots of article content at meaningful points in time (explicit saves, publishes, restores).

## Acceptance criteria

- [ ] `ArticleRevision` model in `app/models/article_revision.py` with fields: `id` (UUID PK), `article_id` (UUID FK to articles), `version_number` (int), `title` (str), `content` (JSON), `description` (text, nullable), `tag_names` (JSON array), `change_type` (str: "save"/"publish"/"restore"), `created_at` (datetime)
- [ ] Foreign key relationship to `Article` with `ondelete="CASCADE"` so revisions are deleted when the article is deleted
- [ ] Index on `article_id` for efficient lookups
- [ ] Model exported in `app/models/__init__.py`
- [ ] Alembic migration generated and verified (run `just migrate` successfully)
- [ ] Model imported in `alembic/env.py` so autogenerate works

## Blocked by

None - can start immediately
