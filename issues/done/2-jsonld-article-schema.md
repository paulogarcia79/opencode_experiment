## Parent

PRD: JSON-LD Structured Data (prd/PRD-jsonld-structured-data.md)

## What to build

Add `Article` JSON-LD schema to `ArticleView.vue` by passing structured data to `useHead`. Includes headline, description, datePublished, dateModified, author, publisher, and mainEntityOfPage.

## Acceptance criteria

- [ ] `ArticleView.vue` passes `jsonLd` to `useHead` with `Article` schema
- [ ] Schema includes: `@context`, `@type: "Article"`, `headline`, `description`, `datePublished`, `dateModified`, `author` (Organization), `publisher` (Organization), `mainEntityOfPage`
- [ ] JSON-LD script tag is visible in DOM when article page loads
- [ ] All existing tests continue to pass
- [ ] `cd frontend && npm run test` passes

## Blocked by

- #1-jsonld-useHead-extension.md
