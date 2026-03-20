# Architecture Research

**Domain:** Trading Research + Approval Systems (High-Conviction Command Center)
**Researched:** 2026-03-19
**Confidence:** MEDIUM-HIGH

> This document covers the standard architecture for trading research + human-approval pipelines, maps Pollyedge existing components onto that model, and identifies gaps, data flow, and build-order implications for roadmap phasing.

---

## Standard Architecture: Signal-to-Approval Pipeline

Every trading system with human-in-the-loop (HITL) approval follows the same layered structure. The research identifies a **6-layer pipeline** consistent across Polymarket bots, general algo trading platforms, and enterprise-grade trading systems.

```
Presentation Layer    -- Dashboard UI (React) + Approval UI (Telegram/Web)
Approval Gate Layer   -- Human HITL Gate + Auto-filter (score threshold)
Orchestration Layer  -- Signal scoring + Deduplication + Routing
Signal Engine Layer  -- Market Scanner + Multi-Agent Swarm (signals merge here)
Risk Management Layer -- Position sizing + Drawdown limits + Kill switches
Execution Layer       -- Order Management + Exchange API (Polymarket CLOB) + DB
```

### Why 6 Layers?

Each layer has exactly one responsibility, confirmed across all sources:

- **Execution Layer** changes whenever the exchange API changes (Polymarket CLOB vs Binance vs Coinbase).
- **Risk Layer** is policy -- it must be auditable and independent of signal logic.
- **Signal Layer** is where alpha lives -- it evolves fastest and must be swappable.
- **Orchestration Layer** coordinates without interfering -- it translates signal outputs into trade proposals.
- **Approval Layer** is the human boundary -- it should be the ONLY place where a human can intervene.
- **Presentation Layer** is pure display -- it never makes trading decisions.

---

## Component Boundaries

### Pollyedge Mapping

| Component | Layer | Current Implementation | Responsibility Boundary |
|-----------|-------|----------------------|------------------------|
| client/ | Presentation | React dashboard | Shows bot status, positions, trades. Does NOT make decisions. |
| api/server.py | Presentation + Orchestration | Express server | Polls bot state from files, serves to dashboard. |
| approval_gate.py | Approval Gate | Telegram inline buttons | ONLY component that blocks trades waiting for human input. |
| orchestrator.py | Orchestration | Python main loop | Scores signals, deduplicates, routes to approval. |
| bot/agents/ (5 agents) | Signal Engine | ThreadPool agents | Each agent scans one signal type. Output is raw signals. |
| risk_manager.py | Risk Management | Policy engine | Enforces ALL safety rules. Called before every trade. |
| pollyedge_bot.py | Execution + Orchestration | Entry point | Initializes client, starts orchestrator. |
| signal_engine.py | Signal Engine | (exists but unused?) | May be legacy or strategy scoring. |

### What Should NOT Talk to What

These boundaries must be enforced:

1. **Agents must NOT call RiskManager directly.** They emit signals only. The orchestrator applies risk rules.
2. **Dashboard must NOT push commands to agents.** It writes to bot_state.json. The bot reads it.
3. **RiskManager must NOT know about Telegram.** It returns (allowed, reason) tuples. The orchestrator decides what to do with rejection.
4. **ApprovalGate must NOT execute trades.** It returns True/False. The orchestrator calls _execute().
5. **Signal Engine must NOT know about execution details.** It outputs token_id, side, edge, source only.

### Boundary Violation Warning

The current approval_gate.py sends notifications internally (notify()) -- this is a minor boundary blur. Acceptable for v1 but flag for extraction later.

---

## Data Flow

### Primary Flow: Signal-to-Trade

1. **Market APIs / Data Sources** -- agents pull raw data
2. **Signal Engine: 5 parallel agents** -- each emits: token_id, label, side, edge, source, market_prob, model_prob, volume
3. **Orchestrator: queue.Queue** -- deduplication (seen_tokens), scoring (0-100), min-score filter
4. **Risk Manager: can_trade()** -- returns (allowed, reason). Blocks: max positions, daily loss, low balance.
5. **Approval Gate: request_approval()** -- Telegram message with APPROVE/REJECT. Blocks up to 120s.
6. **Execution: py_clob_client** -- MarketOrder -> FOK order type. Records position in bot_state.json.
7. **Notifier: notify()** -- sends Telegram/Discord alerts on result.
8. **Dashboard polling loop** -- Express reads bot_state.json + trades.csv every 5s -> React dashboard.
9. **Presentation: React Dashboard** -- user sees everything, decides nothing on trading.

