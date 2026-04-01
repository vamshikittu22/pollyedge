# POLLYEDGE AGENT SETUP — MASTER SOURCE FILE
# Generated: 2026-04-01
# Usage: Feed this file to any AI agent with the REBUILD PROMPT at the bottom
# It will regenerate all project files from this single source

---
---
## FILE: GEMINI.md
## LOCATION: project root
---

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


---
---
## FILE: JARVIS_MEMORY.md
## LOCATION: project root
---

[PROJECT]
Name: PollyEdge
Repo: vamshikittu22/pollyedge
Description: Polymarket prediction market trading bot with live React dashboard
Started: 2026-03-19

[FACTS]
Stack: React 18, Vite, Tailwind, Shadcn/UI, Express 5 (TS), Python 3.x, SQLite, Drizzle ORM
IPC: Python writes SQLite → TypeScript reads SQLite (one-direction only)
DB file: data/pollyedge.db
DB tables: botstate, openpositions, agentstatus, pendingapprovals, trades
Bot entry: bot/pollyedgebot.py
Dashboard entry: server/index.ts + client/src/main.tsx
Shared types: shared/schema.ts (Drizzle + Zod)
Routing: Wouter hash-based (not React Router)
Auth: Passport.js local strategy + express-session

[PREFS]
No any types in TypeScript — strict mode always
No semicolons in TypeScript — follow existing patterns
load_dotenv at top of every Python file before imports
STARTING_BALANCE default = $10 (never $500)
DRYRUN=true during development and first 7 days live
SQLite primary, CSV backup (dual-write in logger.py)
One function = one responsibility
bot/db.py is single source of SQLite CRUD — never bypass it

[HISTORY]
2026-03-19 → Phase 00 complete: fixed STARTING_BALANCE default ($500→$10), added load_dotenv to all Python files, created positionmonitor.py
2026-03-20 → Phase 01-01 complete: SQLite + Drizzle ORM configured, better-sqlite3 driver, all 5 tables, migrations at migrations/0000_nosy_jimmy_woo.sql
2026-03-20 → Phase 01-04 complete: bot/db.py SQLite CRUD layer created, approvalgate.py migrated from pendingapprovals.json to SQLite

[BLOCKERS]
server/storage.ts still reads from CSV/JSON files for trades — needs Phase 01-05 migration
Phase 01-05 not yet committed — logger.py trade logging still writes CSV only as primary

[NEXT]
Complete Phase 01-05: add logTradeToDb() to bot/db.py, update bot/logger.py to write SQLite primary + CSV backup, update server/storage.ts to read trades from SQLite, remove CSV polling

---
SESSION LOG

[2026-03-19] Phase 00-critical-fixes
- Fixed STARTING_BALANCE default in apiserver.py: 500 → 10
- Added load_dotenv to bot/orchestrator.py (was missing)
- Verified all Python files have load_dotenv before os.getenv
- Created bot/positionmonitor.py (167 lines), PROFIT_TARGET=0.3, STOP_LOSS=0.1
- Removed logtrade from orchestrator.py (timing fix)
- Commits: 055805a, 28e97f8

[2026-03-20] Phase 01-01 — SQLite Foundation
- Configured drizzle.config.ts for SQLite (was PostgreSQL)
- Defined all 5 tables in shared/schema.ts
- Generated migration: migrations/0000_nosy_jimmy_woo.sql
- Created data/ directory, applied migration, DB confirmed at data/pollyedge.db

[2026-03-20] Phase 01-04 — Python SQLite Layer
- Created bot/db.py with full CRUD layer
- Migrated bot/approvalgate.py from pendingapprovals.json to SQLite
- server/storage.ts reads approvals from SQLite — trades migration pending
- Commits: 8556cb7


---
---
## FILE: .agents/workflows/start.md
## LOCATION: .agents/workflows/start.md
---

# /start — PollyEdge Session Startup Workflow

STEP 1 → Read global GEMINI.md (behavior + tool rules)
STEP 2 → Read project GEMINI.md (architecture, decisions, active context)
STEP 3 → Read .agents/rules/ files matching current working directory:
          bot/ or api/     → load db.md + api.md + testing.md
          client/src/      → load frontend.md + testing.md
          bot/agents/      → load ai-agents.md + testing.md
          server/          → load api.md + db.md + testing.md
STEP 4 → Read JARVIS_MEMORY.md
STEP 5 → Print SESSION RECAP:
          - Current phase and status
          - Last 3 decisions made
          - Active blockers
          - Single next action
