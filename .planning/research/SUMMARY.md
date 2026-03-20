# Project Research Summary

**Project:** Pollyedge — High-Conviction Trading Command Center
**Domain:** Trading Research + Human-in-the-Loop Approval System
**Researched:** 2026-03-19
**Confidence:** MEDIUM-HIGH

---

## Executive Summary

Pollyedge is a signal-to-approval trading pipeline that monitors prediction markets (Polymarket), crypto, and stocks — then presents high-conviction setups to a human for approval before executing. The core insight from research: the real moat is not the signal engine, it's the conviction scoring + approval UX that filters noise and keeps humans engaged rather than fatigued.

**Experts build this as a 6-layer pipeline:** Signal Engine (agents scan market data) → Orchestration (score + deduplicate) → Risk Management (policy checks) → Approval Gate (human decides) → Execution (exchange API) → Dashboard (monitor everything). Pollyedge already has working implementations of all 6 layers. The roadmap is not about building from scratch — it's about hardening, scaling, and enriching.

**Recommended approach:** Start with a stable Polymarket-only MVP. The tech stack is verified: FastAPI + Pydantic V2 + SQLAlchemy 2.0 (async) for the backend, Next.js + TypeScript + shadcn/ui + TanStack Query for the dashboard, py-clob-client for Polymarket execution. Keep SQLite for local dev, PostgreSQL for production. Replace Express polling with FastAPI WebSocket in v2. Defer Celery/Temporal/Redis until distributed workflows are actually needed.

**Key risks:** Backtest overfitting will destroy confidence. Approval fatigue will kill user adoption. Polymarket API complexity (dual APIs, rate limits, auth) will break the pipeline. All three must be addressed in Phase 1, not patched later.

---

## Key Findings

### Recommended Stack

**Backend:** FastAPI (~0.115) + Pydantic V2 (~2.10) + SQLAlchemy 2.0 async + asyncpg. Python 3.10+. APScheduler (~3.10) for in-process scheduling — no Celery/Temporal for MVP. Redis (~7) for caching + pub/sub. pydantic-settings for env-based config, structlog for JSON logging, httpx for async HTTP, tenacity for retries.

**Frontend:** Next.js (15/16) + TypeScript (~5.8) + shadcn/ui (copy-paste, Tailwind-based) + Tailwind CSS v4. TanStack Query (~5.83) for server state + polling. Recharts (~3.0) for analytics charts, Framer Motion for animations.

**Data Sources:** py-clob-client (official Polymarket SDK, EIP-712 auth) for execution. Polymarket Gamma API (REST) for market discovery. ccxt (~4.0) for multi-exchange crypto data (Phase 2+). yfinance (~0.2) for stock data (unreliable for production — premium source needed for v2). Tavily AI or DuckDuckGo for news signals.

**DevOps:** Docker + docker-compose. pytest + pytest-asyncio. uv for Python package management (10-100x faster than pip, lockfile support). Ruff for linting + formatting.

**Approval Pattern:** Database-backed queue is the right choice for MVP. Simple, auditable, no extra infrastructure. Upgrade to Temporal only when multi-step approval workflows emerge.

### Expected Features

**Must have (table stakes):**
- Market data display (Polymarket Gamma API + crypto feeds) — no current prices = broken product
- Signal/opportunity list view with conviction score — core UX artifact
- Approve/Reject action buttons — the entire workflow depends on this
- Trade execution via Polymarket CLOB API — approved trades must execute
- Basic P&L tracking (unrealized + realized) — "did I make money?" is the first question
- Audit trail (all signals, approvals, rejections, executions with timestamps)
- Web dashboard (single-page, mobile-friendly)

**Should have (competitive differentiators):**
- Conviction scoring tiers (HIGH/MED/LOW) — the filter between signal flood and approval fatigue
- Whale tracking / smart money monitoring — Polymarket whale positions as signal input
- News + sentiment analysis — AI-synthesized sentiment as signal source
- Telegram bot for approvals — critical for "5 minutes a day" UX
- Multi-exchange support (Binance, Coinbase) — unified signal across venues

