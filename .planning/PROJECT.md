# Pollyedge

## What This Is

A high-conviction trading command center. Bot researches opportunities across Polymarket, crypto, and stocks using multiple signals (trends, news, patterns), filters for only the best setups, and presents them for human approval before execution.

## Core Value

You spend 5 minutes a day approving trades the bot already vetted.

## What Was Built (2026-03-20 Audit)

After a full codebase audit, here's what actually exists:

### Working ✅
- **Python bot core**: Multi-agent orchestrator (4/5 agents), Telegram approval gate, risk management rules
- **4 functional agents**: EarningsAgent, NewsAgent, ArbAgent, CryptoAgent
- **TypeScript server**: Express on port 5000, 3 API endpoints, reads from JSON files
- **React dashboard**: All major components (BalanceCard, TradesTable, ApprovalQueue, etc.), 5s polling
- **Approval workflow**: Telegram inline buttons for approve/reject
- **Trade logging**: CSV file + JSON state persistence
- **Risk rules**: Daily loss cap, max positions, kill switch

### Broken ⚠️
- **MomentumAgent**: File missing — bot crashes on startup
- **pending_approvals.json**: Never written by Python — dashboard queue empty
- **Position exits**: No logic to close positions at profit target/stop loss
- **log_trade P&L**: Always logs 0.0 (called at entry, not exit)
- **agent_status.json race condition**: Plain set, not thread-safe

### Missing ❌
- **SQLite**: Roadmap says SQLite, code uses JSON files
- **WebSocket**: Roadmap says WebSocket, code uses polling
- **Dashboard approve/reject**: UI has queue but no buttons
- **Conviction threshold UI**: Hardcoded, not adjustable from dashboard
- **FastAPI**: Exists but unused (Express is running)
- **Production deployment**: Local dev only

## Key Decisions

| Decision | Rationale | Status |
|----------|-----------|--------|
| JSON files over SQLite | Simpler for rapid iteration, shared state between Python + TS | Working — but migrate later |
| Express over FastAPI | Already deployed, works fine | Working — FastAPI exists but unused |
| Telegram approval first | Mobile-friendly, notifications | Working |
| DRY_RUN=true default | Safety first, paper trade before real money | Working |
| CoinGecko over ccxt | Simpler API, sufficient for 24h changes | Working |
| JSON polling over WebSocket | Simpler to implement, good enough for 5s updates | Working |

## Constraints

- **Approval required**: No fully autonomous trades — human must approve every trade
- **High conviction only**: Bot filters aggressively, surfaces only the best setups
- **Start focused**: Polymarket and crypto first, stocks later
- **Paper trading first**: DRY_RUN=true until confidence built

## Out of Scope (Deferred)

| Feature | Reason |
|---------|--------|
| Autonomous execution | Human approval always required |
| Backtesting | Leads to overfitting; paper trading instead |
| Auto parameter optimization | Complexity, defer to v2 |
| Stocks integration | Start focused on Polymarket + crypto |
| Multi-user support | Single user for now |
| Social media sentiment | Defer to v2 |

---

*Last updated: 2026-03-20 after full codebase audit*
