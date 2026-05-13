## Parent

PRD: `prd/PRD-post-launch-fixes.md`

## What to build

Fix the admin article detail endpoint (`GET /api/admin/articles/{id}`) to eager-load the author relationship and include it in the response. Currently the endpoint uses `session.get(Article, article_id)` without `selectinload`, so `article.author` is never loaded and the response has no author info. This causes the contributor redirect bug: `article.author?.id` is `undefined`, so the ownership check `article.author?.id !== store.user?.id` always evaluates to `true`, redirecting the contributor to their dashboard even for their own article. Write a pytest test.

**End-to-end behavior**: A contributor opens their own article in the editor → author info is present in the API response → ownership check passes → editor loads normally without redirect.

## Acceptance criteria

- [ ] `GET /api/admin/articles/{id}` uses `selectinload(Article.author)` when loading the article
- [ ] Response includes `author: { id, email }` dict (matching the pattern of other endpoints like list and review queue)
- [ ] Contributor still gets 404 when requesting a non-owned article (existing behavior preserved)
- [ ] Backend test (pytest): detail endpoint response includes `author` field with `id` and `email`

## Blocked by

None - can start immediately