### State File Responsibilities

| File | Written By | Read By | Purpose |
|------|-----------|---------|---------|
| bot_state.json | RiskManager, Orchestrator | API server, Dashboard | Bot active flag, P&L, open positions |
| agent_status.json | BaseAgent | API server, Dashboard | Per-agent health and signal counts |
| pending_approvals.json | Orchestrator | Dashboard | Current approval queue (v2 target) |
| logs/trades.csv | log_trade() | API server | Trade history |
| bot_state.json | Dashboard (via API toggle) | Bot polling | bot_active kill switch |

## Recommended Project Structure

Key additions recommended to current structure:

- **bot/scanners/** (new): Extract market data fetching -- polymarket_scanner.py, crypto_scanner.py, news_scanner.py. Agents focus on signal logic, scanners are independently testable and swappable.
- **bot/storage/** (new): Centralize file I/O -- state_store.py (bot_state.json), trade_store.py (trades.csv), agent_store.py (agent_status.json). Enables SQLite/Redis swap without touching business logic.
- **shared/signals.ts** (new): Shared signal contract between Python agents and TypeScript types. Prevents schema drift.

Existing structure is largely correct. No major restructuring needed for Phase 1.

---

## Architectural Patterns

### Pattern 1: Multi-Agent Signal Swarm

**What:** Multiple specialized agents run in parallel threads, each scanning one signal type. All output to a shared queue.

**Pollyedge use:** The orchestrator launches 5 agents in parallel. This is already implemented correctly.

**Trade-offs:**
- PRO: Each agent can fail silently without killing others. Agents can be added/removed without changing others.
- CON: Signal deduplication is needed (seen_tokens in orchestrator -- correct). No cross-agent signal correlation built in yet.

### Pattern 2: Human-in-the-Loop Approval Gate

**What:** System pauses before execution, presents a structured proposal to a human, and blocks until approval or timeout. Returns True/False -- the gate never executes trades.

**Pollyedge use:** approval_gate.py with Telegram inline keyboard buttons. Auto-rejects on timeout (120s default).

**Trade-offs:**
- PRO: Human catches bad signals before capital is at risk. Fail-safe by default.
- CON: Cannot scale beyond human response time -- the 5 min/day UX promise requires approval queue to be browsable. Single point of latency.

**Critical:** Approval gate is non-blocking at the orchestrator level via ThreadPoolExecutor. Do NOT make approval synchronous in the main scan loop.

### Pattern 3: Policy-Centric Risk Management

**What:** All risk rules in a single component called before every trade. Returns (allowed, reason) tuples. Never calls execution or approval directly.

**Pollyedge use:** risk_manager.py -- max position size, daily loss cap, max open positions, minimum balance, minimum edge threshold.

**Trade-offs:**
- PRO: Single audit point for all safety rules. Rules can be changed without touching execution or signal logic.
- CON: Must not become a second orchestrator (keep logic pure: check + return).

### Pattern 4: Event-Driven Orchestration with State Files

**What:** Python bot and Node.js server communicate via shared JSON files. Server polls these files on an interval.

**Pollyedge use:** Dashboard polls GET /api/bot/status every 5 seconds. Already in place.

**Trade-offs:**
- PRO: Zero infrastructure -- works on day one. Easy to debug. Natural audit log.
- CON: File I/O slower than in-memory or pub/sub (acceptable for v1 given 5s polling interval). No browser push without WebSockets.

**Migration path:** Replace file polling with WebSocket server (Socket.IO or SSE) and Redis pub/sub. v2+ concern.

### Pattern 5: Score-Based Conviction Filter

**What:** Orchestrator assigns a numeric score (0-100) to each signal. Only signals above a threshold (currently 50) reach the approval gate.

**Pollyedge use:** orchestrator._score_signal() -- combines edge (up to 40 pts), source reliability (10-25 pts), volume (0-20 pts), confirmations (0-30 pts).

**Trade-offs:**
- PRO: Reduces approval fatigue. Scores are interpretable. Threshold is tunable.
- CON: Score weights are hard-coded -- needs A/B testing or backtesting. Score does not account for portfolio-level diversification.

### Pattern 6: Paper Trading Mode

**What:** Drop-in execution engine that simulates trades without hitting real APIs. All other components run normally.

**Pollyedge use:** Currently dry_run flag in pollyedge_bot.py only logs. PaperExecutionEngine NOT yet implemented.

**Recommendation:** Build a proper PaperExecutionEngine that simulates realistic fill prices (slippage, partial fills).

---

## Data Flow Details

### Signal Lifecycle

1. Agent.scan() -- returns list of signal dicts (token_id, label, side, edge, source, market_prob, model_prob, volume).
2. Agent.run() -- self.q.put(signal) for each signal.
3. Orchestrator._process_signals() loop:
   a. signal_q.get() -- blocks up to 1s
   b. Check seen_tokens dedup -- skip if duplicate
   c. Check pending_futures dedup -- skip if approval in flight
   d. RiskManager.can_trade() -- skip if blocked
   e. _score_signal() -- skip if score < 50
   f. executor.submit(_approve_and_execute, signal) -- non-blocking
4. _approve_and_execute() (in thread pool):
   a. RiskManager.position_size() -- determine trade size
   b. ApprovalGate.request_approval() -- block for up to 120s
   c. On approved: _execute() -- py_clob_client order
   d. On rejected/timeout: log + notify
   e. Add to seen_tokens on success
5. _execute():
   a. RiskManager.record_trade_open()
   b. log_trade() -- trades.csv
   c. MarketOrder -> FOK -> post_order
   d. notify() on result

### Dashboard Polling Loop

1. React (5s interval) -> GET /api/bot/status
2. Express reads: bot_state.json, agent_status.json, trades.csv, pending_approvals.json
3. Express merges into BotStatus response
4. React re-renders dashboard

Dashboard user actions: POST /api/bot/stop (bot_active=false), POST /api/bot/start (bot_active=true). Bot polls bot_state.json on next loop iteration.

---

## Scalability Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| 0-1 user (now) | Single bot process, file-based IPC, Express server, 5s polling. Monolith is fine. |
| 1-10 users | WebSocket push to dashboard (replace 5s polling). Shared state via Redis. |
| 10-100 users | Bot-as-a-service: separate bot processes per user. Approval queue becomes PostgreSQL table. |
| 100+ users | Agentic mesh: agents as independent services, centralized risk engine. |

### First Bottleneck: Approval Throughput

Roughly 30 trades/hour per approver (2 min/approval). Fine for 1 user. Fix: batch approval UI.

### Second Bottleneck: State File Contention

Concurrent readers (Express) and writers (Python bot). File locking on Python side (_file_lock) but not Express side. Fix: add file locking on Express, or migrate to Redis.

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Agents Calling RiskManager Directly

Agents should emit signals only. The orchestrator applies RiskManager. One place, one set of rules.

### Anti-Pattern 2: Approval Gate Executing Trades

Approval gate returns boolean only. Orchestrator calls _execute() on True.

### Anti-Pattern 3: Signal Logic in the Orchestrator

Orchestrator should coordinate, not calculate. Keep signal logic in agents or signal_engine.py.

### Anti-Pattern 4: Dashboard Making Trading Decisions

Dashboard should be display-only. Only dashboard-only action: bot on/off (kill switch).

### Anti-Pattern 5: Hardcoded Secrets and Magic Numbers

All config via environment variables (.env). RiskManager, approval timeout, and Telegram credentials all from env vars (already done correctly).

---

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|-------------------|-------|
| Polymarket CLOB | py_clob_client (Python SDK) | Primary execution venue. REST + WebSocket. |
| Polymarket Gamma API | REST polling (HTTP requests) | Market discovery, volume, liquidity. |
| Telegram Bot API | Polling via getUpdates | Approval gate sends messages, polls for callback answers. |
| News APIs | Agent-specific | NewsAgent fetches headlines, sentiment. |
| CoinGecko / Binance | REST polling | CryptoAgent for price data. No WebSocket streaming yet. |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|--------------|-------|
| Agents -> Orchestrator | queue.Queue | Thread-safe, decoupled. |
| Orchestrator -> RiskManager | Direct Python call | Synchronous check before any signal proceeds. |
| Orchestrator -> ApprovalGate | Direct Python call | Blocking (up to 120s) but runs in ThreadPoolExecutor. |
| Orchestrator -> Execution | Direct Python call | Only on approved signals. |
| Python Bot -> Express Server | File-based (JSON) | bot_state.json, agent_status.json. |
| Express Server -> React | REST polling (5s) | Replaceable with WebSocket later. |

---

## Build Order Implications

### Phase 1: Core Pipeline Stabilization (Already Built)
Ensure the existing 5 components (orchestrator, agents, risk, approval, notifier) are rock-solid. Key work: extract signal_engine.py, write integration tests, document signal schema in shared/signals.ts.

### Phase 2: Scanner Extraction
Extract market data fetching into bot/scanners/ module. Polymarket, crypto, and news scanners become independently testable and swappable.

### Phase 3: Storage Layer
Extract state persistence into bot/storage/ module. Reduces coupling, enables SQLite/Redis swap.

### Phase 4: Dashboard Enhancement
Approval queue UI, agent status cards, in-app approve/reject (not just Telegram). Browsable approval experience for the 5 min/day promise.

### Phase 5: Paper Trading Mode
Full paper trading with simulated fills (slippage modeling). Critical before risking capital.

### Phase 6: Real-Time Data (WebSocket)
Replace polling with WebSocket streaming. Reduces latency from 5s to sub-second.

### Phase 7: Multi-User / Portfolio Management
PostgreSQL for user + portfolio data. Shared signal pool, per-user approval queues, individual kill switches.

---

## Sources

- Algovantis: Signal-to-Execution Pipeline Architecture (2026-03-09)
  https://algovantis.com/algo-trading-signal-generation-to-execution-pipeline-architecture/
- AgentBets.ai: Polymarket Trading Bot Quickstart Guide (2026-02-28)
  https://agentbets.ai/guides/polymarket-bot-quickstart/
- Tuvoc: Trading System Architecture 2026 -- Agentic Mesh (2025-12-16)
  https://www.tuvoc.com/blog/trading-system-architecture-microservices-agentic-mesh/
- KX: Signal Architecture Playbook
  https://kx.com/resources/ebook/signal-architecture-playbook/
- Athenic Blog: Human-in-the-Loop Approval Workflows (2025-08-15)
  https://getathenic.com/blog/human-in-the-loop-approval-workflows
- Mastra: Where to Put Approval in Agents and Workflows (2026-02-04)
  https://mastra.ai/blog/hitl-where-to-put-approval-in-agents-and-workflows
- Cordum: Human-in-the-Loop AI Patterns (2026-01-13)
  https://cordum.io/blog/human-in-the-loop-ai-patterns
- Nic Chin: AI NeuroSignal -- 20-Agent Ensemble Trading System (2026-02-27)
  https://nicchin.com/case-studies/trading-ai
- Dev Genius: Two-Layer AI System for Polymarket + Kalshi (2026-03-03)
  https://blog.devgenius.io/just-built-a-two-layer-ai-system-that-trades-polymarket-and-kalshi-while-i-sleep-heres-the-aa59ead275f6
- aulekator/Polymarket-BTC-15-Minute-Trading-Bot (MIT, 2026-02-15)
  https://github.com/aulekator/Polymarket-BTC-15-Minute-Trading-Bot
- Microsoft Agent Framework: Tool Approval and HITL (2026-03-11)
  https://www.devleader.ca/2026/03/11/tool-approval-and-humanintheloop-in-microsoft-agent-framework
- Harness Engineering: Human-in-the-Loop Agent Patterns (2026-03-06)
  https://harnessengineering.academy/blog/human-in-the-loop-agent-patterns-when-agents-should-ask-for-help/

---
*Architecture research for: Pollyedge -- High-Conviction Trading Command Center*
*Researched: 2026-03-19*