STEP 6 → Print [ACTIVE_CONTEXT] from project GEMINI.md verbatim
STEP 7 → Ask: "Ready. What are we working on?"

IDENTITY
Agent for PollyEdge: dual-runtime trading system
Runtimes: Python bot (bot/) + Node.js Express server (server/) + React dashboard (client/)
IPC: Python writes SQLite → TypeScript reads — never reverse

CONSTRAINTS
→ Never write os.getenv before load_dotenv() in any Python file
→ Never change STARTING_BALANCE default away from $10
→ Never write raw sqlite3 outside bot/db.py
→ Never let TypeScript write to SQLite — read-only from TS side
→ Never remove CSV backup from logger.py — dual-write is intentional
→ DRYRUN=true unless explicitly told to go live
→ Risk rules are sacred: 3% per trade, 10% daily cap, max 3 positions, 8% min edge

TOOLS
file_read:    always
file_write:   ask_first outside /client/src/, /bot/, /server/, /shared/
bash_exec:    ask_first for rm, DROP TABLE, pip install, npm install --save
db_query:     read-only default
deploy:       always confirm — real money at risk

<MEMORY>
[FACTS]: loaded from JARVIS_MEMORY.md on /start
[PREFS]: loaded from JARVIS_MEMORY.md on /start
[HISTORY]: last 3 sessions from JARVIS_MEMORY.md SESSION LOG
[BLOCKERS]: loaded from JARVIS_MEMORY.md [BLOCKERS]
[NEXT]: loaded from JARVIS_MEMORY.md [NEXT]
</MEMORY>

CONTEXT LIMIT RULE
If context exceeds 40,000 tokens:
  1. Summarize completed work in 5 bullets
  2. Append new decisions to JARVIS_MEMORY.md [HISTORY]
  3. Update [BLOCKERS] and [NEXT] in JARVIS_MEMORY.md
  4. Drop all intermediate reasoning from context
  5. Reload: project GEMINI.md + JARVIS_MEMORY.md + current task
  6. Print: [CONTEXT COMPACTED — resuming from memory]

/save COMMAND
When user types /save:
  1. Append today's date + session entry to JARVIS_MEMORY.md SESSION LOG
  2. Update [BLOCKERS] and [NEXT] in JARVIS_MEMORY.md
  3. Update [PROGRESS] and [ACTIVE_CONTEXT] in project GEMINI.md
  4. Print: "Session saved. Run /start next time to resume."

AGENT MODE
orchestrator: plans subtasks — never executes file writes directly when planning
workers: each subtask = one file scope + minimum tools
parallel: allowed for lint, type-check, read-only analysis
sequential: required for any write touching shared/schema.ts, bot/db.py, server/storage.ts


---
---
## FILE: .agents/rules/frontend.md
## LOCATION: .agents/rules/frontend.md
## SCOPE: client/src/, *.tsx, *.jsx
---

[FRONTEND RULES]
→ No raw fetch() in components — use TanStack Query (queryClient.ts)
→ Routing: Wouter only — never import from react-router-dom
→ Forms: react-hook-form + Zod resolver — validate on blur not submit
→ State: TanStack Query for server state — useState/useReducer for local only
→ Components in client/src/components/ui/ are Shadcn/Radix — never edit directly
→ Loading, empty, and error states required for every useQuery call
→ No any types — strict TypeScript, use shared/schema.ts types
→ Path alias: use @/ for client/src/ imports, shared/ for shared/
→ Icons: lucide-react primary, react-icons secondary — no inline SVG icons
→ Charts: recharts only — already installed, do not add chart.js or d3
→ Animation: framer-motion only — do not add additional animation libraries
→ No semicolons — follow existing file style
→ PascalCase for components and types, camelCase for functions and variables


---
---
## FILE: .agents/rules/api.md
## LOCATION: .agents/rules/api.md
## SCOPE: server/, api/, routes.ts, server.py
---

[API RULES]
→ Express routes: consistent response shape { success, data, error }
→ FastAPI routes: pydantic models for request/response validation
→ All routes must have input validation before any business logic
→ HTTP status codes: 200 OK, 201 Created, 400 Bad input, 401 Unauth, 500 Server error
→ Never expose raw SQLite errors or Python tracebacks in API responses
→ All list endpoints must be paginated: { data[], total, page, limit }
→ Bot state reads: server/storage.ts reads from SQLite — never from JSON files directly
→ Python API (api/server.py): load_dotenv at top before any os.getenv usage
→ Express server: TypeScript strict mode, no any types
→ Session auth via Passport.js — never roll custom auth logic
→ Rate limit public endpoints — bot-facing endpoints are internal only


