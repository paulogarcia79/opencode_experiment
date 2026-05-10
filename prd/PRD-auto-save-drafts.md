---
title: "Auto-Save Drafts"
labels:
  - needs-triage
---

# PRD: Auto-Save Drafts

## Problem Statement

When writing articles in the admin editor, authors must manually click "Create Article" or "Update Article" to persist their work. If they navigate away from the page, close the browser tab, or experience a crash before saving, all unsaved content is lost. This is especially painful for long-form writing sessions and for new articles that do not yet have a database record.

## Solution

Introduce automatic background saving of article drafts. As the author types, the system periodically persists the draft to the backend without any explicit action. A subtle status indicator communicates save state (saving, saved, failed). For brand-new articles, the first auto-save creates the draft and seamlessly redirects the browser to the edit URL.

## User Stories

1. As an admin author, I want my article draft to be saved automatically as I type, so that I don't lose work if I forget to click save.
2. As an admin author, I want auto-save to work for brand-new articles before I have manually created them, so that I can start writing without worrying about an initial save.
3. As an admin author, I want to see a subtle indicator that my draft has been saved, so that I have confidence my work is persisted.
4. As an admin author, I want the system to retry automatically if an auto-save fails temporarily, so that transient network issues don't interrupt my flow.
5. As an admin author, I want to be notified if auto-save has persistently failed, so that I know my work is at risk and can take action.
6. As an admin author, I want auto-save to never accidentally publish my article, so that I remain in control of when content goes live.
7. As an admin author, I want auto-save to skip saving when I haven't made any changes, so that the system doesn't waste resources.
8. As an admin author, I want auto-save to skip saving completely empty drafts, so that my admin article list isn't cluttered with blank entries.
9. As an admin author, I want to start writing content before entering a title and still have auto-save kick in after a reasonable delay, so that my creative flow isn't blocked by form requirements.
10. As an admin author, I want the publish and newsletter toggle states to remain unaffected by auto-save, so that my publish intentions are only executed when I explicitly choose to publish.
11. As an admin author, I want the article editor to redirect to the proper edit URL after the first auto-save creates a new draft, so that I can bookmark or refresh the page safely.
12. As a reader, I want auto-saved drafts to never appear on the public site, RSS feed, sitemap, or search results, so that unfinished work is never visible.

## Implementation Decisions

### Modules to Build or Modify

**Auto-Save Service (Backend -- new deep module)**
Encapsulates all logic for persisting a draft article. Responsibilities: enforce `status = "draft"`, generate a unique slug for new articles, create or update the article record, handle tag associations, rebuild search text, and return a lightweight response. This module isolates draft persistence from the main article update flow (which triggers newsletters and enforces publish rules).

**Auto-Save API Endpoints (Backend -- new thin layer)**
- `POST /api/admin/articles/autosave` -- Creates a new draft article. Returns the generated article ID and slug.
- `PUT /api/admin/articles/{id}/autosave` -- Updates an existing draft. Returns a minimal success payload.

These endpoints require admin authentication, accept the same content fields as normal article creation, but unconditionally set `status = "draft"` and bypass all newsletter-sending logic.

**`useAutoSave` Composable (Frontend -- new deep module)**
Encapsulates the entire auto-save lifecycle. Responsibilities: detect form changes, debounce user input (2 seconds after idle), heartbeat force-save (every 30 seconds if dirty), determine if the form is empty or unchanged since last save, call the appropriate auto-save endpoint, manage retry logic with exponential backoff, expose reactive status and error states, and handle the first-save redirect for new articles.

Interface: accepts reactive refs to the form data and article ID, returns `{ status, error, retry, lastSavedAt }`.

**Admin Article Edit View (Frontend -- modified integration layer)**
Integrates `useAutoSave`. Renders the subtle status indicator. On first successful auto-save of a new article, pushes the browser to `/admin/articles/{id}/edit` so subsequent saves target the correct article.