**Defer to v2+:**
- Market regime detection — complex, requires extensive validation
- Cross-market correlation graph — nice visualization, low priority
- Stocks integration with premium data (Polygon.io, Alpaca) — yfinance unreliable
- Advanced risk models (Monte Carlo, VaR) — creates paralysis, not protection
- Automated parameter optimization — static perfection collapses when conditions change

### Architecture Approach

Pollyedge already implements the correct 6-layer pipeline. The architecture research confirms the component boundaries: agents emit signals only (never call RiskManager), orchestrator coordinates and scores, RiskManager returns (allowed, reason) tuples without knowing about execution, ApprovalGate returns True/False without executing, dashboard is display-only (only killswitch action). The existing multi-agent signal swarm (5 parallel agents), score-based conviction filter (0-100), and database-backed HITL approval are all validated patterns.

**Major components:**
1. **Signal Engine (agents)** — parallel scanning of Polymarket, crypto, news. Each outputs raw signals to a queue. Must remain independently testable.
2. **Orchestration Layer** — deduplicates signals, applies conviction scoring (0-100, threshold 50), routes to risk + approval. The coordination layer, not a calculation layer.
3. **Risk Management Layer** — policy engine. Max position size, daily loss cap, max open positions, minimum balance. Single audit point, called before every trade.
4. **Approval Gate Layer** — human HITL boundary. Presents structured proposal, blocks up to 120s, returns True/False. Never executes trades.
5. **Execution Layer** — Polymarket CLOB via py-clob-client. Market orders with FOK. Logs to trades.csv. PaperExecutionEngine not yet implemented.
6. **Presentation Layer** — React dashboard via Express/Next.js. Polls bot_state.json + agent_status.json + trades.csv every 5s. Kill switch is the only trading-adjacent action.

**Data flow:** Agents → queue.Queue → Orchestrator (dedup + score) → RiskManager (can_trade check) → ApprovalGate (blocking human decision) → Execution (py_clob_client) → Notifier (Telegram/Discord) → Dashboard polling.

### Critical Pitfalls

1. **Backtest Overfitting (Curve Fitting)** — The #1 killer of trading bots. 90% of profitable backtests are statistically invalid. Limit to 3-5 parameters. Use walk-forward validation. Require out-of-sample Sharpe > 1.0. Add 30-50% transaction cost buffer. **Phase to address: Signal Engine Phase.**

2. **Signal Lag / Timing Decay** — 74% of popular indicators generate signals 2-8 candles after optimal entry. Single-dimension indicators don't account for market context. Measure latency, prefer leading indicators (volume, order flow) over lagging (moving averages, RSI). **Phase to address: Signal Engine Phase.**

3. **Approval Workflow Review Fatigue** — The #1 failure mode for HITL systems. Without strict filtering, users get 50+ approvals/day and start auto-approving or abandoning. Present max 5-10 signals/day. Implement confidence tiers. **Phase to address: Approval Interface Phase.**

4. **False Signal Flood (Noisy Signal Filtering)** — False signal rates can exceed 76% for certain indicator configs. Require 2-3 independent signals to align. Filter by market regime. Track win rate over time. **Phase to address: Signal Engine Phase.**

5. **Polymarket API Integration Complexity** — Dual APIs (US CFTC-regulated vs Global crypto-native). Tiered rate limits (15k/10s general, 9k/10s CLOB). Auth requires proxy wallet architecture. 401 errors from token expiry. 429 errors from rate limit exhaustion. **Phase to address: Integration Phase (immediately).**

---

## Implications for Roadmap

Based on the 6-layer architecture and the pitfall-to-phase mapping, the following phase structure minimizes risk and maximizes learning:

### Phase 1: Core Pipeline Stabilization + Polymarket Integration

