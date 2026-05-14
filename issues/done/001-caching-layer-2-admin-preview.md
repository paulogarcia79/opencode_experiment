## Parent

prd/PRD-caching-layer.md

## What to build

Create a new `GET /api/admin/articles/preview/{slug}` backend endpoint that allows authenticated admins/editors to view unpublished drafts. Remove the authentication-bypass logic from the public `GET /api/articles/{slug}` endpoint so it strictly serves published articles. Update the Vue frontend so admin preview buttons/links route to the new preview endpoint. This ensures drafts are never accidentally cached or served publicly.

## Acceptance criteria

- [ ] New `GET /api/admin/articles/preview/{slug}` endpoint exists and requires authentication.
- [ ] Public `GET /api/articles/{slug}` strictly returns 404 for unpublished drafts, regardless of authentication.
- [ ] Vue frontend uses the new preview endpoint for admin previews.
- [ ] Admins can still preview unpublished drafts successfully.

## Blocked by

None - can start immediately
