# Codebase Concerns

**Analysis Date:** 2026-03-19

## Tech Debt

**File-based IPC between Python and Node.js:**
- Issue: Bot state communicated via JSON files read/written by both processes
- Files: `bot_state.json`, `agent_status.json`, `pending_approvals.json`
- Impact: Race conditions possible, polling required for updates
- Fix approach: Use a message queue (Redis pub/sub, RabbitMQ) or WebSocket for real-time updates

**Dual API servers:**
- Issue: Both Express (`server/`) and FastAPI (`api/server.py`) provide similar endpoints
- Files: `server/routes.ts`, `api/server.py`
- Impact: Maintenance duplication, potential for divergent behavior
- Fix approach: Consolidate on one API (likely Express since it's already serving the frontend)

**No test coverage:**
- Issue: No automated tests detected
- Files: Entire codebase
- Impact: Changes may break functionality undetected
- Fix approach: Add Vitest for frontend, pytest for bot

## Known Bugs

**No documented bugs in code comments or issue tracking detected.**

## Security Considerations

**Private key exposure:**
- Risk: `PRIVATE_KEY` stored in `.env` file
- Files: `.env` (not committed but exists locally)
- Current mitigation: `.gitignore` excludes `.env`
- Recommendations: Consider key management service, never commit secrets

**Telegram token exposure:**
- Risk: Bot token and chat ID in environment variables
- Files: `.env`, `bot/approval_gate.py`
- Current mitigation: Environment-based configuration
- Recommendations: Same as above

**CORS wide open:**
- Risk: `allow_origins=["*"]` in FastAPI
- Files: `api/server.py`
- Impact: Any website can make API requests
- Current mitigation: Not externally exposed (internal dashboard)
- Recommendations: Restrict to dashboard domain in production

## Performance Bottlenecks

**Polling-based dashboard refresh:**
- Problem: Frontend polls `/api/bot/status` every 5 seconds
- Files: `client/src/pages/dashboard.tsx`
- Cause: File-based IPC requires polling to detect changes
- Improvement path: WebSocket or SSE for real-time updates

**Agent scan intervals:**
- Problem: Agents scan with fixed intervals (30s default)
- Files: `bot/agents/base_agent.py`, individual agents
- Cause: Simple time.sleep() loops
- Improvement path: Async agents with proper scheduling

## Fragile Areas

**File I/O with no locks:**
- Files: `server/storage.ts`, `bot/risk_manager.py`
- Why fragile: Concurrent reads/writes to JSON files could corrupt data
- Safe modification: Add file locking or switch to database
- Test coverage: None

**Approval gate polling:**
- Files: `bot/approval_gate.py`
- Why fragile: Telegram polling with fixed timeout could miss responses
- Safe modification: Consider Telegram webhook instead of polling

## Scaling Limits

**Single-process bot:**
- Current capacity: 5 agents in threads
- Limit: GIL constraints, thread overhead
- Scaling path: Move to async/await or multiprocessing

**File-based storage:**
- Current capacity: Small number of concurrent users
- Limit: File I/O doesn't scale
- Scaling path: PostgreSQL (already included in stack)

## Dependencies at Risk

**py-clob-client:**
- Risk: External API client could break with API changes
- Impact: Trading functionality stops
- Migration plan: Monitor API changelog, pin to specific version

**Radix UI (many packages):**
- Risk: Multiple packages to update
- Impact: UI could break on major version updates
- Migration plan: Update one at a time, test thoroughly

## Missing Critical Features

**Error boundaries:**
- Problem: React components lack error boundaries
- Blocks: Dashboard crashes on unexpected errors

**Input validation:**
- Problem: API routes trust client input
- Blocks: Malformed requests could cause issues

**Logging/monitoring:**
- Problem: No structured logging or error tracking
- Blocks: Production debugging difficult

## Test Coverage Gaps

**API routes:**
- What's not tested: All route handlers
- Files: `server/routes.ts`
- Risk: Breaking changes go unnoticed
- Priority: High

**Bot trading logic:**
- What's not tested: Risk manager, approval gate, orchestrator
- Files: `bot/*.py`
- Risk: Trading losses from bugs
- Priority: Critical

**React components:**
- What's not tested: All dashboard components
- Files: `client/src/components/`
- Risk: UI bugs undetected
- Priority: Medium

---

*Concerns audit: 2026-03-19*
