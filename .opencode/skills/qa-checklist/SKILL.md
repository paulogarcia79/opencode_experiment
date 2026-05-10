---
name: qa-checklist
description: "Generate a manual QA checklist from a completed implementation. Reads the PRD, tests, and issues to produce actionable human-verification steps."
---

# /qa-checklist

## When to Activate

Only on explicit request. The user types `/qa-checklist` after completing an implementation.

## What You Must Do

1. **Gather context** — Read the PRD, the issue(s), and the test files that drove the implementation. Also read the actual code changes (modified or new files).
2. **Understand scope** — Determine what was built (backend API? frontend UI? both?).
3. **Generate a manual QA checklist** — Produce a concise, actionable Markdown checklist that a human can follow to verify the feature works end-to-end.

## Input Sources (read these)

- The PRD file (`prd/PRD-*.md`) for the feature
- The issue file(s) (`issues/*.md` for active, `issues/done/*.md` for completed) that broke the PRD into tasks
- The test files (`tests/test_*.py`, `frontend/src/**/__tests__/*.spec.ts`) that verify the implementation
- The actual implementation code (new or modified files)

## Output Structure

Produce a single Markdown file. Keep it concise — only what a human tester needs to verify manually.

### 1. Prerequisites & Setup
What must be running? What initial state is required?

### 2. Backend API Checks
If the feature touches the backend, list:
- Endpoint URLs and HTTP methods
- Example request payloads
- Expected HTTP status codes and response shapes
- Auth requirements

### 3. Frontend UI Checks
If the feature touches the frontend, list:
- Navigation steps (which URL, which buttons to click)
- Expected UI states (what should be visible, what should be hidden)
- Interaction steps (type, click, wait, observe)

### 4. Edge Cases & Error Handling
- Invalid inputs (empty fields, malformed data, oversize payloads)
- Unauthorized access attempts
- Network failure scenarios (if applicable)
- Expected error messages or UI feedback

### 5. Integration Checks
- End-to-end flow (frontend action → backend persistence → frontend reflection)
- Database state changes (if observable)
- Cross-browser concerns (if applicable)

## Constraints

- This is strictly for **manual human verification**. Do NOT include automated test commands (pytest, vitest, etc.).
- Each checklist item must be actionable: `[ ] **Action:** ... → **Expected:** ...`
- Group by area (Backend vs Frontend) when both are involved.
- Keep each item to one line if possible.
- Do not include implementation details or code snippets — focus on observable behavior only.
