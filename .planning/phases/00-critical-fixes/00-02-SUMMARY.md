---
phase: "00-critical-fixes"
plan: "02"
subsystem: "approval-gate"
tags: ["pending-approvals", "telegram", "dashboard", "json", "thread-safety"]
dependency_graph:
  requires: []
  provides:
    - path: "pending_approvals.json"
      description: "Shared state file between Python bot and TypeScript server"
  affects:
    - "server/storage.ts" # reads this file
    - "Dashboard ApprovalQueue" # displays live pending approvals
tech_stack:
  added: ["json", "datetime", "threading"]
  patterns: ["thread-safe file I/O with threading.Lock", "shared JSON state file"]
key_files:
  created: []
  modified:
    - "bot/approval_gate.py"
decisions: []
metrics:
  duration_minutes: "5"
  completed_date: "2026-03-20"
  tasks_completed: 1
  tasks_total: 1
---

# Phase 00 Plan 02: Wire pending_approvals.json from Approval Gate

## One-liner
Python approval gate now writes `pending_approvals.json` with all signal fields, keeping last 20 entries, updated on every approval/rejection/timeout.

## What Was Built

### Changes to `bot/approval_gate.py`

**New module-level functions:**

1. **`_read_pending()`** — Reads `pending_approvals.json` from disk, returns empty list if missing/unreadable.

2. **`_write_pending(signal, size, msg_id_key)`** — Thread-safe writer that:
   - Reads existing approvals
   - Builds entry with all required fields: `id`, `label`, `side`, `size`, `edge`, `source`, `score`, `market_prob`, `model_prob`, `timestamp`, `status="pending"`
   - Appends to list, keeps only last 20 entries
   - Writes back to `APPROVALS_FILE`
   - Protected by `_approvals_lock`

3. **`_resolve_pending(msg_id_key, status)`** — Thread-safe updater that:
   - Finds entry by `id`
   - Updates `status` to `approved`, `rejected`, or `expired`
   - Writes back to disk
   - Protected by `_approvals_lock`

**Wiring into approval flow:**

- `_write_pending()` is called **AFTER** `pending[msg_id_key] = None` and **BEFORE** the poll loop starts (line 142)
- `_resolve_pending(msg_id_key, "approved" if decision else "rejected")` is called **AFTER** each Telegram callback decision (line 150)
- `_resolve_pending(msg_id_key, "expired")` is called **AFTER** timeout (line 160)

### How TypeScript Reads It

`server/storage.ts` already had `getPendingApprovals()` that reads from `APPROVALS_FILE`. Since we now write the same format TypeScript expects, the dashboard will show live pending approvals automatically — no changes needed to TypeScript side.

## Verification

```
PASS: _write_pending created file with correct entry
PASS: _resolve_pending updated status to approved
All tests passed!
```

Functions verified: `_write_pending`, `_resolve_pending`, `_read_pending`, `APPROVALS_FILE`, `_approvals_lock`

## Deviations from Plan

**None — plan executed exactly as written.**

## Auth Gates

None.

## Checkpoint Details

N/A — fully autonomous plan executed completely.
