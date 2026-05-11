## Problem Statement

As a blog admin, I want to import existing articles written in Markdown format (from Hugo, Jekyll, Ghost, WordPress exports, or plain `.md` files) so that I can migrate my content to this platform without manually copying and reformatting each article.

## Solution

A dedicated Markdown import feature that accepts single or bulk `.md` file uploads, parses YAML frontmatter for metadata, converts GFM content to TipTap JSON, downloads remote images to local storage, and creates draft articles ready for review and publishing.

## User Stories

1. As an admin, I want to upload a single Markdown file so that I can quickly import one article
2. As an admin, I want to upload multiple Markdown files at once so that I can bulk-import articles during a migration
3. As an admin, I want the system to extract title, description, tags, and slug from YAML frontmatter so that I don't have to re-enter metadata manually
4. As an admin, I want imported articles to always be created as drafts so that I can review and edit them before publishing
5. As an admin, I want remote images in Markdown to be downloaded and stored locally so that my articles are self-contained
6. As an admin, I want image download failures to fall back to the original URL so that a broken image doesn't block the entire article import
7. As an admin, I want slug conflicts to be auto-resolved by appending a counter so that imports don't fail over duplicate titles
8. As an admin, I want unknown tags to be auto-created so that I don't have to pre-create tags before importing
9. As an admin, I want to see a summary of import results with links to each imported article so that I can review them
10. As an admin, I want to see a list of failed imports with error reasons so that I can fix and re-import them
11. As an admin, I want GFM features (tables, strikethrough, task lists) to be converted correctly so that my content renders faithfully
12. As an admin, I want code blocks with language hints to be preserved so that syntax highlighting works in the editor
13. As an admin, I want headings, paragraphs, lists, blockquotes, links, and bold/italic formatting to be converted so that my article structure is preserved
14. As an admin, I want a dedicated `/admin/import` page with drag-and-drop upload so that the import process is intuitive
15. As an admin, I want the import page to show progress while files are being processed so that I know the system is working
16. As an admin, I want the import page to have a link back to the articles list so that I can navigate easily

## Implementation Decisions

### Backend Modules

1. **`markdown_import_service.py`** — Deep module with a simple interface: `import_markdown_files(files: list) -> ImportResult`. Encapsulates:
   - YAML frontmatter parsing (extract title, description, tags, slug, date)
   - GFM Markdown to TipTap JSON conversion via `markdown-it-py`
   - Remote image downloading and local storage via `storage_service`
   - Article creation via existing `create_article()` service
   - Error collection per file

2. **`POST /api/admin/articles/import`** — Single endpoint accepting multipart form with multiple files. Returns `{successes: [{id, title, slug, edit_url}], errors: [{filename, error}]}`. Requires admin auth.

3. **`schemas.py`** — New schemas:
   - `ImportSuccessItem`: `id`, `title`, `slug`
   - `ImportErrorItem`: `filename`, `error`
   - `ImportResult`: `successes` (list), `errors` (list), `total` (int)

4. **`pyproject.toml`** — Add `markdown-it-py` dependency (with `linkify` and `tables` plugins for GFM support)

### Frontend Modules

1. **`AdminImportView.vue`** — Dedicated page at `/admin/import`:
   - Drag-and-drop file upload area (accepts `.md` files, single + multiple)
   - File input fallback button
   - Upload → Import → Results flow
   - Results section: success count, error count, collapsible error list, links to each imported article in editor
   - "Back to Articles" link

2. **Router** — Add `/admin/import` route under admin layout

3. **`AdminLayout.vue`** — Add "Import" nav link between "Articles" and "Media"

4. **`useMarkdownImport.ts`** — Composable wrapping the import API call, returns `{importFiles, loading, result}`

### Markdown-to-TipTap Conversion

- Use `markdown-it-py` with GFM plugins (tables, linkify, strikethrough)
- Parse Markdown to HTML, then convert HTML AST to TipTap JSON nodes
- Map HTML elements to TipTap nodes: `p` → paragraph, `h1-h6` → heading (levels 2-3 only, matching editor), `ul/ol` → lists, `blockquote` → blockquote, `pre/code` → codeBlock, `table` → table nodes, `img` → image, `a` → link mark, `strong` → bold, `em` → italic, `s/strike` → strikethrough (if TipTap extension added)
- YAML frontmatter: strip from content before parsing, extract fields

