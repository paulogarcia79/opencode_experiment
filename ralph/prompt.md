# RALPH — Autonomous Task Loop for Blog + Newsletter Platform

## ISSUES

Local issue files from `issues/` are provided at start of context. Parse them to understand the open issues.

You will work on the AFK issues only, not the HITL ones.

You've also been passed a file containing the last few commits. Review these to understand what work has been done.

If all AFK tasks are complete, output <promise>NO MORE TASKS</promise>.

## TASK SELECTION

Pick the next task. Prioritize tasks in this order:

1. Critical bugfixes
2. Development infrastructure

Getting development infrastructure like tests, type checking, and dev scripts ready is an important precursor to building features.

3. Tracer bullets for new features

Tracer bullets are small slices of functionality that go through all layers of the system, allowing you to test and validate your approach early. This helps in identifying potential issues and ensures that the overall architecture is sound before investing significant time in development.

TL;DR - build a tiny, end-to-end slice of the feature first, then expand it out.

4. Polish and quick wins
5. Refactors

## EXPLORATION

Explore the repo. Read AGENTS.md for project-specific conventions. Read `openspec/config.yaml` for tech stack context.

## IMPLEMENTATION

Use strict TDD to complete the task:

- Backend (FastAPI/SQLModel): Write pytest test first, then implementation
- Frontend (Vue 3/TypeScript): Write Vitest test first, then implementation
- Follow the OpenSpec workflow: changes live in `openspec/changes/<name>/`
- Never implement without tests

## FEEDBACK LOOPS

Before committing, run the feedback loops:

- `pytest tests/ -v` to run backend tests
- `cd frontend && npm run test` to run frontend tests (if frontend changed)
- `cd frontend && npm run typecheck` to run type checker (if frontend changed)
- `just test` to run all tests (if justfile exists)

## COMMIT

Make a git commit. The commit message must:

1. Include key decisions made
2. Include files changed
3. Blockers or notes for next iteration

## THE ISSUE

If the task is complete, move the issue file to `issues/done/`.

If the task is not complete, add a note to the issue file with what was done.

## FINAL RULES

ONLY WORK ON A SINGLE TASK.
