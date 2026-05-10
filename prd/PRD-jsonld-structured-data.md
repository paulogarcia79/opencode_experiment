## Problem Statement

Search engines cannot fully understand the blog's content structure. While meta tags (title, description, OpenGraph, Twitter Cards) are implemented, there is no JSON-LD structured data on any page. This means Google and other search engines miss critical context about articles (author, publish date, content type) and the site's search capability. Rich search results (article cards, site search boxes in SERPs) are unavailable, reducing click-through rates and discoverability.

## Solution

Add JSON-LD structured data to article detail pages and the homepage. The `useHead` composable is extended to manage a `<script type="application/ld+json">` tag alongside existing meta tags. Article pages get `Article` schema with headline, description, dates, author, and publisher. The homepage gets `WebSite` schema with a `SearchAction` to enable Google site search integration.

## User Stories

1. As a search engine crawler, I want to see `Article` structured data on article pages, so that I can display rich search results with author, date, and description
2. As a reader searching on Google, I want to see article metadata (author, publish date) in search results, so that I can evaluate article credibility before clicking
3. As a search engine crawler, I want to see `WebSite` structured data on the homepage, so that I can understand the site's identity and purpose
4. As a reader searching on Google, I want to see a site search box in search results, so that I can search the blog directly from Google
5. As a developer, I want JSON-LD injection handled by the existing `useHead` composable, so that head management stays centralized
6. As a developer, I want the JSON-LD script to be cleared when navigating away from pages, so that stale structured data doesn't leak between routes
7. As a developer, I want the `resetHead` function to also clear JSON-LD, so that navigation to non-article pages has clean head state
8. As a developer, I want the `HeadMeta` interface to accept a `jsonLd` object, so that structured data is type-safe and validated at compile time
9. As a content creator, I want article structured data to include `dateModified`, so that search engines know when content was last updated
10. As a future developer, I want the JSON-LD system to be extensible, so that adding cover image and BreadcrumbList schemas later is straightforward

## Implementation Decisions

### Modules

**useHead Composable (Extended)**
- Add `jsonLd?: Record<string, unknown>` to the `HeadMeta` interface
- When `jsonLd` is provided, inject a `<script type="application/ld+json">` tag with the serialized JSON
- If a JSON-LD script tag already exists, update its content (not create a duplicate)
- `resetHead()` removes the JSON-LD script tag entirely

**ArticleView**
- Pass `jsonLd` to `useHead` with `Article` schema:
  - `@context`: "https://schema.org"
  - `@type`: "Article"
  - `headline`: article title
  - `description`: article description
  - `datePublished`: article.published_at (ISO 8601)
  - `dateModified`: article.updated_at (ISO 8601)
  - `author`: { "@type": "Organization", "name": "Tech & Games Blog" }
  - `publisher`: { "@type": "Organization", "name": "Tech & Games Blog" }
  - `mainEntityOfPage`: canonical URL

**HomeView**
- Pass `jsonLd` to `useHead` with `WebSite` + `SearchAction` schema:
  - `@context`: "https://schema.org"
  - `@type`: "WebSite"
  - `name`: "Tech & Games Blog"
  - `url`: site origin
  - `potentialAction`: { "@type": "SearchAction", "target": "{origin}/search?q={search_term_string}", "query-input": "required name=search_term_string" }

### Schema Design

The `jsonLd` parameter accepts any `Record<string, unknown>`, allowing any Schema.org type to be passed. This is intentionally flexible — the interface rarely changes, but the objects passed to it vary by page type.

### Author/Publisher

Uses `{ "@type": "Organization", "name": "Tech & Games Blog" }` as a placeholder. When multi-author support is added, this will be updated to use real author data.

### Date Fields

Both `datePublished` and `dateModified` are included. The Article model already has `published_at` and `updated_at` fields, so no schema changes are needed.

## Testing Decisions

**What makes a good test:** Test that `useHead` correctly creates/updates/removes the JSON-LD script tag. Verify the serialized JSON matches the expected schema structure. Do not test DOM manipulation internals — test the observable result (script tag exists with correct content).

**Modules to test:**
- `useHead` composable: verify JSON-LD script tag is created with correct content, verify existing tag is updated (not duplicated), verify `resetHead` removes the tag
- No view-level tests needed — ArticleView and HomeView already test that `useHead` is called; the JSON-LD parameter is just another argument

**Prior art:**
- `frontend/src/composables/__tests__/useHead.spec.ts` already tests meta tag creation and updates
- Same pattern applies: verify `document.querySelector` finds the expected element with correct attributes

## Out of Scope

- **Cover image field** — Will be added as a separate change. When implemented, `image` will be added to the Article JSON-LD schema.
- **BreadcrumbList schema** — Deferred. Low SEO impact for a single-level blog.
- **Real author data** — Placeholder organization used until multi-author support is implemented.
- **Backend changes** — No API or database changes needed; all existing fields are available.
- **Other Schema.org types** — `BlogPosting`, `Blog`, `ListItem` etc. deferred to future enhancements.

## Further Notes

- The `updated_at` field exists in the Article model but is always set to `datetime.utcnow` on creation and update. It is already populated and usable for `dateModified`.
- The JSON-LD script tag uses `type="application/ld+json"` — this is the standard format recognized by Google, Bing, and other search engines.
- Google's Structured Data Testing Tool can be used to validate the output once deployed.
- When cover image is added later, the Article schema should also include `image` with the cover image URL.
