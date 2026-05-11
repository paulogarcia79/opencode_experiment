# AGENTS.md

## What This Repo Is

A **Blog + Newsletter Platform** with a real application stack: FastAPI backend, Vue 3 frontend, PostgreSQL, Docker Compose, and Nginx. It also carries an **OpenSpec planning layer** for spec-driven development.

## Implementation Flow (User-Mandated)

**CRITICAL: Never skip steps. Never jump from planning directly to implementation.**

Always follow this sequence for new features:

1. **`/grill-me [feature]`** or **`/grill-with-docs`** — Stress-test the plan with the user until decisions crystallize
   - **DO NOT implement code, create files, or make changes during this phase**
   - Ask questions one at a time, resolve design decisions, explore codebase
   - Capture resolved decisions as you go
   - When grilling is complete, proceed to step 2

2. **`/to-prd`** — Convert the grilled plan into a PRD and publish to `prd/PRD-<name>.md`
   - Use the resolved decisions from the grilling session as input
   - Wait for user review and approval before proceeding

3. **`/to-issues`** — Break the PRD into independently-grabbable issues (tracer-bullet vertical slices)
   - Issues are created in `issues/<number>-<name>.md`
   - Each issue should be independently implementable

4. **TDD** — Write tests before logic (pytest backend, Vitest frontend)
   - Use the **Ralph loop** (`./ralph/once.sh`) for autonomous implementation, OR the **`/tdd`** skill for manual implementation
   - Only now do you start implementing code
   - Pick issues from `issues/` and work through them

5. **`/qa-checklist`** — After implementation, generate a manual QA checklist from the PRD, issues, tests, and code
   - This is ALWAYS the final step before commit
   - User must review and approve the QA checklist

6. **Commit changes** — After QA checklist approval, commit the implementation
   - Follow git safety protocols (never force push, never skip hooks)

### Workflow Enforcement Rules

- **Grilling is planning only.** If you catch yourself writing implementation code during a grilling session, stop immediately.
- **No direct implementation from grilling.** The sequence grill → PRD → issues → implementation is mandatory.
- **Wait for user approval.** After `/to-prd` publishes the PRD, wait for the user to review before running `/to-issues`.
- **Issues must exist before implementation.** Do not implement features that don't have a corresponding issue in `issues/`.
- **QA checklist is mandatory.** Always run `/qa-checklist` after implementation and wait for user approval before committing.
- **Never commit without approval.** Only commit changes after the user approves the QA checklist.

## Tech Stack

- **Backend:** Python ≥3.14, FastAPI, SQLModel, PostgreSQL, Alembic, Resend (email)
- **Frontend:** Vue 3 (Composition API), TypeScript, Tailwind CSS, Vite, Vitest, TipTap editor
- **Infra:** Docker Compose (dev + prod profiles), Nginx (port 80/443 only entry point)
- **Package Managers:** `uv` (Python), `npm` (Node)

## Key Commands

```bash
# Dev (Docker Compose — recommended, no local Postgres needed)
just dev          # Start full stack (Nginx on http://localhost)
just dev-down     # Stop
just dev-clean    # Stop + wipe volumes

# Dev (local — requires Postgres on :5432)
just db           # Start Postgres in Docker
just migrate      # Run Alembic migrations
just back         # Backend dev server (:8000)
just front        # Frontend dev server (:5173)

# Testing (TDD is mandatory — write tests FIRST)
just test         # Backend: pytest tests/ -v
just test-cov     # Backend with coverage
just test-front   # Frontend: vitest
just build-front  # Type-check + build (vue-tsc && vite build)

# Database
just migration <name>   # Generate Alembic migration
just db-reset           # Drop all tables and re-run migrations

# OpenSpec workflow
openspec new change "<kebab-case>"
openspec status --change "<name>" --json
openspec instructions apply --change "<name>" --json
openspec list --json
```

## Architecture

### Entry Points
- **Backend:** `app/main.py` → FastAPI app. Routers in `app/routers/`. Services in `app/services/`. Models in `app/models/`.
- **Frontend:** `frontend/src/main.ts` → Vue 3 + Vue Router + Pinia. Vite dev server proxies `/api` to `:8000`.
- **Nginx:** The only external entry point. Dev routes `/` → Vite, `/api` → FastAPI, `/uploads` → filesystem. Prod serves built static files.

### Backend Patterns
- **SQLModel classes are the single source of truth** for both DB tables and API validation.
- **UUIDs for all primary keys.**
- **Bearer-token admin auth** via `ADMIN_API_TOKEN` env var (`app/dependencies.py::require_admin`).
- **Tests use SQLite in-memory** (`tests/conftest.py`) with FastAPI `TestClient`.
- **Alembic migrations** in `alembic/versions/`. Import all models in `alembic/env.py` for autogenerate.

### Frontend Patterns
- **Strict TypeScript — no `any`.** Interfaces must map to the backend OpenAPI schema.
- **TipTap JSON** is the article content format. Render with `@tiptap/html` (public) or `app/services/tiptap_renderer.py` (email).
- **Image upload** is fully implemented: drag-and-drop/paste into TipTap, local storage with year/month dirs, Media Library admin page, Nginx serves `/uploads`.
- **Design system:** Dark tech aesthetic. Background `#0F0F23`, primary `#7C3AED`, accent `#F43F5E`. Fonts: Space Grotesk (headings), Inter (body), JetBrains Mono (code). See `design-system/tech-&-games-blog/MASTER.md`.

