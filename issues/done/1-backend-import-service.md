## Parent

PRD: Markdown Import (prd/PRD-markdown-import.md)

## What to build

Backend service and API endpoint for importing Markdown files. Install `markdown-it-py`, build `markdown_import_service.py` that parses YAML frontmatter, converts GFM Markdown to TipTap JSON, and creates draft articles via the existing `create_article()`. Add `POST /api/admin/articles/import` endpoint accepting multipart form with multiple files. Handle slug conflicts via auto-rename, auto-create tags, always import as draft.

## Acceptance criteria

- [x] `markdown-it-py` added to `pyproject.toml` with GFM plugins (tables, linkify, strikethrough)
- [x] `markdown_import_service.py` exists with `import_markdown_files(files) -> ImportResult` interface
- [x] YAML frontmatter parsed: title, description, tags, slug extracted; missing title falls back to filename
- [x] GFM Markdown converted to TipTap JSON: headings (h2/h3), paragraphs, lists, blockquotes, code blocks, links, bold/italic, tables
- [x] `POST /api/admin/articles/import` endpoint accepts multipart form with multiple `.md` files
- [x] Endpoint requires admin auth (401 without token)
- [x] Imported articles always created as draft status
- [x] Slug conflicts auto-resolved by appending counter (e.g., `my-post-2`)
- [x] Unknown tags auto-created during import
- [x] Response returns `{successes: [{id, title, slug}], errors: [{filename, error}], total}`
- [x] Per-file errors collected without aborting the batch
- [x] Schemas added to `schemas.py`: `ImportSuccessItem`, `ImportErrorItem`, `ImportResult`

## Blocked by

None - can start immediately

## Implementation Notes

- Added `markdown-it-py>=3.0.0` and `python-frontmatter>=1.1.0` to pyproject.toml
- Created `app/services/markdown_import_service.py` with HTML-to-TipTap converter
- Added endpoint at `POST /api/admin/articles/import` in articles router
- Added 3 schemas to `app/schemas.py`
- 5 tests in `tests/test_markdown_import.py`: auth, single import, slug conflict, filename fallback, mixed results
- All 158 tests pass
