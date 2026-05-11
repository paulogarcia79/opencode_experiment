## Parent

PRD: Markdown Import (prd/PRD-markdown-import.md)

## What to build

Extend the markdown import service to download remote images found in Markdown content and store them locally via the existing `storage_service`. Rewrite image URLs in the TipTap JSON to point to local `/uploads/...` paths. On download failure, keep the original remote URL intact so the article still imports successfully.

## Acceptance criteria

- [x] Remote image URLs extracted from Markdown before conversion (both `![alt](url)` and `<img src="url">` patterns)
- [x] Images downloaded via `httpx` and saved via `storage_service.save()` (year/month directory layout)
- [x] Image src rewritten in TipTap JSON to local `/uploads/...` URL
- [x] Already-local URLs (starting with `/uploads/`) left unchanged
- [x] Download failures (404, network error, invalid content type) leave original URL intact
- [x] Failed image downloads logged as warnings in the per-file error list but do not block article import
- [x] Only allowed image MIME types downloaded (matching `settings.ALLOWED_IMAGE_TYPES`)

## Blocked by

- #1 - Backend Import Service + Endpoint

## Implementation Notes

- Fixed HTML parser bug: added `</p>` closing tag handler in `_close_block("paragraph")`
- Added `_download_remote_images()` and `_walk_and_download()` functions
- Added `_extension_from_mime()` helper
- 4 new tests: download success, local URL skip, download failure fallback, invalid MIME type rejection
- All 162 tests pass
