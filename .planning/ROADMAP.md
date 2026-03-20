# Roadmap: Pollyedge

> **Reality Check (2026-03-20):** This roadmap has been rewritten based on a full codebase audit. The previous roadmap marked all phases as "Not started" but substantial code exists. This version reflects what actually needs to be built.

## Overview

A high-conviction trading command center. The bot researches opportunities across Polymarket and crypto using multiple signals, filters for high-confidence setups, and presents them on a web dashboard for human approval before execution.

## Current State (Audit Summary)

| Component | Status | Notes |
|-----------|--------|-------|
| Python Bot Core | ✅ Working | Multi-agent, Telegram approval, risk rules |
| Python Agents | ⚠️ 4/5 | MomentumAgent file missing (bot crashes on start) |
| TypeScript Server | ✅ Working | Express, 3 endpoints, polling |
| React Dashboard | ✅ Working | All major components functional |
| Database | ❌ Not Used | JSON files instead of SQLite |
| Real-time | ⚠️ Partial | 5s polling instead of WebSocket |
| Approvals → Dashboard | ❌ Broken | pending_approvals.json never written |
| Position Exit Logic | ❌ Missing | Positions never close |
| Deployment | ⚠️ Local Only | No Docker/systemd |

## Re-Phased Roadmap

### Phase 0: Critical Fixes
**Goal**: Bot starts cleanly, all 5 agents load, data flows correctly
**Depends on**: Nothing
**Why this phase exists**: 5 bugs prevent basic functionality. Fix these first before any new features.
**Success Criteria**:
1. `python -m bot.pollyedge_bot` starts without errors (all 5 agents load)
2. `pending_approvals.json` is written by Python and read by TypeScript
3. Approval queue shows live pending approvals on dashboard
4. `agent_status.json` is written by Python and read by TypeScript
5. Bot connects to Telegram and processes approval callbacks

**Plans:**
- [ ] 00-01: Fix MomentumAgent missing file + orchestrator imports
- [ ] 00-02: Wire pending_approvals.json (Python writes, TypeScript reads)
- [ ] 00-03: Fix agent_status.json writes + race conditions
- [ ] 00-04: Add position monitor (positions never close without this)
- [ ] 00-05: Fix log_trade() P&L logging + STARTING_BALANCE defaults

---

### Phase 1: Integration & Polish
**Goal**: Clean architecture, single source of truth, reliable data flow
**Depends on**: Phase 0 (needs working bot first)
**Success Criteria**:
1. SQLite replaces all JSON file storage (single source of truth)
2. Dashboard shows all data in real-time (≤2s latency)
3. Bot and dashboard share the same database (not file-based)
4. API is clean, documented, and stable

**Plans:**
- [ ] 01-01: Migrate bot_state.json → SQLite (Drizzle ORM)
- [ ] 01-02: Migrate agent_status.json → SQLite
- [ ] 01-03: Migrate pending_approvals.json → SQLite
- [ ] 01-04: Migrate logs/trades.csv → SQLite
- [ ] 01-05: Wire dashboard to read from SQLite (remove JSON file polling)

---

### Phase 2: Dashboard Completion
**Goal**: Full dashboard functionality — approve/reject from UI, live updates
**Depends on**: Phase 1 (needs clean data layer)
**Success Criteria**:
1. User can approve trades from dashboard (not just Telegram)
2. User can reject trades from dashboard
3. Dashboard shows opportunities with analysis breakdown
4. Real-time updates via WebSocket (not polling)
5. Conviction threshold adjustable from UI

**Plans:**
- [ ] 02-01: Add approve/reject buttons to dashboard + API endpoints
- [ ] 02-02: Display opportunity analysis breakdown per signal
- [ ] 02-03: Implement WebSocket/SSE for real-time updates
- [ ] 02-04: Add conviction threshold slider with live preview

---

### Phase 3: Research Engine Polish
**Goal**: All 5 agents working, better signal quality
**Depends on**: Phase 1 (needs storage layer)
**Success Criteria**:
1. All 5 agents generate signals (MomentumAgent fixed)
2. Each opportunity has clear analysis breakdown
3. Confidence score (0-100) shown for each signal
4. News + price action + sentiment all factored in

**Plans:**
- [ ] 03-01: Implement MomentumAgent (price mean-reversion)
- [ ] 03-02: Improve conviction scoring algorithm
- [ ] 03-03: Add Polymarket market discovery scanner
- [ ] 03-04: Improve opportunity display with full analysis

---

### Phase 4: Conviction Filter
**Goal**: Configurable, visible filtering — user controls what surfaces
**Depends on**: Phase 2 + Phase 3
**Success Criteria**:
1. Conviction threshold configurable from UI
2. Filter rules visible and adjustable (min volume, min edge, etc.)
3. Filter changes apply immediately (no restart needed)
4. Only opportunities scoring above threshold appear

**Plans:**
- [ ] 04-01: Threshold filter logic + UI controls
- [ ] 04-02: Additional filter rules (volume, edge, source weight)

---

### Phase 5: Execution & Production
**Goal**: Reliable live trading, production-ready deployment
**Depends on**: Phase 2 (approval actions) + Phase 4 (filtering)
**Success Criteria**:
1. Approved Polymarket trades execute via py-clob-client
2. Paper trading mode works (DRY_RUN=true)
3. Position monitoring with profit target + stop loss
4. Production deployment (Docker, systemd, monitoring)

**Plans:**
- [ ] 05-01: Integrate Polymarket CLOB execution for approved trades
- [ ] 05-02: Position monitor with profit target / stop loss
- [ ] 05-03: Production deployment (Docker, health checks, pm2)

---

## Phase Dependencies

```
Phase 0 (Critical Fixes)
    ↓
Phase 1 (Integration & Polish)
    ↓
  ┌──────────────────────────────────┐
  ↓                                  ↓
Phase 2                         Phase 3
(Dashboard Completion)      (Research Polish)
  ↓                                  ↓
  └──────────────┬───────────────────┘
                 ↓
           Phase 4
        (Conviction Filter)
                 ↓
           Phase 5
         (Execution)

```

## Progress

| Phase | Status | Plans | Progress |
|-------|--------|-------|----------|
| 0. Critical Fixes | ✅ Complete | 5/5 | 100% |
| 1. Integration | Not started | 5 | 0% |
| 2. Dashboard | Not started | 4 | 0% |
| 3. Research | Not started | 4 | 0% |
| 4. Conviction Filter | Not started | 2 | 0% |
| 5. Execution | Not started | 3 | 0% |

---

## Original Roadmap vs Re-Phased

| Original | Re-Phased | Why Changed |
|----------|-----------|-------------|
| Phase 1: Foundation | Phase 1: Integration | FastAPI+SQLite already 75% done; Express+JSON is working |
| Phase 2: Dashboard | Phase 2: Dashboard | Mostly built; missing approve/reject from UI |
| Phase 3: Research Engine | Phase 3: Research Polish | 4/5 agents work; MomentumAgent missing |
| Phase 4: Conviction Filter | Phase 4: Conviction Filter | Moved after dashboard (needs UI first) |
| Phase 5: Execution | Phase 5: Execution | Position exit + production added |
| — | Phase 0: Critical Fixes | **NEW** — 5 bugs block basic functionality |

---

*Last updated: 2026-03-20 — Phase 0 complete (all 5 critical fixes)*