**Rationale:** The existing pipeline is architecturally sound but unproven in production. Before adding features, the foundation must be hardened. Polymarket API complexity (dual APIs, rate limits, auth) is the most immediate blocker — it affects every downstream feature.

**Delivers:**
- Fixed Polymarket CLOB integration (US/Global detection, EIP-712 auth, rate limit handling with backoff, 401 recovery)
- Polymarket Gamma API scanner (market discovery, volume, liquidity)
- Conviction scoring confidence tiers (HIGH/MED/LOW — addresses Approval Fatigue pitfall)
- Paper trading mode with realistic fill simulation (addresses Look-Ahead Bias pitfall)
- Integration tests for signal lifecycle

**Addresses from FEATURES.md:** Market data display, signal/opportunity list, conviction scoring, trade execution (Polymarket only), basic P&L, audit trail

**Avoids from PITFALLS.md:** Polymarket API issues (P5), Approval fatigue (P3) via conviction tiers, Look-Ahead bias (P6) via paper trading

**Stack elements used:** FastAPI, Pydantic V2, py-clob-client, APScheduler, SQLite, uv, pytest

---

### Phase 2: Scanner Extraction + Signal Quality Validation

**Rationale:** Agents currently mix data fetching with signal logic. Extracting scanners makes each independently testable and swappable. This is also when backtest methodology and signal timing validation must be built — before conviction scores are trusted with real capital.

**Delivers:**
- `bot/scanners/` module: polymarket_scanner.py, crypto_scanner.py, news_scanner.py
- Signal deduplication improvements (cross-agent correlation)
- Signal quality tracking (win rate per source, signal history)
- Multi-factor signal filtering (require 2-3 independent confirmations)
- Walk-forward validation framework for backtests

**Addresses from FEATURES.md:** Multi-signal research engine (partial), whale tracking integration (Polymarket-specific)

**Avoids from PITFALLS.md:** Backtest overfitting (P1), Signal lag (P2), False signal flood (P4)

**Stack elements used:** SQLAlchemy 2.0 async, Redis (for signal caching), ccxt (for multi-exchange), httpx, tenacity

---

### Phase 3: Dashboard Enhancement + Storage Layer

**Rationale:** The current Express/React dashboard reads from JSON files. This phase migrates to a proper FastAPI backend with SQLite (or PostgreSQL) storage, enabling the in-app approval queue UI. This is also when Telegram approvals get the full treatment (rich messages, inline keyboard).

**Delivers:**
- FastAPI backend replacing Express server (unified Python codebase)
- `bot/storage/` module: state_store.py, trade_store.py, agent_store.py
- SQLite → PostgreSQL migration path (single command swap)
- In-app approval queue UI (browsable, sortable, filterable — not just Telegram)
- Agent status cards and per-agent signal quality metrics in dashboard
- Shared `shared/signals.ts` contract (TypeScript ↔ Python schema alignment)

**Addresses from FEATURES.md:** Web dashboard (enhanced), approval workflow (in-app option), Telegram bot for approvals

**Avoids from PITFALLS.md:** Approval fatigue via improved UX (browsable queue, signal context, historical accuracy per signal)

---

### Phase 4: Paper Trading Validation + Real-Time Data

**Rationale:** Before risking capital, the full paper trading pipeline must run live. This phase also replaces the 5s file-polling with WebSocket/SSE for sub-second dashboard updates — critical when trades are live.

**Delivers:**
- Full paper trading pipeline with slippage/fee modeling
- Paper trading vs backtest comparison (must match within 20% — Look-Ahead Bias check)
- WebSocket server (FastAPI WebSockets + SSE) replacing polling
- Redis pub/sub for real-time state broadcast
- Position size validation + risk metrics display (risk/reward ratio, max drawdown)

**Addresses from FEATURES.md:** Alert/notification system, price charts (TradingView Lightweight Charts for candlesticks)

---

### Phase 5: Multi-Exchange + Multi-User Extension

