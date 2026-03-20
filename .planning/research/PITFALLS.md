# Pitfalls Research

**Domain:** High-Conviction Trading Command Center (Signal Research + Human Approval System)
**Researched:** March 19, 2026
**Confidence:** MEDIUM-HIGH

## Critical Pitfalls

### Pitfall 1: Backtest Overfitting (Curve Fitting)

**What goes wrong:**
Strategies appear highly profitable on historical data but fail catastrophically in live trading. The backtest shows 40%+ returns with low drawdown, but real-money execution loses 30%+ within months.

**Why it happens:**
Developers optimize strategy parameters (indicators, thresholds, timeframes) to maximize performance on historical data. With enough parameters and enough iterations, you can always find a configuration that "works" on past data - but it captures noise, not signal. Research shows 90% of profitable backtests are statistically invalid.

**How to avoid:**
- Limit strategy parameters to 3-5 maximum (every additional parameter dramatically increases overfit risk)
- Use walk-forward validation: optimize on data subset A, validate on data subset B
- Require out-of-sample Sharpe ratio above 1.0 before considering deployment
- Run Monte Carlo simulations on parameter combinations, not single best params
- Add transaction costs (slippage, spread, commission) to backtests - expect 30-50% performance degradation live

**Warning signs:**
- Backtest shows Sharpe ratio > 2.0 (likely overfitted)
- Strategy uses 10+ adjustable parameters
- Maximum drawdown < 5% (too smooth = curve fitting)
- No walk-forward validation performed
- Testing on single market/period only

**Phase to address:** Signal Engine Phase - backtest validation should happen before signals are ever presented for approval

---

### Pitfall 2: Signal Lag / Timing Decay

**What goes wrong:**
Signals are generated after the optimal entry point has passed. Research shows 74% of popular TradingView buy/sell indicators generate signals 2-8 candles after optimal entry on volatile crypto pairs.

**Why it happens:**
Single-dimension indicators (RSI oversold, support bounce, etc.) do not account for market context. By the time a signal fires, price has already moved. In fast-moving markets like crypto/Polymarket, this lag is fatal.

**How to avoid:**
- Test signal timing against live market data, not historical candles
- Combine multiple indicators for confirmation, but ensure they do not all lag
- Measure signal-to-action latency and penalize in scoring
- Prefer leading indicators (volume, order flow, price action) over lagging (moving averages, RSI)
- Build signals that anticipate, not follow - check if market structure supports the signal

**Warning signs:**
- Backtest entry points do not match live execution
- Signals fire after major moves already happened
- No latency measurement in signal pipeline
- Single-indicator signal generation

**Phase to address:** Signal Engine Phase - timing validation should be part of signal quality scoring

---

### Pitfall 3: Approval Workflow Review Fatigue

**What goes wrong:**
Human approvers receive too many signals, leading to decision fatigue. They either start auto-approving without review or abandon the system entirely. The "human-in-the-loop" becomes a bottleneck or is bypassed.

**Why it happens:**
Without strict filtering, the bot presents every possible setup. Users get 50+ approvals per day, making meaningful review impossible. Studies show approval fatigue is the #1 failure mode in enterprise HITL systems.

**How to avoid:**
- Present max 5-10 high-conviction signals per day, not 50
- Implement "confidence tiers": auto-execute low-risk, require approval for high-risk
- Add snooze/delay: signals expire after N hours to prevent backlog
- Surface only signals exceeding conviction threshold (e.g., 75%+ confidence)
- Show historical accuracy alongside each signal

**Warning signs:**
- Users approve >80% of signals without differentiation
- Approval queue grows >20 items unprocessed
- User feedback: "too many signals to review"
- No confidence scoring on presented signals

**Phase to address:** Approval Interface Phase - workflow design directly prevents this

---

### Pitfall 4: False Signal Flood (Noisy Signal Filtering)

**What goes wrong:**
The bot generates too many low-quality signals, leading to overtrading and account erosion. Research shows false signal rates can exceed 76% for certain indicator configurations, especially in sideways/volatile markets.

