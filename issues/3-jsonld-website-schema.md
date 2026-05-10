## Parent

PRD: JSON-LD Structured Data (prd/PRD-jsonld-structured-data.md)

## What to build

Add `WebSite` JSON-LD schema with `SearchAction` to `HomeView.vue` by passing structured data to `useHead`. Enables Google site search integration from SERPs.

## Acceptance criteria

- [ ] `HomeView.vue` passes `jsonLd` to `useHead` with `WebSite` schema
- [ ] Schema includes: `@context`, `@type: "WebSite"`, `name`, `url`, `potentialAction` with `SearchAction`
- [ ] `SearchAction` target uses `{origin}/search?q={search_term_string}` format
- [ ] JSON-LD script tag is visible in DOM when homepage loads
- [ ] All existing tests continue to pass
- [ ] `cd frontend && npm run test` passes

## Blocked by

- #1-jsonld-useHead-extension.md
