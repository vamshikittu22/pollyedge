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
| RESR-01 | — | Pending |
| RESR-02 | — | Pending |
| RESR-03 | — | Pending |
| RESR-04 | — | Pending |
| RESR-05 | — | Pending |
| FILT-01 | — | Pending |
| FILT-02 | — | Pending |
| FILT-03 | — | Pending |
| DASH-01 | — | Pending |
| DASH-02 | — | Pending |
| DASH-03 | — | Pending |
| DASH-04 | — | Pending |
| DASH-05 | — | Pending |
| DASH-06 | — | Pending |
| EXEC-01 | — | Pending |
| EXEC-02 | — | Pending |
| EXEC-03 | — | Pending |
| FOUN-01 | — | Pending |
| FOUN-02 | — | Pending |
| FOUN-03 | — | Pending |

**Coverage:**
- v1 requirements: 19 total
- Mapped to phases: 0
- Unmapped: 19 ⚠️

---
*Requirements defined: 2026-03-19*
*Last updated: 2026-03-19 after initial definition*
