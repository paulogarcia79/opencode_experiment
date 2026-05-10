# [Slice 1] Upload API + Storage Backend + Nginx Serving

**GitHub Issue:** #1
**Labels:** needs-triage
**State:** open

## Parent

PRD: Image Upload Feature

## What to build

A complete vertical slice for uploading and serving images. Includes the ImageAsset data model, a file storage service, upload endpoint with validation, and Nginx routing to serve uploaded files.

## Acceptance criteria

- [ ] ImageAsset SQLModel with fields: id (UUID), filename, original_name, mime_type, size_bytes, storage_path, url, created_at, updated_at
- [ ] Migration script for image_assets table
- [ ] LocalFileSystemStorage service with year/month directory layout
- [ ] POST /api/admin/images endpoint accepting multipart/form-data
- [ ] File validation: allowed types (jpg, png, gif, webp), max size 5MB
- [ ] Nginx dev config routes /uploads/ to local storage
- [ ] Docker Compose mounts uploads/ as persistent volume
- [ ] Tests: unit tests for storage service, integration test for upload endpoint

## Blocked by

None - can start immediately
