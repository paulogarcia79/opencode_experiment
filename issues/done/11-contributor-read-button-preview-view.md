## Parent

PRD: `prd/PRD-post-launch-fixes.md`

## What to build

Add a "Read" button to each card on the Contributor Cards dashboard. Create a new `ArticlePreviewView` component and route (`/contributor/articles/:id/preview`) that renders the article's TipTap JSON content as HTML in a clean reading layout. The preview fetches the article via `GET /api/admin/articles/{id}`, renders it using the `@tiptap/html` package, and is accessible regardless of article status. Write Vitest tests.

**End-to-end behavior**: A contributor clicks "Read" on a draft card → navigates to `/contributor/articles/{id}/preview` → sees their article rendered as HTML with "Back to Dashboard" link → clicks back → returns to card grid.

## Acceptance criteria

- [ ] `ContributorCardsView`: each card has a "Read" button with a neutral outline style
- [ ] "Read" button links to `/contributor/articles/{id}/preview`
- [ ] New route registered: `/contributor/articles/:id/preview` under the contributor namespace
- [ ] `ArticlePreviewView.vue` fetches article from `GET /api/admin/articles/{id}`
- [ ] Renders `content` (TipTap JSON) to HTML using the `@tiptap/html` package (`generateHTML`)
- [ ] Styled to match the public article page aesthetic (same fonts, spacing, dark background)
- [ ] Shows article title and status badge at top
- [ ] "Back to Dashboard" link at top navigates to `/contributor`
- [ ] Works for all article statuses: draft, pending_review, published, rejected
- [ ] Loading and error states handled
- [ ] Frontend tests (Vitest): "Read" button renders on cards, preview view renders HTML from TipTap JSON

## Blocked by

- Issue 10 (Article detail endpoint: author eager-load)