**Why it happens:**
Filtering logic is too permissive or does not account for market conditions. Every RSI oversold = signal, every support bounce = signal, without considering volume, liquidity, or regime.

**How to avoid:**
- Multi-factor filtering: require 2-3 independent signals to align before presenting
- Filter by market regime (trend vs. range) - some signals only work in specific regimes
- Add minimum conviction threshold before signal surfaces for approval
- Build in volume confirmation, liquidity checks for Polymarket
- Track signal quality over time and auto-adjust filtering

**Warning signs:**
- Win rate < 40% on approved signals
- Signal volume does not correlate with market opportunity
- No regime-aware filtering logic
- Every indicator triggers independently

**Phase to address:** Signal Engine Phase - filtering should be the core competency of the bot

---

### Pitfall 5: Polymarket API Integration Complexity

**What goes wrong:**
Bot fails to fetch market data reliably due to rate limits, auth issues, or US/Global API confusion. Polymarket has tiered rate limits (15k/10s general, 9k/10s CLOB) and requires specific auth headers.

**Why it happens:**
Polymarket has dual APIs (US - CFTC regulated with Ed25519, Global - crypto-native with EIP-712). Rate limits vary by endpoint. Authentication requires proxy wallet architecture. Many developers use wrong API or exceed limits.

**How to avoid:**
- Implement proper rate limit handling with exponential backoff
- Use correct SDK for region: polymarket-us (US) vs py-clob-client (Global)
- Cache market data to reduce API calls
- Monitor X-RateLimit headers and adapt dynamically
- Handle auth header refresh to prevent 401 errors
- Build in graceful degradation when API unavailable

**Warning signs:**
- Frequent 429 errors in logs
- Auth failures after ~1 hour (token expiry)
- Using wrong API for region
- No caching layer for market data
- No retry logic with backoff

**Phase to address:** Integration Phase - Polymarket data pipeline must be robust before signals can be generated

---

### Pitfall 6: Look-Ahead Bias in Signal Generation

**What goes wrong:**
Backtests show profitability but live trading fails because the system inadvertently used "future" data to generate signals. Historical data includes information that was not available at signal time.

**Why it happens:**
Developers process historical data with complete knowledge of outcomes. Code accidentally uses later candles to confirm earlier signals. For example, "if price closed above X, buy" - but you only knew X after the candle closed.

**How to avoid:**
- Use point-in-time data, not adjusted close
- Encode signal generation as if running live: only use data available at signal time
- Run paper trading with fresh data before trusting backtests
- Add "execution delay" simulation to backtests (signal at candle N, entry at N+1)

**Warning signs:**
- Backtest results far exceed paper trading results
- Code uses future data in any form (even for feature engineering)
- No point-in-time data validation
- No paper trading phase before real money

**Phase to address:** Signal Engine Phase - backtest methodology must prevent look-ahead

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Skip walk-forward validation | Faster backtests | Overfit strategies fail live | Never - this is mandatory |
| Single market backtest only | Quick to run | Strategy fails in other markets | Only for initial prototyping |
| Ignore transaction costs | Cleaner equity curve | Live results 30-50% worse | Never |
| Hard-code API endpoints | Faster integration | Breaks on API changes | Never |
| No signal confidence scoring | Faster to ship | Approval fatigue, low quality | MVP only - must add in phase 2 |
| Cache market data indefinitely | Fewer API calls | Stale data, wrong signals | Only with TTL and refresh |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Polymarket | Using Global API for US users (or vice versa) | Detect user region, use correct SDK + auth |
| Polymarket | Not handling rate limits (429 errors) | Implement per-endpoint limits with backoff |
| Polymarket | Hardcoding endpoint URLs | Use SDK abstractions, they handle URL changes |
| Crypto exchanges | Ignoring order book depth | Filter signals by liquidity thresholds |
| News API | No caching, hitting limits | Cache headlines, batch fetch, respect limits |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Too many signals for approval | Users skip review | Conviction threshold filtering | At >20 signals/day |
| API rate limit exhaustion | Bot stops getting data | Aggressive caching, queue management | When monitoring many markets |
| Real-time signal calculation | High CPU, lagging UI | Pre-compute signals, async update | At >50 monitored markets |
| No position size validation | Unlimited risk | Max position limits, auto-scaling | When user forgets to set limits |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Storing API keys in plaintext | Funds stolen if DB compromised | Use encrypted secrets, env vars, key management |
| No trade confirmation before execution | Accidental large trades | Require human approval for all trades |
| Webhook lacks signature verification | Fake signals injected | Verify webhook signatures from Polymarket |
| No position limits | Catastrophic loss | Enforce per-trade and daily limits |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Signal shows no context | User cannot assess quality | Show confidence, signal history, market regime |
| Approval requires full scroll | Slower decisions | Summary view with expand for details |
| No way to feedback signal quality | Bot keeps suggesting bad signals | Add thumbs up/down on approvals |
| Signals expire silently | User misses opportunities | Clear expiration warnings, notifications |

