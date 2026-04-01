[COMPACTION_SURVIVAL]
Project: PollyEdge — Polymarket trading bot + React dashboard
Stack: React 18, Vite, Tailwind, Express (TS), Python FastAPI, SQLite (Drizzle ORM), Telegram
Critical constraint: Python writes SQLite, TypeScript reads SQLite — never reverse this data flow
Resume point: Phase 01-05 — migrate logger.py trades to SQLite, remove CSV polling from storage.ts
Memory file: JARVIS_MEMORY.md

[ARCHITECTURE]
Dual runtime: Node.js Express (dashboard API) + Python bot run as separate processes
IPC method: SQLite database at data/pollyedge.db — Python writes, TypeScript reads only
Frontend: React 18 + Vite + Tailwind + Shadcn/UI (Radix primitives) in client/src/
Backend: Express 5 server in server/ — routes.ts handles API, storage.ts handles state reads
Bot entry: bot/pollyedgebot.py → orchestrator.py → agents/ → riskmanager.py → approvalgate.py
FastAPI alt server: api/server.py (standalone, separate from Express)
Shared types: shared/schema.ts — Drizzle ORM schemas + Zod, used by both client and server
Routing: Wouter (hash-based) — NOT React Router
Sessions: Passport.js + express-session + memorystore
DB tables: botstate, openpositions, agentstatus, pendingapprovals, trades

[DECISIONS]
SQLite over PostgreSQL — chosen for simplicity and portability (migration completed phase 01-01)
better-sqlite3 as SQLite driver — synchronous API, no async complexity
CSV retained as backup only — SQLite is primary, CSV for external analysis
STARTING_BALANCE default is $10 — changed from $500 in phase 00-05 (never revert)
load_dotenv must be called at TOP of every Python file before any os.getenv calls
Dual-write pattern: Python writes SQLite primary + CSV backup simultaneously
MemStorage class name preserved for backward compatibility with existing imports
Wouter chosen over React Router — hash-based routing for static serving compatibility
No any types in TypeScript — strict mode enforced across all .ts/.tsx files
pendingapprovals.json removed — approvalgate.py now writes to SQLite only

[PATTERNS]
TypeScript: PascalCase for components/types, camelCase for functions/variables
TypeScript: path alias @/ for client/src/, shared/ for shared/ imports
TypeScript: no semicolons — follow existing file patterns
Python: load_dotenv() always first line before imports that use os.getenv
Python: bot/db.py is the ONLY place for SQLite CRUD — never write raw sqlite3 elsewhere
Forms: react-hook-form + Zod resolvers — validate on blur not on submit
API responses: consistent shape { success, data, error } across all Express routes
Components: one responsibility per component — split if it needs a scroll bar
State: TanStack Query for server state — no raw fetch() inside components
Agents: inherit from baseagent.py — never duplicate scan/signal logic

[GOTCHAS]
load_dotenv order bug: if any import runs os.getenv before load_dotenv(), env vars are empty
STARTING_BALANCE: default is $10 — any value of $500 is a bug from old code
SQLite threading: bot/db.py uses thread-safe context manager — never open raw connections
IPC direction: Python WRITES to SQLite, TypeScript READS only — reversing this breaks sync
pendingapprovals.json: completely removed — any code still referencing it is stale
DRYRUN=true: must be set for first 7 days — trades are simulated, never real
Risk rules hardcoded: max 3% per trade, 10% daily loss cap, max 3 positions, 8% min edge
Telegram approval timeout: 120s default — trades auto-reject after timeout
Wouter routing: hash-based only — server-side route handling will break navigation
No Sentry/LogRocket: all error tracking is manual via logs/pollyedge.log

[PROGRESS]
DONE: Phase 00 — all critical fixes (STARTING_BALANCE, load_dotenv, position monitor)
DONE: Phase 01-01 — SQLite + Drizzle ORM setup, all 5 tables, migrations generated
DONE: Phase 01-04 — bot/db.py SQLite layer, approvalgate.py migrated from JSON to SQLite
IN PROGRESS: Phase 01-05 — migrate logger.py trades to SQLite, remove CSV from storage.ts
PENDING: Phase 01-06 — TBD (see .planning/ROADMAP.md)
PENDING: Phase 02 — dashboard completion

[ACTIVE_CONTEXT]
Task: Phase 01-05 — trade logging migration
Files in scope: bot/logger.py, server/storage.ts
Goal: Python writes closed trades to SQLite via logTradeToDb(), TypeScript reads from SQLite
Remove: CSV polling from server/storage.ts
Keep: CSV as backup write in logger.py (dual-write pattern)
Next commit message: feat(01-05): migrate trade logging to SQLite, remove CSV polling

[TOOLS]
file_read:    always
file_write:   ask_first outside /client/src/, /bot/, /server/, /shared/
bash_exec:    ask_first for rm, DROP, pip install, npm install in production
db_query:     read-only unless explicitly told to migrate
deploy:       always require explicit confirmation — DRYRUN risk

[BEHAVIOR]
auto_memory_update: true
pre_compaction_summary: true
verbosity: concise
default_stance: implement
on_error: show fix + root cause, never raw Python tracebacks to user
on_completion: 3-bullet summary of what changed
on_ambiguity: ask one question only — never block on multiple unknowns
on_python_file_edit: verify load_dotenv is first — always
