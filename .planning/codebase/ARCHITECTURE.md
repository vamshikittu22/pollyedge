# Architecture

**Analysis Date:** 2026-03-19

## Pattern Overview

**Overall:** Multi-tier architecture with a React dashboard frontend, Express.js API server, and Python trading bot orchestrator.

**Key Characteristics:**
- Frontend-backend co-location: Single Express server serves both API and React app
- Agent-based bot architecture: 5 parallel signal agents feeding into an approval queue
- File-based IPC: Python bot and Node.js server communicate via shared JSON files (`bot_state.json`, `agent_status.json`)
- Human-in-the-loop approval: Telegram integration for trade authorization
- Shared TypeScript schemas between client and server

## Layers

**Frontend (React):**
- Purpose: Trading dashboard UI
- Location: `client/src/`
- Contains: React components, pages, hooks, utilities
- Depends on: `@tanstack/react-query`, `wouter`, Tailwind CSS, Radix UI components
- Used by: Browser via Vite dev server or production build

**API Server (Express):**
- Purpose: REST API for bot status and control, serves static React build in production
- Location: `server/`
- Contains: Route handlers (`routes.ts`), storage layer (`storage.ts`), Vite setup (`vite.ts`)
- Depends on: Express 5.x, file system for state persistence
- Used by: React frontend via fetch API

**Trading Bot (Python):**
- Purpose: Autonomous trading with multi-agent signal generation
- Location: `bot/`
- Contains: Orchestrator, agents, risk manager, approval gate, notifier
- Depends on: web3, py-clob-client, requests, dotenv
- Used by: Terminal (standalone process)

**Python API Server (FastAPI):**
- Purpose: Alternative REST API (less used than Express server)
- Location: `api/server.py`
- Contains: FastAPI endpoints mirroring Express routes
- Used by: Can be run standalone on port 8000

**Shared Code:**
- Purpose: TypeScript schemas shared between client and server
- Location: `shared/schema.ts`
- Contains: Zod schemas for bot status, trades, approvals, agents

## Data Flow

**Bot Status Request:**
1. React dashboard polls `/api/bot/status` every 5 seconds
2. Express server reads from `bot_state.json` (written by Python bot)
3. Express server reads trades from `logs/trades.csv`
4. Express server reads pending approvals from `pending_approvals.json`
5. Express server reads agent status from `agent_status.json`
6. Response assembled and sent to React dashboard

**Trade Execution Flow:**
1. Python agents scan markets and generate signals
2. Signals sent to orchestrator via Python `queue.Queue`
3. Orchestrator scores and filters signals
4. Approval gate sends Telegram message for human confirmation
5. On approval, trade executed via `py_clob_client`
6. Trade recorded in `bot_state.json` and `logs/trades.csv`
7. Status files updated for dashboard polling

## Key Abstractions

**Orchestrator (Python):**
- Purpose: Coordinates 5 parallel agent threads
- Examples: `bot/orchestrator.py`
- Pattern: Thread-based parallelism with `ThreadPoolExecutor`

**BaseAgent (Python):**
- Purpose: Abstract base class for all signal agents
- Examples: `bot/agents/base_agent.py`
- Pattern: ABC with `scan()` abstract method

**MemStorage (TypeScript):**
- Purpose: File-based state management for Express server
- Examples: `server/storage.ts`
- Pattern: Singleton with file I/O

**BotStatus (TypeScript):**
- Purpose: Shared type definition for bot state
- Examples: `shared/schema.ts`
- Pattern: Zod schema with TypeScript inference

## Entry Points

**Frontend:**
- Location: `client/src/main.tsx`
- Triggers: Browser loads SPA
- Responsibilities: Mounts React app with QueryClient, Router, Toaster

**API Server:**
- Location: `server/index.ts`
- Triggers: `npm run dev` or `npm start`
- Responsibilities: Express app setup, route registration, HTTP server creation

**Trading Bot:**
- Location: `bot/pollyedge_bot.py`
- Triggers: `python bot/pollyedge_bot.py`
- Responsibilities: Initializes orchestrator, handles signals

**FastAPI Server:**
- Location: `api/server.py`
- Triggers: `uvicorn api.server:app --port 8000`
- Responsibilities: Alternative API serving

## Error Handling

**Strategy:** Fail-safe defaults with logging

**Patterns:**
- Bot: All exceptions caught in agent loops, logged to `logs/pollyedge.log`
- Server: Express error middleware catches and returns JSON error responses
- Approval gate: Returns `False` (reject) on any exception (fail-safe)
- Risk manager: Returns `(False, reason)` tuples for blocked trades

## Cross-Cutting Concerns

**Logging:** 
- Python: `logging` module with file + console handlers
- Node.js: Custom `log()` function in `server/index.ts`

**Validation:**
- TypeScript: Zod schemas in `shared/schema.ts`
- Python: Environment variable type coercion

**Authentication:** 
- None (internal dashboard, not exposed externally)

---

*Architecture analysis: 2026-03-19*
