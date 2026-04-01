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