**Rationale:** At this point the system is proven on Polymarket. Adding Binance/Coinbase support and multi-user portfolios requires PostgreSQL (user accounts, per-user portfolios, shared signal pool) and Celery+Redis for distributed task handling.

**Delivers:**
- Multi-exchange support (ccxt for Binance, Kraken, Coinbase)
- PostgreSQL backend with user authentication (NextAuth.js or Clerk)
- Per-user approval queues with individual kill switches
- Shared signal pool across exchanges
- Alert/notification system (web push, email)

**Addresses from FEATURES.md:** Multi-exchange support, alert system, multi-signal research engine (complete)

**Avoids from PITFALLS.md:** State file contention (multiple users reading/writing), scalability bottlenecks

---

### Phase 6: Advanced Intelligence (v2+)

**Rationale:** Once signal quality data is rich, proprietary intelligence features can be built on top.

**Delivers:**
- Market regime detection (trend vs. range filtering)
- Whale tracking (on-chain analysis for Polymarket wallets)
- News + social sentiment scoring (AI-synthesized)
- Cross-market correlation graph
- Advanced risk models (optional, opt-in)

---

### Phase Ordering Rationale

1. **Polymarket integration first** — it's the primary venue and every other phase depends on having live market data. API complexity must be solved immediately.
2. **Scanner extraction before dashboard enhancement** — don't polish the presentation layer until the data pipeline is clean and testable.
3. **Paper trading before any real capital** — backtest overfitting and look-ahead bias are existential risks. Paper validation is the gatekeeper to Phase 5.
4. **SQLite → PostgreSQL migration after signal quality is established** — don't add user complexity until the signal pipeline is proven. SQLite is fine for a single-user proof-of-concept.
5. **Multi-exchange after Polymarket-only validation** — Polymarket's binary-outcome microstructure is unique. Prove the conviction scoring works there first, then generalize.

### Research Flags

- **Phase 1 (Polymarket Integration):** Needs deeper research on Polymarket US vs Global API auth architecture, rate limit handling specifics, and EIP-712 signature implementation details.
- **Phase 2 (Signal Quality):** Needs statistical methodology review for walk-forward validation and conviction scoring weight calibration.
- **Phase 4 (Paper Trading):** Needs research on realistic slippage/fill modeling for Polymarket's AMM model (not standard order book).
- **Phase 5 (Multi-User):** Needs research on PostgreSQL schema for per-user portfolios and shared signal pools.

**Phases with standard patterns (skip research-phase):**
- **Phase 3 (Dashboard Enhancement):** Next.js + TanStack Query + shadcn/ui patterns are well-documented.
- **Phase 1 (FastAPI setup):** FastAPI + SQLAlchemy 2.0 async patterns are verified via multiple 2026 sources.
- **Phase 1 (Docker):** Standard Docker patterns for trading bots, documented across multiple 2026 guides.

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | FastAPI + Pydantic + SQLAlchemy + Next.js + shadcn/ui all verified via multiple 2026 sources and official docs. uv is newer but backed by Astral. |
| Features | MEDIUM | WebSearch-heavy research. Competitor analysis and feature matrix from secondary sources. MVP definition is solid; v2+ features need user validation. |
| Architecture | MEDIUM-HIGH | Standard 6-layer pipeline validated across 10+ sources. Pollyedge existing implementation maps well. Some gaps (PaperExecutionEngine, scanner extraction) need detailed design. |
| Pitfalls | MEDIUM-HIGH | Statistical claims (90% overfit, 74% lag, 76% false signals) sourced from 2026 articles. Recovery strategies are practical. Polymarket API gotchas are verified via pm.wiki and agentbets.ai (March 2026). |

**Overall confidence:** MEDIUM-HIGH. The architecture and stack are well-researched. Features need user validation to prioritize. Pitfall prevention needs implementation verification.

### Gaps to Address

