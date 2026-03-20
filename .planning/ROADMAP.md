# Roadmap: Pollyedge

## Overview

A high-conviction trading command center. The bot researches opportunities across Polymarket and crypto using multiple signals, filters for high-confidence setups, and presents them on a web dashboard for human approval before execution. The journey: build the foundation → surface opportunities → analyze signals → filter noise → execute trades.

## Phases

- [ ] **Phase 1: Foundation** - FastAPI backend, SQLite storage, real-time dashboard updates
- [ ] **Phase 2: Dashboard** - Live opportunity display, approve/reject workflow, P&L tracking
- [ ] **Phase 3: Research Engine** - Market scanners, trend analysis, news sentiment, conviction scoring
- [ ] **Phase 4: Conviction Filter** - Threshold-based surfacing, configurable rules, user-adjustable settings
- [ ] **Phase 5: Execution** - Automatic trade execution, outcome tracking, paper trading mode

## Phase Details

### Phase 1: Foundation
**Goal**: API backend, storage layer, and real-time communication are in place
**Depends on**: Nothing (first phase)
**Requirements**: FOUN-01, FOUN-02, FOUN-03
**Success Criteria** (what must be TRUE):
  1. FastAPI server is running and responding to requests (replaces Express)
  2. SQLite database stores and retrieves opportunities, trades, and agent state across restarts
  3. Dashboard receives live updates without manual refresh (WebSocket or SSE)
**Plans**: 3 plans

Plans:
- [ ] 01-01: Set up FastAPI project with Pydantic models and SQLite via SQLAlchemy
- [ ] 01-02: Migrate data models (opportunities, trades, agent state) to SQLite
- [ ] 01-03: Implement WebSocket/SSE endpoint for real-time dashboard updates

### Phase 2: Dashboard
**Goal**: Users can view opportunities, make decisions, and track performance
**Depends on**: Phase 1
**Requirements**: DASH-01, DASH-02, DASH-03, DASH-04, DASH-05, DASH-06
**Success Criteria** (what must be TRUE):
  1. User sees a live list of high-conviction opportunities on the dashboard
  2. Each opportunity shows why it's rated high (analysis breakdown visible)
  3. User can approve a trade with one click and see confirmation
  4. User can reject a trade and it disappears from the active list
  5. User can view complete trade history with outcomes
  6. User can view portfolio summary with P&L figures
**Plans**: 4 plans

Plans:
- [ ] 02-01: Build React dashboard pages (opportunities list, trade history, portfolio)
- [ ] 02-02: Display analysis breakdown per opportunity (why it's rated high)
- [ ] 02-03: Implement approve/reject actions wired to FastAPI endpoints
- [ ] 02-04: Build portfolio summary page with P&L calculations

### Phase 3: Research Engine
**Goal**: Bot scans Polymarket and crypto markets, analyzes signals, and scores each opportunity
**Depends on**: Phase 1 (needs storage and real-time pipeline)
**Requirements**: RESR-01, RESR-02, RESR-03, RESR-04, RESR-05
**Success Criteria** (what must be TRUE):
  1. Bot discovers active Polymarket markets and evaluates them as opportunities
  2. Bot fetches crypto market data via ccxt and evaluates it as opportunities
  3. Bot analyzes price action and volume trends for each market scanned
  4. Bot evaluates news and sentiment signals for each market scanned
  5. Each opportunity receives a conviction score (0-100) that reflects confidence
**Plans**: 5 plans

Plans:
- [ ] 03-01: Build Polymarket scanner (market discovery via Gamma API)
- [ ] 03-02: Build crypto scanner (ccxt integration for price/volume data)
- [ ] 03-03: Build trend analyzer (price action, volume patterns)
- [ ] 03-04: Build news analyzer (sentiment signal for markets)
- [ ] 03-05: Implement conviction scoring (0-100) for each opportunity

### Phase 4: Conviction Filter
**Goal**: Only high-confidence opportunities surface to users; rules are configurable
**Depends on**: Phase 3 (needs scored opportunities to filter)
**Requirements**: FILT-01, FILT-02, FILT-03
**Success Criteria** (what must be TRUE):
  1. Only opportunities scoring above the configured threshold appear on the dashboard
  2. Filter rules (thresholds, minimums) are stored in config and load on startup
  3. User can adjust conviction threshold in the dashboard and see results change immediately
**Plans**: 2 plans

Plans:
- [ ] 04-01: Implement threshold filter (only score ≥ threshold pass through)
- [ ] 04-02: Add threshold adjustment UI in dashboard with live preview

### Phase 5: Execution
**Goal**: Approved trades execute automatically; outcomes are tracked; paper mode is available
**Depends on**: Phase 2 (approval actions) and Phase 4 (filter gates trades)
**Requirements**: EXEC-01, EXEC-02, EXEC-03
**Success Criteria** (what must be TRUE):
  1. Approved Polymarket trade executes automatically via py-clob-client
  2. Trade outcomes (profit/loss, status) are recorded and retrievable
  3. User can toggle paper trading mode; no real money moves in paper mode
**Plans**: 3 plans

Plans:
- [ ] 05-01: Integrate Polymarket CLOB execution for approved trades
- [ ] 05-02: Build trade outcome tracking (fills, P&L, status)
- [ ] 05-03: Implement paper trading mode with simulated fills

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation | 0/3 | Not started | - |
| 2. Dashboard | 0/4 | Not started | - |
| 3. Research Engine | 0/5 | Not started | - |
| 4. Conviction Filter | 0/2 | Not started | - |
| 5. Execution | 0/3 | Not started | - |
