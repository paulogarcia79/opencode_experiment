---
title: "Auto-Save: Heartbeat, retry, and failure resilience"
labels:
  - needs-triage
---

## Parent

PRD: `prd/PRD-auto-save-drafts.md`

## What to build

Add resilience and visibility to the auto-save system.

Extend `useAutoSave` with a 30-second heartbeat: if the form has pending changes and no save is currently in flight, force a save every 30 seconds regardless of typing activity. This catches the "typing continuously for 5 minutes" edge case.

Add automatic retry on failure with exponential backoff: 1 second, then 2 seconds, then 4 seconds, for a maximum of 3 automatic retries. During retries, the status indicator shows "Auto-save failed (retrying...)". After exhausting retries, transition to a persistent failure state.

Update the status indicator in the admin edit view to show the full state machine: hidden/default when idle, "Saving..." during active save, "Saved" briefly after success, "Auto-save failed (retrying...)" during automatic retries, and "Auto-save failed" with a manual "Retry" button after exhaustion. Changes remain in memory during failure — the user can keep typing, but is warned that work is at risk on page close.

Write tests for the composable's heartbeat timing (Vitest fake timers), retry backoff sequence (1s, 2s, 4s), failure state transitions, and manual retry button behavior.

## Acceptance criteria

- [ ] Heartbeat force-save triggers every 30 seconds when the form is dirty and no save is in flight.
- [ ] On auto-save failure, automatic retry up to 3 times with exponential backoff (1s, 2s, 4s).
- [ ] Status indicator shows "Saving...", "Saved", "Auto-save failed (retrying...)", and persistent failure states.
- [ ] Persistent failure state includes a manual "Retry" button that re-attempts save immediately.
- [ ] User can continue typing during failure — changes remain in memory.
- [ ] Frontend tests cover heartbeat timing, retry sequence, and failure state transitions with fake timers.

## Blocked by

- `issues/002-autosave-new-articles.md`