## Non-Obvious Conventions

- **TDD is strictly required.** Backend: `pytest` + `TestClient`. Frontend: `Vitest` + `@vue/test-utils`. Write the test first, then the implementation.
- **Proposals must be under 500 words** and always include a "Non-goals" section.
- **Task chunks max 2 hours.** Break work accordingly.
- **Do NOT copy `<context>`, `<rules>`, or `<project_context>` blocks** into artifact files. These are agent constraints, not file content.
- **In explore mode (`/opsx-explore`), NEVER write application code.** OpenSpec artifacts only.
- **Always read `contextFiles` from `openspec instructions apply --json`** before implementing. Do not assume artifact filenames.
- **Keep changes minimal and scoped** to the current task.
- **During grilling sessions (`/grill-me` or `/grill-with-docs`):**
  - NEVER write application code, create files, or make changes
  - Ask questions one at a time, waiting for user feedback
  - Explore the codebase to answer questions instead of guessing
  - Capture resolved decisions as you go for use in `/to-prd`
  - When grilling concludes, run `/to-prd` next — do NOT implement

## Artifact Locations

- **PRDs:** `prd/PRD-<name>.md` — created by `/to-prd`, referenced by issues
- **Active issues:** `issues/<number>-<name>.md` — created by `/to-issues`, moved to `issues/done/` when completed
- **Completed issues:** `issues/done/<number>-<name>.md` — reference for QA and retrospectives
- **QA checklists:** `qa-checklist-<name>.md` — generated by `/qa-checklist` after implementation

## Environment Setup

- **Python:** Requires ≥3.14. Managed with `uv`. Virtual env at `.venv/`. Activate: `source .venv/bin/activate`.
- **Node:** `npm` in `frontend/`. `ecc-universal` is an OpenCode plugin (see `opencode.json`).
- **Env:** Copy `.env.example` → `.env`. Key vars: `DATABASE_URL`, `ADMIN_API_TOKEN`, `RESEND_API_KEY`, `APP_BASE_URL`, `VITE_API_BASE_URL`.

## Ralph (Autonomous Loop)

- **Purpose:** Picks AFK issues from `issues/`, implements with TDD, commits, moves done issues to `issues/done/`.
- **Run:** `./ralph/once.sh` (single iteration) or `./ralph/afk.sh 10` (loop).
- **Requires:** `opencode` CLI, `GITHUB_TOKEN` (for `sync-issues.sh`), activated `.venv`.
- **Task priority:** 1. Critical bugfixes → 2. Dev infrastructure → 3. Tracer bullets → 4. Polish → 5. Refactors.
- **Feedback loops before commit:** `pytest tests/ -v`, `cd frontend && npm run test`, `cd frontend && npm run build` (type-check).

## Directory Boundaries

```
app/                   # FastAPI backend
  main.py              # App entry point
  routers/             # API routes
  services/            # Business logic
  models/              # SQLModel tables
  config.py            # Pydantic Settings (.env)
frontend/              # Vue 3 frontend
  src/
    views/             # Page components
    components/        # Reusable components
    composables/       # Logic + API clients
    stores/            # Pinia stores
prd/                   # Product requirement documents
issues/                # Active AFK issues
  done/                # Completed issues
openspec/              # OpenSpec planning layer
  config.yaml          # Project context, tech stack, rules
  specs/               # Main capability specs (persistent)
  changes/             # Active changes
    archive/           # Completed changes (date-prefixed)
ralph/                 # Autonomous task loop scripts
design-system/         # UI design specs
```

## Available Skills

Skills are triggered by typing `/<skill-name>` in chat.

**Repo-local** (`.opencode/skills/`): `openspec-propose`, `openspec-apply-change`, `openspec-explore`, `openspec-archive-change`, `graphify`, `api-design`, `backend-patterns`, `coding-standards`, `e2e-testing`, `eval-harness`, `frontend-patterns`, `frontend-slides`, `security-review`, `strategic-compact`, `tdd-workflow`, `ui-ux-pro-max`, `verification-loop`, `qa-checklist`

**External** (`.agents/skills/`): `grill-me`, `grill-with-docs`, `improve-codebase-architecture`, `tdd`, `to-issues`, `to-prd`

## Testing Quirks

- Backend tests run against **SQLite in-memory**, not PostgreSQL. This is fast but may hide Postgres-specific behavior (e.g., JSONB operators).
- Frontend tests use **happy-dom** environment (configured in `vite.config.ts`).
- The `vue-tsc` type-checker is strict (`noUnusedLocals`, `noUnusedParameters`). Prefix unused params with `_`.
- **No CI/CD pipeline exists yet.** All quality checks are local via `just` commands.

## Custom Commands

The `opencode.json` registers custom slash commands. Currently:
- `/graphify` — Build a queryable knowledge graph from the codebase

Skills can also be invoked as slash commands when registered (e.g., `/qa-checklist`).
