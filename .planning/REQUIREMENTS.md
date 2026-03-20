# Requirements: Pollyedge

**Defined:** 2026-03-19
**Core Value:** You spend 5 minutes a day approving trades the bot already vetted.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Research Engine

- [ ] **RESR-01**: Bot scans Polymarket markets for opportunities
- [ ] **RESR-02**: Bot scans crypto markets (via ccxt) for opportunities
- [ ] **RESR-03**: Bot analyzes market trends (price action, volume)
- [ ] **RESR-04**: Bot analyzes news and sentiment for opportunities
- [ ] **RESR-05**: Bot scores each opportunity with conviction rating (0-100)

### Conviction Filter

- [ ] **FILT-01**: Only opportunities scoring above threshold surface to user
- [ ] **FILT-02**: Filter rules are configurable
- [ ] **FILT-03**: User can adjust conviction threshold

### Dashboard

- [ ] **DASH-01**: User can view live list of high-conviction opportunities
- [ ] **DASH-02**: Each opportunity shows analysis breakdown (why it's rated high)
- [ ] **DASH-03**: User can approve trade from dashboard
- [ ] **DASH-04**: User can reject trade from dashboard
- [ ] **DASH-05**: User can view trade history and outcomes
- [ ] **DASH-06**: User can view portfolio summary and P&L

### Execution

- [ ] **EXEC-01**: Approved Polymarket trades execute automatically
- [ ] **EXEC-02**: Trade outcomes tracked and recorded
- [ ] **EXEC-03**: Paper trading mode available (no real money)

### Foundation

- [ ] **FOUN-01**: FastAPI backend replaces Express server
- [ ] **FOUN-02**: SQLite database for storage layer
- [ ] **FOUN-03**: Real-time dashboard updates (polling or WebSocket)

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Extensions

- **EXT-01**: Telegram notifications for new opportunities
- **EXT-02**: Whale tracking (large Polymarket positions)
- **EXT-03**: Multi-exchange support (stocks, more crypto)
- **EXT-04**: Multi-user support
- **EXT-05**: Sentiment analysis from social media

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Autonomous execution | Human approval always required |
| Backtesting | Leads to overfitting; paper trading instead |
| Auto parameter optimization | Complexity, defer to v2 |
| Stocks integration | Start focused on Polymarket + crypto |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| RESR-01 | Phase 3 — Research Engine | Pending |
| RESR-02 | Phase 3 — Research Engine | Pending |
| RESR-03 | Phase 3 — Research Engine | Pending |
| RESR-04 | Phase 3 — Research Engine | Pending |
| RESR-05 | Phase 3 — Research Engine | Pending |
| FILT-01 | Phase 4 — Conviction Filter | Pending |
| FILT-02 | Phase 4 — Conviction Filter | Pending |
| FILT-03 | Phase 4 — Conviction Filter | Pending |
| DASH-01 | Phase 2 — Dashboard | Pending |
| DASH-02 | Phase 2 — Dashboard | Pending |
| DASH-03 | Phase 2 — Dashboard | Pending |
| DASH-04 | Phase 2 — Dashboard | Pending |
| DASH-05 | Phase 2 — Dashboard | Pending |
| DASH-06 | Phase 2 — Dashboard | Pending |
| EXEC-01 | Phase 5 — Execution | Pending |
| EXEC-02 | Phase 5 — Execution | Pending |
| EXEC-03 | Phase 5 — Execution | Pending |
| FOUN-01 | Phase 1 — Foundation | Pending |
| FOUN-02 | Phase 1 — Foundation | Pending |
| FOUN-03 | Phase 1 — Foundation | Pending |

**Coverage:**
- v1 requirements: 19 total
- Mapped to phases: 19
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-19*
*Roadmap created: 2026-03-19 — 19/19 requirements mapped to 5 phases*