- **Conviction scoring weights:** The 0-100 scoring (edge 40pts, reliability 10-25pts, volume 0-20pts, confirmations 0-30pts) is reasonable but not validated. Needs backtest + paper trading to calibrate.
- **Polymarket US vs Global API decision:** Not determined yet. This affects wallet architecture and regulatory considerations. Must resolve in Phase 1.
- **News signal reliability:** Tavily has API costs, DuckDuckGo reliability varies. Need to validate which news source provides sufficient signal quality for the sentiment agent.
- **Frontend/backend split:** Current Express server + Python bot with file polling. Research recommends FastAPI backend (unified Python). Decision needed on whether to migrate Express → FastAPI or keep parallel stacks.
- **Multi-user requirements:** Not fully defined. PostgreSQL migration path exists but user auth, portfolio isolation, and shared signal pool semantics need clearer requirements.

---

## Sources

### Primary (HIGH confidence)
- [FastAPI Official Docs](https://fastapi.tiangolo.com/) — Pydantic V2 integration, async patterns, production deployment
- [FastAPI Release Notes](https://fastapi.tiangolo.com/release-notes/) — Version compatibility, Pydantic V2 drop
- [pm.wiki Polymarket API Guide (March 2026)](https://pm.wiki/learn/polymarket-api) — CLOB, Gamma, Data API, auth
- [agentbets.ai Polymarket Bot Quickstart (2026)](https://agentbets.ai/guides/polymarket-bot-quickstart/) — SDK patterns, architecture
- [Astral uv + FastAPI Docs](https://docs.astral.sh/uv/guides/integration/fastapi/) — uv project setup
- [TanStack Ecosystem 2026 Guide](https://codewithseb.com/blog/tanstack-ecosystem-complete-guide-2026) — Query, Table, Router
- [Algovantis: Signal-to-Execution Pipeline (2026)](https://algovantis.com/algo-trading-signal-generation-to-execution-pipeline-architecture/) — 6-layer architecture model
- [PickMyTrade Blog: Backtest Curve Fitting (2026)](https://pickmytrade.com) — Overfitting statistics, walk-forward validation
- [Quantified Strategies: False Signal Rates (2025)](https://quantifiedstrategies.com) — MA strategy false signal rates

### Secondary (MEDIUM confidence)
- [Mastra: HITL Approval Patterns (2026)](https://mastra.ai/blog/hitl-where-to-put-approval-in-agents-and-workflows) — Where to place human approval
- [Dev Genius: Polymarket + Kalshi Two-Layer System (2026)](https://blog.devgenius.io/just-built-a-two-layer-ai-system-that-trades-polymarket-and-kalshi-while-i-sleep-heres-the-aa59ead275f6) — Architecture reference
- [Dev.to: shadcn/ui Cheat Sheet 2026](https://dev.to/codedthemes/shadcnui-cheat-sheet-2026) — Component patterns
- [OneUptime: SQLAlchemy 2.0 + FastAPI Async](https://oneuptime.com/blog/post/2026-01-27-sqlalchemy-fastapi) — Async patterns
- [Medium (Ravi Palwe): Review Fatigue Breaking HITL AI (2026)](https://medium.com/@ravipalwe) — Approval fatigue statistics
- [Cordum: HITL AI Patterns (2026)](https://cordum.io/blog/human-in-the-loop-ai-patterns) — Enterprise HITL workflows

### Tertiary (LOW confidence — needs validation)
- [Kalena Research: 74% indicator lag (2026)](https://kalenaresearch.com) — Indicator timing statistics (single source)
- [BullByte Medium: 90% signal failure (2026)](https://medium.com/@bullbyte) — Signal failure rate (single source, needs corroboration)
- [yfinance reliability](https://pypi.org/project/yfinance/) — Unofficial API, frequent changes, needs production validation
- News signal sources (DuckDuckGo, Tavily) — Not validated for trading signal quality

---

*Research completed: 2026-03-19*
*Ready for roadmap: YES*
