# Blog + Newsletter Platform

A robust, full-stack blog and newsletter platform designed for high performance and engagement.

## Tech Stack

- **Backend:** Python ≥3.14, FastAPI, SQLModel, PostgreSQL, Redis (Caching & Jobs)
- **Frontend:** Vue 3 (Composition API), TypeScript, Tailwind CSS, Vite
- **Infrastructure:** Docker Compose, Nginx, ARQ (Background Queue)
- **Package Managers:** `uv` (Python), `npm` (Node)

## Core Features

- **Content Management:** Markdown import, TipTap rich-text editor, automated drafts, and full revision history.
- **Newsletter Engine:** MJML templates, background delivery via Redis/ARQ, open/click tracking, and bounce handling.
- **Performance:** Aggressive Redis caching for public endpoints and RSS feeds.
- **SEO & Social:** Automated XML sitemaps, RSS feed, JSON-LD structured data, and OpenGraph sharing.
- **Admin Dashboard:** Real-time engagement analytics, subscriber growth charts, and article performance metrics.

## Development

Requires [Just](https://github.com/casey/just) as a command runner.

```bash
# Setup environment
just env
just install

# Start development stack (Docker Compose)
just dev

# Run tests
just test        # Backend
just test-front  # Frontend
```

## Architecture

- **Caching Layer:** Uses `fastapi-cache2` with Redis for public GET endpoints (`/api/articles`, `/feed.xml`). Invalidation is event-driven, triggered by any admin mutation.
- **View Tracking:** Decoupled from content delivery via a client-side background POST request to `/api/articles/{slug}/view`.
- **Admin Auth:** Bearer-token authentication with role-based access control (Admin, Editor, Contributor).
