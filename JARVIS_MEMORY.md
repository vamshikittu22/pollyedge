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