---
---
## FILE: .agents/rules/db.md
## LOCATION: .agents/rules/db.md
## SCOPE: bot/db.py, server/storage.ts, shared/schema.ts, migrations/
---

[DATABASE RULES]
→ bot/db.py is the ONLY file allowed to write to SQLite — never bypass it
→ TypeScript (server/storage.ts) reads SQLite via Drizzle ORM — read-only
→ IPC direction is ONE-WAY: Python writes, TypeScript reads — never reverse
→ All migrations via drizzle-kit: npx drizzle-kit generate → npx drizzle-kit migrate
→ Every migration must be reversible — document rollback steps
→ New columns must have defaults — no silent NULLs
→ Schema source of truth: shared/schema.ts — Drizzle tables + Zod schemas both here
→ SQLite threading: use thread-safe context manager in bot/db.py always
→ Dual-write pattern: SQLite primary + CSV backup in logger.py — keep both
→ DB file location: data/pollyedge.db — never hardcode alternate paths
→ Never use raw sqlite3 module in any file except bot/db.py
→ Query only columns you need — no SELECT * in production queries


---
---
## FILE: .agents/rules/testing.md
## LOCATION: .agents/rules/testing.md
## SCOPE: *.test.ts, *.test.tsx, *.spec.py, tests/
---

[TESTING RULES]
→ Reproduce the failure before writing the fix — write test first
→ One assertion per test — name describes exact behavior being tested
→ Use AAA pattern: Arrange → Act → Assert, separated by blank lines
→ Never mock bot/db.py internals — mock the SQLite connection instead
→ Test file mirrors source: bot/logger.py → tests/test_logger.py
→ Python tests: pytest, fixtures for SQLite in-memory DB (not real data/pollyedge.db)
→ TypeScript tests: vitest (already in vite ecosystem)
→ Risk rules are high-priority tests: 3% cap, 10% daily loss cap, 3 positions, 8% edge
→ Always test DRYRUN=true behavior separately from live behavior
→ Test Telegram approval timeout: 120s auto-reject behavior
→ No test should modify data/pollyedge.db — use in-memory SQLite for all tests


---
---
## FILE: .agents/rules/ai-agents.md
## LOCATION: .agents/rules/ai-agents.md
## SCOPE: bot/agents/, bot/orchestrator.py, bot/signalengine.py
---

[AI AGENT RULES]
→ All agents inherit from bot/agents/baseagent.py — never duplicate scan/signal logic
→ Orchestrator (orchestrator.py) coordinates agents — never places trades directly
→ Signal flow: agent.scan() → signalengine.py → riskmanager.py → approvalgate.py → trade
→ Risk manager gates every trade — no agent bypasses riskmanager.py
→ Approval gate: REQUIRE_APPROVAL=true sends to Telegram before execution
→ Each agent is responsible for ONE signal type only — no crossover logic
→ Agent parallelism: Python threading in orchestrator — never asyncio in bot code
→ load_dotenv must be first in every agent file — checked via AST before commit
→ Agent signals must include: label, side, size, edge, source, score, market_prob, model_prob
→ Min edge threshold: 8% — any signal below this is filtered before risk manager sees it
→ Never hardcode API keys — all via os.getenv after load_dotenv
→ Log every signal: found, rejected (with reason), and executed to logs/pollyedge.log


---
---
## REBUILD PROMPT
## Use this prompt to regenerate all files from this master source
---

Read the master source file I am providing. It contains all configuration files
for the PollyEdge project, separated by FILE and LOCATION headers.

Extract each file block and write it to its correct location:

  GEMINI.md                          → project root
  JARVIS_MEMORY.md                   → project root
  .agents/workflows/start.md         → create folder if missing
  .agents/rules/frontend.md          → create folder if missing
  .agents/rules/api.md               → create folder if missing
  .agents/rules/db.md                → create folder if missing
  .agents/rules/testing.md           → create folder if missing
  .agents/rules/ai-agents.md         → create folder if missing

Rules for extraction:
→ Each file block starts with: ## FILE: filename
→ Each file block ends at the next: ---\n---\n## FILE:
→ Strip the header comment lines (## FILE, ## LOCATION, ## SCOPE)
→ Write the file content exactly as-is — no modifications
→ Create all missing directories before writing files
→ After writing all files, print a checklist confirming each file was written
→ Then ask: "All files written. Type /start to begin your session."

