# Feature Research

**Domain:** Trading Research + Approval Dashboard
**Researched:** 2026-03-19
**Confidence:** MEDIUM (WebSearch-heavy)

---

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = product feels broken or incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Real-time market data display | Traders need current prices, no one waits for delayed data | MEDIUM | Polymarket has public Gamma API; crypto exchanges have WebSocket APIs |
| Signal/opportunity list view | Core workflow: see what is worth considering | LOW | Grid or card layout showing opportunity name, direction, confidence score, asset, time |
| Approve/Reject action buttons | Without action buttons, there is no workflow | LOW | Clear green/red buttons. One click to decide |
| Trade execution after approval | If approved trades do not execute, the product is useless | MEDIUM | API integration with Polymarket CLOB API, exchange APIs |
| Portfolio/position overview | Users need to know current holdings before approving new trades | LOW | Simple table: asset, quantity, entry price, P&L |
| Basic P&L tracking | Did I make money? is the first question | MEDIUM | Unrealized + realized P&L. Aggregated and per-trade |
| Alert/notification system | Tell me when something needs my attention | MEDIUM | Web push, email, or in-app |
| Market search/filter | Users need to find specific markets quickly | LOW | Search by keyword, filter by asset class, status, date range |
| Price charts | Visual confirmation of trend/pattern | MEDIUM | TradingView embed or lightweight chart library |
| Risk metrics display | How much am I risking? | MEDIUM | Position size, stop loss, take profit, max drawdown, risk/reward ratio |
| Audit trail / action history | What did I approve yesterday? | MEDIUM | Log of all signals, approvals, rejections, executions with timestamps |

### Differentiators (Competitive Advantage)

Features that set the product apart. Not required, but valuable. These are where Pollyedge can compete.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Multi-signal research engine | Bot synthesizes trends, news sentiment, on-chain data, whale activity | HIGH | Core differentiator: multi-source scanning beats single-source alerts |
| Conviction scoring / quality filter | Only shows A+ setups. Bot filters, user sees only best | HIGH | Proprietary scoring: signal strength + trend alignment + historical win rate + volatility edge |
| Human-in-the-loop approval workflow | Compliance-friendly, emotionally sound. Users approve, not auto-execute | MEDIUM | 5 minutes a day UX. Frictionless approve/reject with reasoning |
| Whale tracking / smart money monitoring | Follow smart money signals. Polymarket whale trackers show profitable wallet activity | HIGH | On-chain analysis. Polymarket-specific: track top traders positions |
| News + social sentiment analysis | AI-analyzed news sentiment predicts moves before price action | MEDIUM | Aggregate from 180+ sources. NLP scoring. Valuable for Polymarket event outcomes |
| Market regime awareness | Bot adapts signals to market conditions | HIGH | Most bots fail when regime changes. Regime detection adds accuracy |
| Cross-market opportunity correlation | Related opportunities surfaced together | MEDIUM | Graph of market relationships |
| Transparent performance metrics | Win rate, expectancy, Sharpe ratio, drawdown | MEDIUM | Reproducible, auditable metrics |
| Polymarket-native integration | Deep Polymarket support (prediction markets, not just crypto) | MEDIUM | Binary outcomes, resolution tracking, market categories |
| Telegram bot for approvals | Approve trades from anywhere | MEDIUM | Fast approval from mobile. Critical for 5 minutes a day |

### Anti-Features (Commonly Requested, Often Problematic)

Features that seem good but create problems.

| Anti-Feature | Why Requested | Why Problematic | Alternative |
|--------------|---------------|-----------------|-------------|
| Fully autonomous execution | I want to set it and forget it | Loses human oversight, blows up in volatile markets | Keep human-in-the-loop. Approval step is a feature |
| Real-time everything | I want to see every tick | Creates cognitive overload, alert fatigue, analysis paralysis | Batch signals into daily digests |
| 100+ signals and indicators | More data = better decisions | Overfitting risk. 15+ parameters almost certainly fail live | Focus on 3-5 high-conviction signals |
| Automatic parameter optimization | The bot should learn and improve | Static perfection collapses when conditions change | Manual tuning with periodic review |
| Copy trading / mirror trading | Just copy the best trader | Moral hazard, regulatory issues, over-leveraged followers | Transparency into why signals generated |
| Backtest-forwarding | Our backtest showed 80% win rate | Overestimates 30-50%. Live = chaotic vs smooth backtests | Paper trading alongside signals |
| Too many asset classes too soon | Add forex, futures, options, stocks | Dilutes focus. Unique microstructure per class | Polymarket + crypto first |
| Complex risk management UI | Add Monte Carlo, Greeks, VaR models | Creates paralysis. Retail traders do not use these | Simple risk/reward display |

