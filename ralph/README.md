# Ralph — Autonomous Issue Loop

Ralph is an autonomous task loop that picks AFK (away-from-keyboard) issues from `issues/`, implements them using TDD, runs feedback loops, commits, and moves completed issues to `issues/done/`.

Inspired by [Matt Pocock's AI Engineer Workshop](https://github.com/mattpocock/ai-engineer-workshop-2026-project/tree/main/ralph).

## Workflow

1. **Sync issues from GitHub**
   ```bash
   export GITHUB_TOKEN=ghp_...
   ./ralph/sync-issues.sh
   ```

2. **Run one iteration** (picks next AFK issue, implements, commits)
   ```bash
   ./ralph/once.sh
   ```

3. **Run multiple iterations** (loop until done or max iterations)
   ```bash
   ./ralph/afk.sh 10
   ```

## Directory Structure

```
ralph/
  prompt.md        # Instructions given to the AI agent
  once.sh          # Single iteration
  afk.sh           # Loop runner
  sync-issues.sh   # Pull GitHub issues into issues/
issues/
  001-....md       # Active AFK issues (synced from GitHub)
  done/
    001-....md     # Completed issues
```

## How It Works

1. `sync-issues.sh` fetches open issues from GitHub and saves them as `.md` files in `issues/`
2. `once.sh` reads all issues + recent git commits + `prompt.md`, then invokes `opencode run` with the full context
3. The AI agent:
   - Parses issues and picks the next AFK task
   - Explores the repo (reads AGENTS.md, openspec config)
   - Implements using strict TDD (pytest for backend, vitest for frontend)
   - Runs feedback loops (`pytest`, `npm run test`, `npm run typecheck`)
   - Commits with descriptive messages
   - Moves completed issue to `issues/done/`, or adds a note if incomplete
4. `afk.sh` repeats `once.sh` until all issues are done or max iterations reached

## Task Priority (from prompt.md)

1. Critical bugfixes
2. Development infrastructure
3. Tracer bullets for new features
4. Polish and quick wins
5. Refactors

## Important Notes

- **Only AFK issues are worked on.** HITL (human-in-the-loop) issues are skipped.
- **Only one task per iteration.** The agent focuses on a single issue at a time.
- **Tests are required.** No implementation without tests (backend: pytest, frontend: vitest).
- **Git commits are automatic.** Each iteration produces one commit with key decisions and blockers noted.

## Requirements

- `opencode` CLI installed
- `GITHUB_TOKEN` with `repo` scope (for sync)
- Python ≥3.14 and `uv` (for backend tests)
- Node.js and `npm` (for frontend tests)
