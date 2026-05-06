## 1. Project Setup & Dependencies

- [x] 1.1 Initialize FastAPI backend structure (`main.py`, settings module, database connection)
- [x] 1.2 Initialize Vue 3 frontend structure (Vite, Tailwind config, router, basic layout)
- [x] 1.3 Add Python dependencies (`fastapi`, `sqlmodel`, `alembic`, `resend`, `pytest`, `httpx`)
- [x] 1.4 Add Node dependencies (`@tiptap/vue-3`, `@tiptap/starter-kit`, `vue-router`, `pinia`, `@vue/test-utils`)

## 2. Database Models & Migrations

- [x] 2.1 Create `User` SQLModel with UUID PK, email, hashed_password, is_admin — seed default admin on startup
- [x] 2.2 Create `Article` SQLModel with UUID PK, title, slug, content (JSON), description, status, send_newsletter, published_at
- [x] 2.3 Create `Subscriber` SQLModel with UUID PK, email, status (pending/active/unsubscribed), confirmation_token
- [x] 2.4 Create `NewsletterSend` SQLModel with UUID PK, article_id, subscriber_id, sent_at
- [x] 2.5 Generate Alembic migration and verify all tables in PostgreSQL

## 3. Backend Core API

- [x] 3.1 Implement bearer token auth dependency (`ADMIN_API_TOKEN` env var) with tests
- [x] 3.2 Implement Article CRUD router (POST/PUT/DELETE admin, GET public by slug) with tests
- [x] 3.3 Implement public article list endpoint (only `published`, ordered by `published_at` desc) with tests
- [x] 3.4 Implement slug generation and collision handling (`-2`, `-3`) with tests

## 4. Subscriber & Email Service

- [x] 4.1 Configure Resend client and create email template utilities (confirmation, newsletter, unsubscribe)
- [x] 4.2 Implement subscriber creation endpoint (creates `pending` record + sends confirmation) with tests
- [x] 4.3 Implement confirmation token validation endpoint (transitions `pending` → `active`) with tests
- [x] 4.4 Implement unsubscribe endpoint (sets `unsubscribed`) with tests
- [x] 4.5 Implement newsletter auto-send on publish (Resend batch to `active` subscribers + `NewsletterSend` log) with tests

## 5. Frontend Public Pages

- [x] 5.1 Build article list page with laboratory aesthetic (monospace metadata, sans-serif content, thin borders)
- [x] 5.2 Build article detail page with TipTap JSON-to-HTML rendering
- [x] 5.3 Build newsletter subscription form at end of articles with triple-coded states (color + icon + pattern)
- [x] 5.4 Build static confirmation success / unsubscribe success pages

## 6. Frontend Admin Panel

- [x] 6.1 Build admin layout with bearer token injection on all API requests
- [x] 6.2 Build admin article list page with edit/delete actions
- [x] 6.3 Build TipTap WYSIWYG editor component (bold, italic, links, headings, blockquotes, code, lists)
- [x] 6.4 Build article create/edit form with publish toggle and `send_newsletter` checkbox

## 7. Infrastructure

- [x] 7.1 Create Docker Compose dev setup (FastAPI + PostgreSQL + Vite dev server behind Nginx)
- [x] 7.2 Create Docker Compose prod setup (FastAPI + PostgreSQL + built static files served by Nginx)
- [x] 7.3 Configure Nginx as reverse proxy (`/` → Vite, `/api` → FastAPI, port 80)

## 8. Integration & Polish

- [x] 8.1 Run end-to-end smoke test: subscribe → confirm → create article → publish → verify newsletter sent
- [x] 8.2 Verify triple-coded accessibility on all UI states (error, success, loading, info)
- [x] 8.3 Verify auto-description generation and slug collision handling manually
