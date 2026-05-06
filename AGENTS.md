# AGENTS.md

## What This Repo Is

An **OpenSpec workspace** for spec-driven development. It contains NO application code — only the planning layer, agent tooling, and conventions for a Blog + Newsletter platform. All work flows through the `openspec` CLI (v1.3.1).

## Tech Stack (from `openspec/config.yaml`)

- **Backend:** Python (≥3.14), FastAPI, SQLModel, PostgreSQL
- **Frontend:** Vue.js 3 (Composition API), TypeScript, Tailwind CSS, Vite, Vitest
- **Infra:** Docker, Docker Compose, Nginx (reverse proxy/gateway)
- **Methodology:** Spec-Driven Development (SDD) + strict Test-Driven Development (TDD)
- **Package Manager:** `uv` (Python), `npm` (Node)

## Key Commands

- `openspec new change "<kebab-case-name>"` — Scaffold a new change
- `openspec status --change "<name>" --json` — Artifact completion & dependencies
- `openspec instructions <artifact-id> --change "<name>" --json` — Artifact creation guidance
- `openspec instructions apply --change "<name>" --json` — Task list & context files for implementation
- `openspec list --json` — List active changes

### Slash Commands (defined in `.opencode/commands/`)

- `/opsx-propose <name>` — Create change + generate proposal.md, design.md, tasks.md
- `/opsx-apply <name>` — Implement pending tasks from a change
- `/opsx-explore <topic>` — Thinking/investigation mode. NEVER implement code here
- `/opsx-archive <name>` — Move completed change to `openspec/changes/archive/YYYY-MM-DD-<name>/`
- `/graphify <path>` — Build a queryable knowledge graph. Requires `source .venv/bin/activate` first. Outputs: `graphify-out/graph.html`, `GRAPH_REPORT.md`, `graph.json`

### Available Skills

**Repo-local** (`.opencode/skills/`): `openspec-propose`, `openspec-apply-change`, `openspec-explore`, `openspec-archive-change`, `graphify`, `api-design`, `backend-patterns`, `coding-standards`, `e2e-testing`, `eval-harness`, `frontend-patterns`, `frontend-slides`, `security-review`, `strategic-compact`, `tdd-workflow`, `ui-ux-pro-max`, `verification-loop`

**External** (`.agents/skills/`, locked in `skills-lock.json` from `mattpocock/skills`): `grill-me`, `grill-with-docs`, `improve-codebase-architecture`, `tdd`, `to-issues`, `to-prd`

## Non-Obvious Conventions

- **TDD is strictly required.** Write tests before logic: `pytest` + FastAPI `TestClient` for backend; `Vitest` + `@vue/test-utils` for frontend.
- **SQLModel classes are the single source of truth** for both database tables and API validation.
- **UUIDs for all primary keys.**
- **Task chunks max 2 hours.** Break work accordingly.
- **Proposals must be under 500 words** and always include a "Non-goals" section.
- **Nginx is the only external entry point** (ports 80/443). In dev mode, it routes `/` to Vite and `/api` to FastAPI.
- **No `any` in TypeScript.** Frontend interfaces must strictly map to the backend OpenAPI schema.
- **Do NOT copy `<context>`, `<rules>`, or `<project_context>` blocks into artifact files.** These are agent constraints, not file content.

## Directory Boundaries

```
openspec/
  config.yaml          # Project context, tech stack, rules
  specs/               # Main capability specs (persistent source of truth)
  changes/             # Active changes (transient work in progress)
    archive/           # Completed changes (date-prefixed folders)
.opencode/
  commands/            # Slash command definitions for agents
  skills/              # Agent skill instructions
.agents/
  skills/              # External agent skills (locked via skills-lock.json)
```

## Environment Setup

- **Python:** Managed with `uv`. Requires Python ≥3.14. Never install with system `pip` without `--break-system-packages`.
- **Virtual env:** `.venv/` exists and contains `graphifyy`. Activate with `source .venv/bin/activate` before running `graphify` commands.
- **Node:** `ecc-universal` is installed as an OpenCode plugin (see `opencode.json`).

## Workflow Lifecycle

1. **Propose:** `/opsx-propose <name>` → creates artifacts in `openspec/changes/<name>/`
2. **Apply:** `/opsx-apply <name>` → implement tasks, mark checkboxes `- [x]`
3. **Archive:** `/opsx-archive <name>` → moves to `openspec/changes/archive/`, optionally syncs delta specs to `openspec/specs/`

## Agent Guardrails

- Always read `contextFiles` from `openspec instructions apply --json` before implementing. Do not assume artifact filenames.
- In explore mode, NEVER write application code. Creating OpenSpec artifacts is allowed.
- Keep changes minimal and scoped to the current task.
