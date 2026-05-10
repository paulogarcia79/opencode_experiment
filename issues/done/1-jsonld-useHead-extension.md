## Parent

PRD: JSON-LD Structured Data (prd/PRD-jsonld-structured-data.md)

## What to build

Extend the `useHead` composable to support JSON-LD structured data injection. Add `jsonLd` to the `HeadMeta` interface, inject/update a `<script type="application/ld+json">` tag when provided, and ensure `resetHead` removes the tag. Tests added to `useHead.spec.ts`.

## Acceptance criteria

- [ ] `jsonLd?: Record<string, unknown>` added to `HeadMeta` interface
- [ ] `useHead` creates `<script type="application/ld+json">` tag with serialized JSON when `jsonLd` provided
- [ ] Existing JSON-LD script tag is updated (not duplicated) on subsequent `useHead` calls
- [ ] `resetHead` removes the JSON-LD script tag
- [ ] Tests added to `useHead.spec.ts` covering injection, update, and removal
- [ ] All existing tests continue to pass
- [ ] `cd frontend && npm run test` passes

## Blocked by

None - can start immediately
