## Problem Statement

The Blog + Newsletter Platform MVP launched with a significant content limitation: articles can only reference external image URLs. Authors must upload images to third-party services (Imgur, S3, etc.) and paste URLs into the TipTap editor. This creates friction in the writing workflow, breaks when external URLs expire or change, and prevents offline editing. Readers see broken images when external hosts are unavailable. The platform needs first-class image support to feel like a complete publishing tool.

## Solution

Add native image upload to the platform. Authors drag-and-drop or paste images directly into the TipTap editor. Images upload to a local or S3-backed storage service, persist as first-class assets, and render reliably in both the public blog and newsletter emails. A new admin "Media Library" page lets authors browse, reuse, and delete uploaded images.

## User Stories

### Author Experience

1. As an author writing an article, I want to drag and drop an image into the TipTap editor, so that it appears inline without leaving the editor or managing external URLs.
2. As an author, I want to paste an image from my clipboard into the editor, so that screenshots and copied images appear instantly.
3. As an author, I want to see a loading state while an image uploads, so that I know the system is working and don't accidentally save a broken reference.
4. As an author, I want uploaded images to appear at a reasonable maximum width in the editor, so that the layout remains readable and predictable.
5. As an author, I want to click an inline image to select it and press Delete to remove it, so that I can edit my content naturally.
6. As an author, I want to upload images via a "Media Library" admin page, so that I can prepare assets before writing the article.
7. As an author, I want to browse previously uploaded images in the Media Library and copy their URL, so that I can reuse images across multiple articles.
8. As an author, I want to delete an image from the Media Library, so that I can clean up unused assets and manage storage.

### Reader Experience

9. As a reader viewing a published article, I want images to load quickly and reliably, so that the reading experience is not interrupted by broken external links.
10. As a reader, I want images to be responsive and not overflow the article container on mobile devices, so that the layout stays readable.
11. As a newsletter subscriber, I want article images to appear inline in the email, so that the newsletter feels as rich as the web version.

### System & Admin

12. As a platform operator, I want uploaded images to be validated (type, size), so that malicious or oversized files cannot abuse the system.
13. As a platform operator, I want images to be stored outside the application container, so that deployments and container restarts don't delete user content.
14. As a platform operator, I want image URLs to be served via Nginx (not FastAPI), so that the backend is not bogged down serving static files.
15. As a platform operator, I want configurable storage backends (local filesystem for dev, S3 for production), so that the same code works in both environments.

## Implementation Decisions

### Modules

**Image Upload API (`app/routers/images.py`)**
- `POST /api/admin/images` — Accept multipart upload, validate, store, return public URL
- `GET /api/admin/images` — List all uploaded images (filename, URL, upload date, size)
- `DELETE /api/admin/images/{image_id}` — Delete image from storage and database
- Protected by bearer token auth (existing `require_admin` dependency)

**Image Storage Service (`app/services/image_storage.py`)**
- Deep module abstracting storage backend details
- Interface: `store(file_bytes, filename, content_type) -> public_url`, `delete(url) -> bool`, `list() -> list[ImageAsset]`
- Two implementations: `LocalFileSystemStorage` (dev) and `S3Storage` (prod)
- Selected at runtime via `STORAGE_BACKEND` env var
- Local storage writes to `uploads/` directory mounted as Docker volume
- S3 implementation uses `boto3` with configurable bucket, region, and prefix

**Image Asset SQLModel (`app/models/image_asset.py`)**
- `id` (UUID PK), `filename` (original name), `stored_filename` (UUID-based unique name), `content_type`, `size_bytes`, `url`, `created_at`
- Stored in PostgreSQL for querying and lifecycle management
- `stored_filename` uses UUID to prevent collisions and directory traversal

**TipTap Image Extension Integration**
- The existing TipTap editor already includes the `Image` extension from `StarterKit`
- Add a custom `handleDrop` and `handlePaste` handler to the editor configuration
- On drop/paste: extract File object, upload via `POST /api/admin/images`, insert returned URL as `img` node
- Loading state: insert temporary placeholder node, replace with real image on success

**Nginx Static File Serving**
- In dev: Nginx serves `/uploads/` directly from the mounted volume
- In prod: Nginx serves `/uploads/` from the volume (or from S3 via `proxy_pass` if configured)
- FastAPI never serves image bytes directly

**Newsletter HTML Rendering**
- The existing `tiptap_renderer.py` already handles `image` nodes
- Ensure rendered `<img>` tags use absolute URLs (prepend `APP_BASE_URL` if relative)
- Inline styles for email client compatibility: `max-width: 100%; height: auto; display: block;`

### Validation Rules

- Allowed types: `image/jpeg`, `image/png`, `image/webp`, `image/gif`
- Max file size: 5 MB per image
- Max total storage per platform: configurable via env (default 1 GB)
- Reject files with mismatched extension and magic bytes

### Storage Layout (Local)

```
uploads/
  2025/
    05/
      a1b2c3d4-e5f6-7890-abcd-ef1234567890.jpg
      b2c3d4e5-f6a7-8901-bcde-f23456789012.png
```

Organized by year/month to prevent single-directory overload.

## Testing Decisions

**Backend Tests**
- Test the storage service interface with an in-memory implementation (no real disk/S3 needed for unit tests)
- Test upload endpoint with `TestClient` and `UploadFile` mock: validate 200 for valid image, 400 for oversized, 400 for invalid type
- Test `ImageAsset` CRUD: create record, query list, delete cascades from storage
- Test TipTap renderer: ensure `image` nodes produce valid `<img>` tags with absolute URLs

**Frontend Tests**
- Test Media Library component: renders image grid, delete button triggers API call
- Test TipTap editor drop handler: simulate drop event, verify upload API called, verify node inserted
- Mock `fetch` for upload endpoint to test loading and success states

**Integration Tests**
- End-to-end: upload image via admin API → verify file exists on disk → verify URL is accessible via Nginx → verify image appears in article HTML and newsletter HTML

## Out of Scope

- Image resizing / thumbnails (keep original size only)
- Image optimization (compression, WebP conversion)
- CDN integration (CloudFront/Cloudflare) — S3 direct URLs are acceptable for this phase
- SVG support (complex security considerations)
- Image captions or alt-text editing UI (can be added to TipTap later)
- Bulk upload (single-file uploads only)
- Usage analytics (which images are used in which articles)

## Further Notes

- The existing `Article.content` JSON already supports `image` nodes via TipTap's default schema — no database migration needed
- The existing `docker-compose.dev.yml` should add a volume mount for `./uploads:/app/uploads`
- The `.env.example` should gain: `STORAGE_BACKEND=local`, `UPLOADS_DIR=/app/uploads`, `MAX_UPLOAD_SIZE=5242880`, `S3_BUCKET=`, `S3_REGION=`, `S3_ACCESS_KEY=`, `S3_SECRET_KEY=`
- Consider rate limiting on the upload endpoint to prevent abuse (deferred to a separate infrastructure change)