---

## Feature Dependencies

- Research Engine requires Market Data: Cannot scan without data. Gamma API is public. CLOB requires wallet auth.
- Conviction Scoring requires Signal Quality Database: Track every signal outcome for scoring.
- Approve/Reject requires Trade Execution API: Approved trades must execute via CLOB.
- P&L Tracking requires Position Database: Know current positions for P&L.
- Audit Trail requires All Systems: Log every action for transparency.

---

## MVP Definition

### Launch With (v1)

- Market data display (Polymarket Gamma API + crypto price feeds)
- Signal/opportunity list view
- Conviction scoring (HIGH/MED/LOW tier)
- Approve/Reject buttons
- Trade execution (Polymarket only)
- Basic P&L tracking
- Audit trail
- Web dashboard (single-page, mobile-friendly)

### Add After Validation (v1.x)

- Telegram bot for approvals
- Whale tracking integration
- News sentiment scoring
- Multi-exchange support (Binance, Coinbase)
- Alert/notification system

### Future Consideration (v2+)

- Market regime detection
- Cross-market correlation graph
- Automated parameter optimization
- Stocks integration
- Advanced risk models (Monte Carlo, VaR)
---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Market data display | HIGH | MEDIUM | P1 |
| Opportunity list view | HIGH | LOW | P1 |
| Conviction scoring | HIGH | HIGH | P1 |
| Approve/Reject workflow | HIGH | LOW | P1 |
| Trade execution (Polymarket) | HIGH | MEDIUM | P1 |
| Basic P&L tracking | MEDIUM | MEDIUM | P1 |
| Audit trail | MEDIUM | MEDIUM | P1 |
| Web dashboard | HIGH | MEDIUM | P1 |
| Telegram approvals | MEDIUM | MEDIUM | P2 |
| Whale tracking | MEDIUM | HIGH | P2 |
| News sentiment | MEDIUM | MEDIUM | P2 |
| Multi-exchange support | MEDIUM | HIGH | P2 |
| Alert/notification system | LOW | MEDIUM | P2 |
| Market regime detection | LOW | HIGH | P3 |
| Cross-market correlation | LOW | MEDIUM | P3 |
| Stocks integration | LOW | HIGH | P3 |
| Advanced risk models | LOW | HIGH | P3 |

Priority key: P1=Must have, P2=Should have, P3=Nice to have
---

## Competitor Feature Analysis

| Feature | PolyTrack | Coinrule | TradingView | Pollyedge |
|---------|-----------|----------|-------------|-----------|
| Polymarket focus | Yes | No | Partial | Core-first |
| Human approval workflow | No | No | No | Yes |
| Multi-signal scanning | Limited | No | No | Yes |
| Conviction scoring | No | No | No | Yes |
| P&L tracking | Limited | Yes | No | Yes |
| Audit trail | No | Limited | No | Yes |
| Whale tracking | Yes | No | No | Yes |

Key insight: No current competitor combines: (1) Polymarket focus, (2) human approval workflow, (3) multi-signal scanning with conviction scoring. This is Pollyedge whitespace.

---

## Sources

- Polymarket API Documentation (docs.polymarket.com)
- PolyTrack Blog - Polymarket whale tracking
- Volatility Box - Conviction scoring methodology
- 3Commas Blog - AI Trading Bot Risk Management
- Petr Vojacek - Trading Bot Overfitting
- Reddit r/Trading - Human approval workflow
- AxonFlow - Human-in-the-Loop AI Approval
- Coin Bureau - Crypto Bot Pitfalls
- SignalWhisper - Social Sentiment Trading
- SentiSignal - AI Market Sentiment
- VeritasChain - Algorithmic Trading Audit Trails

---

Feature research for: Trading Research + Approval Dashboard
Researched: 2026-03-19
Confidence: MEDIUM
