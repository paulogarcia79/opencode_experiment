# [Slice 8b] Search Frontend UI

**GitHub Issue:** #008b
**Labels:** needs-triage
**State:** open

## Parent

PRD: Full-Text Search (`PRD-full-text-search.md`)

## What to build

A complete search experience in the Vue frontend: a search input in the site header, a dedicated `/search` results page with instant debounced search, loading skeleton states, and themed empty states. Uses the backend `/api/articles/search?q=term` endpoint.

## Acceptance criteria

- [ ] Search composable with 300ms debounce, loading state, error state, result caching
- [ ] `useSearch` exposes: `query`, `results`, `loading`, `error`, `search(term)`
- [ ] Search input in site header (compact icon expanding to input on click/focus)
- [ ] Header search navigates to `/search?q=term` on Enter/submit
- [ ] Dedicated `/search` page with prominent search input pre-filled from URL `?q=`
- [ ] Search page renders results as article cards matching homepage card style
- [ ] Search page shows loading skeleton while fetching
- [ ] Search page shows themed empty state when no results
- [ ] Search only triggers when query length >= 2 characters
- [ ] Frontend tests: verify debounced fetch, results render, empty state, loading state, input pre-fills from URL

## Blocked by

- #008a ([Slice 8a] Search Backend & API) — requires the `/api/articles/search?q=term` endpoint to exist
