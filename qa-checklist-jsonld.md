# QA Checklist: JSON-LD Structured Data

## Prerequisites & Setup

- [ ] Dev server running (`just dev` or `just front` + `just back`)
- [ ] At least one published article exists in the database

## Frontend UI Checks

### Homepage JSON-LD

- [ ] **Navigate to** `http://localhost` → **Open browser DevTools Console** → **Expected:** `<script type="application/ld+json">` tag present in `<head>`
- [ ] **Inspect JSON-LD content** → **Expected:** `@type` is `"WebSite"`, `name` is `"Tech & Games Blog"`, `url` matches site origin
- [ ] **Check SearchAction** → **Expected:** `potentialAction` has `@type: "SearchAction"`, `target` contains `/search?q={search_term_string}`

### Article Page JSON-LD

- [ ] **Navigate to any published article** → **Open DevTools Console** → **Expected:** `<script type="application/ld+json">` tag present in `<head>`
- [ ] **Inspect JSON-LD content** → **Expected:** `@type` is `"Article"`, `headline` matches article title, `description` matches article description
- [ ] **Check dates** → **Expected:** `datePublished` and `dateModified` are valid ISO 8601 timestamps
- [ ] **Check author/publisher** → **Expected:** Both are `{ "@type": "Organization", "name": "Tech & Games Blog" }`
- [ ] **Check mainEntityOfPage** → **Expected:** URL matches the article's canonical URL

### Navigation Between Pages

- [ ] **Navigate from homepage to an article** → **Expected:** JSON-LD script tag updates from WebSite schema to Article schema (no duplicate tags)
- [ ] **Navigate back to homepage** → **Expected:** JSON-LD script tag updates back to WebSite schema
- [ ] **Navigate to a non-article page** (e.g., `/search`) → **Expected:** JSON-LD script tag is removed from `<head>`

## Edge Cases & Error Handling

- [ ] **Article with no description** → **Expected:** JSON-LD `description` field is absent or null, page still renders correctly
- [ ] **Article with no tags** → **Expected:** JSON-LD renders without errors, no visible UI breakage

## Integration Checks

- [ ] **Validate with Google Rich Results Test** — Copy article URL into [Google Rich Results Test](https://search.google.com/test/rich-results) → **Expected:** Article schema detected and valid
- [ ] **Validate with Schema Markup Validator** — Copy article URL into [Schema Markup Validator](https://validator.schema.org/) → **Expected:** No errors, Article schema recognized