### Image Handling

- Regex/AST scan for `<img>` tags or Markdown `![alt](url)` patterns in source
- For each remote URL: download via `httpx`, validate content type, save via `storage_service.save()`
- Rewrite image src in TipTap JSON to local `/uploads/...` URL
- On failure: leave original URL intact, log warning in error list

### Field Mapping

| Frontmatter Key | Article Field | Notes |
|---|---|---|
| `title` | `title` | Required; fallback to filename if missing |
| `description` | `description` | Optional; fall back to auto-generate |
| `tags` / `category` / `categories` | `tag_names` | Normalize: split comma-separated, strip whitespace |
| `slug` | `slug` | Optional; if provided, validate uniqueness; auto-rename on conflict |
| `date` / `published_at` | — | Ignored; always import as draft |
| `draft` | — | Ignored; always import as draft |
| `image` / `featured_image` | — | Skipped (no featured image field in Article model) |

### Conflict Handling

- Title slug conflicts: auto-rename using existing `generate_slug()` pattern (appends `-2`, `-3`, etc.)
- No duplicate detection beyond slug — if same content is imported twice, two articles are created

### Error Handling

- Per-file errors collected, not fatal to batch
- Error types: invalid Markdown, missing title, YAML parse error, image download failure (non-fatal), tag limit exceeded
- Results returned in single response after all files processed

## Testing Decisions

### What Makes a Good Test

- Test external behavior, not implementation details
- Tests should verify: correct TipTap JSON output for given Markdown input, correct frontmatter extraction, correct image download behavior, correct error reporting
- Use real `markdown-it-py` parsing, not mocks

### Modules to Test

1. **`markdown_import_service.py`** — Unit tests:
   - Frontmatter parsing (valid, missing, malformed)
   - GFM → TipTap conversion (headings, paragraphs, lists, code blocks, blockquotes, tables, links, images, bold/italic)
   - Image download (success, failure, already-local URL)
   - Article creation with auto-created tags
   - Slug conflict auto-renaming
   - Error collection and reporting

2. **Import endpoint** — Integration tests via `TestClient`:
   - Single file upload success
   - Multiple file upload with mixed success/failure
   - Admin auth required
   - Response schema validation

3. **Frontend `AdminImportView.vue`** — Component tests via Vitest:
   - File selection triggers import
   - Results display (success + error states)
   - Navigation links render correctly

### Prior Art

- Backend: `tests/test_articles.py`, `tests/test_images.py` — `TestClient` + SQLite in-memory pattern
- Frontend: `frontend/src/components/__tests__/` — Vitest + `@vue/test-utils` pattern (116 existing tests)

## Out of Scope

- Markdown export (converting TipTap JSON back to Markdown)
- WordPress XML (WXR) import
- Medium/Substack/Ghost JSON import
- S3 image storage for imported images
- Live preview before import confirmation
- Respecting frontmatter `date`/`published_at` for auto-publishing
- Image optimization/resizing during import
- Article series / collections
- Bulk edit after import (e.g., "publish all imported")
- TipTap editor tests (deferred, as per existing follow-up.md)
- E2E tests for import flow (deferred, as per existing follow-up.md)

## Further Notes

- The `markdown_import_service.py` should be designed as a deep module — simple interface, encapsulated complexity. This makes it easy to extend later for other import formats (WordPress XML, JSON, etc.) by adding new import functions that reuse the article creation logic.
- The TipTap JSON conversion should handle the same node types that `tiptap_renderer.py` already supports for email rendering, ensuring round-trip compatibility.
- If `markdown-it-py` doesn't natively support a GFM feature (e.g., task lists), the HTML output should be preserved as-is or gracefully degraded rather than failing the import.
- The import page should match the existing dark tech aesthetic: background `#0F0F23`, primary `#7C3AED`, accent `#F43F5E`.
