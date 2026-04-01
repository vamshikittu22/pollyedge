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