**Admin API Client (Frontend -- thin extension)**
Adds thin wrapper functions for the two auto-save endpoints to the existing admin API module.

### Trigger Strategy

Hybrid timing:
- **Debounced save**: 2 seconds after the user stops typing (detected via form model changes).
- **Heartbeat save**: Every 30 seconds if the form has pending changes and no save is in flight.

### Payload & Scope

Auto-save payload includes: `title`, `description`, `content` (TipTap JSON), `tag_names`.
Excluded: `status`, `send_newsletter`, `published_at`. The backend endpoint always forces `status = "draft"`.

### First-Save Behavior for New Articles

Auto-save is deferred until the draft has meaningful content: either a non-empty title, or 60 seconds of active editing with non-empty body content. While deferred, the UI shows a subtle hint encouraging a title entry. Once the threshold is met, the first auto-save creates the article and triggers a client-side route redirect.

### Empty & Unchanged Detection

Before triggering any save, the composable checks:
1. Is the form effectively empty (no title, no description, no content beyond a single empty paragraph, no tags)? If so, skip.
2. Is the current form data byte-equal to the last successfully saved payload? If so, skip.

### Retry & Failure Strategy

Hybrid retry:
- On failure, automatically retry up to 3 times with exponential backoff (1s, 2s, 4s).
- After exhausting retries, transition to a persistent failure state exposed to the UI.
- The user can click a manual retry button or simply continue typing (changes remain in memory, at risk only on page unload).

### Data Model & Schema

No database schema changes. The existing `Article` table is reused. Auto-saved drafts are rows with `status = "draft"`. The `updated_at` timestamp serves as the last-modified time.

### Persistence Strategy

Backend-only. No `localStorage` or `sessionStorage` is used. This avoids synchronization complexity and ensures the server is the single source of truth.

## Testing Decisions

**What makes a good test:** Tests should verify external behavior, not internal timer implementation. For the composable, this means asserting on the exposed status ref after simulating user input and advancing fake timers. For the backend, this means asserting on the database state and response shape after calling the service/endpoint.

**Modules to test:**

1. **Auto-Save Service (backend integration tests)** -- Test creating a new draft via auto-save, updating an existing draft, enforcing draft status even if a published status is passed, handling tag associations, generating slugs, and returning correct IDs.
2. **Auto-Save Endpoints (backend integration tests)** -- Test auth rejection, validation of tag limits, response payloads, and that published articles are unaffected.
3. **`useAutoSave` Composable (frontend unit tests)** -- Test dirty detection, debounce timing (with Vitest fake timers), heartbeat timing, empty-form suppression, retry backoff sequence, status state transitions, and first-save redirect callback.
4. **Admin Article Edit View (frontend unit tests)** -- Test that the status indicator renders correctly for each composable state, and that the route redirect occurs after first save.

**Prior art:** The codebase already has tests for `useImageUpload`, `useReadingTime`, and `useHead` composables using Vitest fake timers. The backend uses pytest with FastAPI `TestClient` and an in-memory SQLite database.

## Out of Scope

- `localStorage` or offline-first fallback.
- Revision history or restore-to-previous-version.
- Concurrent editing / conflict resolution (last-write-wins).
- Auto-save for any forms other than the article editor.
- Scheduled publishing.
- Markdown import.
- Changes to the database schema.
- Persisting the "publish immediately" or "send newsletter" toggle states across reloads.

## Further Notes

- The existing `updated_at` field on `Article` will advance on every auto-save. If the admin article list needs to distinguish "manually saved" from "auto-saved" in the future, a separate `last_autosaved_at` column can be added without breaking this design.
- The slug generation for new auto-saved drafts should use the same `generate_slug` utility as manual creation, ensuring uniqueness.
- Because auto-save bypasses newsletter logic, the existing `PUT /api/articles/{id}` endpoint should remain untouched for explicit publish actions.