## "Looks Done But Is not" Checklist

Things that appear complete but are missing critical pieces.

- [ ] **Backtest:** Contains look-ahead bias - verify with point-in-time data
- [ ] **Backtest:** Ignores transaction costs - add slippage/spread/fees
- [ ] **Signal Filtering:** Only checks single indicator - verify multi-factor
- [ ] **Approval Workflow:** No confidence scoring - add tier system
- [ ] **API Integration:** No rate limit handling - verify 429 handling
- [ ] **API Integration:** Hardcoded endpoints - verify SDK usage
- [ ] **Paper Trading:** Missing - backtest is not live, need live validation
- [ ] **Position Limits:** Not enforced - add hard caps

## Recovery Strategies

When pitfalls occur despite prevention, how to recover.

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Overfitted strategy fails | HIGH | Stop trading, re-validate with walk-forward, reduce parameters |
| Signal latency too high | MEDIUM | Switch to leading indicators, re-test on live data |
| Approval fatigue | LOW | Implement confidence tiers, reduce signal volume |
| API rate limit issues | LOW | Add caching, exponential backoff, use SDK properly |
| Look-ahead bias | HIGH | Rewrite backtest using point-in-time data only |

## Pitfall-to-Phase Mapping

How roadmap phases should address these pitfalls.

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Backtest Overfitting | Signal Engine | Walk-forward validation passes, out-of-sample Sharpe > 1.0 |
| Signal Lag | Signal Engine | Live timing test shows signal before entry window |
| Approval Fatigue | Approval Interface | Signal volume <= 10/day, user satisfaction high |
| False Signal Flood | Signal Engine | Win rate > 50% on approved signals |
| Polymarket API Issues | Integration Phase | 0 rate limit errors in 24h test |
| Look-Ahead Bias | Signal Engine | Paper trading matches backtest within 20% |

## Sources

- PickMyTrade Blog: "Deadly Backtest Errors and Curve Fitting Traps 2026" (HIGH confidence - 2026)
- Kalena Research: "74% of TradingView buy/sell indicators lag 2-8 candles" (MEDIUM - 2026)
- BullByte Medium: "Why 90%% of trading signals fail before you enter" (MEDIUM - 2026)
- Quantified Strategies: "False signal rates up to 76%% for MA strategies" (HIGH - 2025)
- LuxAlgo: "Lessons from Algo Trading Failures" (Knight Capital case study) (HIGH - 2025)
- Athenic Blog: "Human-in-the-Loop Approval Workflows" (HIGH - 2025)
- Medium (Ravi Palwe): "Review Fatigue Breaking HITL AI" (MEDIUM - 2026)
- AgentBets.ai: Polymarket API troubleshooting and rate limit guides (HIGH - 2026)
- AgentBets.ai: "Polymarket US vs Global API" (HIGH - 2026)

---
*Pitfalls research for: Pollyedge - High-Conviction Trading Command Center*
*Researched: March 19, 2026*
