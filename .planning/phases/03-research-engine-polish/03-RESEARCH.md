# Phase 3: Research Engine Polish - Research

**Researched:** 2026-04-16
**Domain:** Polymarket signal generation, confidence scoring, market discovery
**Confidence:** HIGH

## Summary

This phase focuses on improving the research engine to get all 5 agents working with better signal quality. Key findings:

1. **MomentumAgent** is already implemented with rolling window mean-reversion (10-point window, 8% threshold)
2. **Conviction scoring** needs multi-factor improvement:News + price action + sentiment all need to be weighted
3. **Polymarket Gamma API** provides rich market discovery with tags, events, sorting - already well-supported
4. **Analysis breakdown** needs structured format showing all inputs that contributed to the signal

**Primary recommendation:** Enhance `_score_signal()` to include multi-factor weighing and add structured analysis fields to all agent signals.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- MomentumAgent uses rolling window of 10 price points for mean-reversion
- Thread-safe seen_tokens with threading.Lock

### Claude's Discretion
- Conviction scoring algorithm improvements
- Polymarket market discovery with tags/categories
- Analysis breakdown structure

### Deferred Ideas (OUT OF SCOPE)
- None specified - full research scope allowed
</user_constraints>

## Standard Stack

### Core APIs
| API | Version | Purpose | Why Standard |
|-----|---------|---------|-------------|
| Gamma API | Current | Market discovery, metadata, tags | Official Polymarket API - no auth required |
| CLOB API | Current | Midpoint prices, orderbook | Official pricing endpoint |

### Data Sources
| Source | Purpose | Integration |
|--------|---------|-------------|
| Daloopa API | Earnings beat probability | Already integrated in EarningsAgent |
| NewsAPI | Breaking news sentiment | Already integrated in NewsAgent |
| Yahoo Finance | EPS surprise history | Fallback in EarningsAgent |
| Alpha Vantage | Earnings calendar | Fallback in EarningsAgent |

### Rate Limits (from official docs)
| Endpoint | Limit | Notes |
|-----------|-------|-------|
| Gamma /markets | 300/10s | Primary market discovery |
| Gamma /events | 500/10s | Event browsing |
| CLOB /midpoint | 4000/10s | Price queries |

## MomentumAgent Deep Dive

### Current Implementation Analysis
The MomentumAgent is already implemented in `bot/agents/momentum_agent.py`:

**Data Source:** CLOB `/midpoint` endpoint - gets real-time midpoint price
**Algorithm:** Rolling window mean-reversion
- Window size: 10 price points
- EDGE_THRESHOLD: 8% (configurable via `EDGE_THRESHOLD` env var)
- Minimum 5 data points before signaling
- Deviation calculation: `(mid - avg) / avg`

**Signal Output:**
```python
{
    "token_id": tok,
    "side": "BUY" if dev < 0 else "SELL",  # Mean reversion direction
    "market_prob": mid,
    "model_prob": avg,
    "edge": abs(dev),
    "label": f"MR:{question[:50]}",
    "source": "momentum",
    "analysis": f"Deviation: {dev:+.2%} from {WINDOW_SIZE}hr avg",
    "volume": volume
}
```

### Improvements to Consider
1. **Lower threshold:** 8% is conservative; 5% may catch more opportunities
2. **Shorter window:** 5-7 points for faster reaction to price moves
3. **Vol-weighted average:** Recent prices weighted higher than older ones
4. **Multi-timeframe:** Check 5-point, 10-point, 20-point windows simultaneously

**Confidence:** MEDIUM - Current implementation is functional but tuning is experimental

## Conviction Scoring Algorithm

### Current Implementation (`orchestrator._score_signal`)

Current scoring (0-100):

| Edge Range | Points | Rationale |
|-----------|--------|-----------|
| >= 20% | 40 | Strong edge |
| >= 15% | 30 | Good edge |
| >= 10% | 20 | Moderate edge |
| >= 8% | 10 | Minimum viable |

**Source bonuses:**
| Source | Points | Rationale |
|--------|--------|-----------|
| earnings | 25 | Daloopa fundamental data |
| news | 20 | Sentiment confirmation |
| momentum | 15 | Price action |
| crypto | 15 | Crypto signals |
| underpriced | 15 | Arb detection |

**Volume bonuses:**
| Volume | Points | Rationale |
|--------|--------|-----------|
| > $500K | 20 | High liquidity |
| > $100K | 10 | Decent liquidity |

### Recommended Improved Formula

**New multi-factor scoring (0-100):**

```
score = min(edge_score + source_score + confluence_score + volume_score, 100)
```

**1. Edge Score (0-40):**
| Edge | Points |
|------|--------|
| >= 25% | 40 |
| >= 18% | 30 |
| >= 12% | 20 |
| >= 8% | 10 |
| < 8% | 0 |

**2. Source Reliability Score (0-25):**
| Source | Points | Rationale |
|--------|--------|-----------|
| earnings | 25 | Multi-source validation (Daloopa + Yahoo + AV) |
| news+momentum | 20 | Confluence of sentiment + price action |
| news | 18 | News sentiment alone |
| momentum | 15 | Technical price action |
| crypto | 12 | Single source |
| arb | 10 | Price inefficiency |

**3. Confluence Score (0-15):** - NEW
| Factor | Points |
|--------|--------|
| Multiple agents agree | +15 per confirmation (max 15) |
| Has analyst breakdown | +5 |

**4. Volume Score (0-20):**
| Volume | Points |
|--------|--------|
| > $1M | 20 |
| > $500K | 15 |
| > $100K | 10 |
| < $100K | 0 |

### Implementation

```python
def _score_signal(self, signal: dict) -> int:
    """Improved multi-factor scoring 0-100."""
    score = 0
    edge = abs(signal.get("edge", 0))

    # 1. Edge score
    if edge >= 0.25:
        score += 40
    elif edge >= 0.18:
        score += 30
    elif edge >= 0.12:
        score += 20
    elif edge >= 0.08:
        score += 10

    # 2. Source reliability
    source_scores = {
        "earnings": 25,
        "news+momentum": 20,  # NEW: cross-agent
        "news": 18,
        "momentum": 15,
        "crypto": 12,
        "arb": 10,
    }
    score += source_scores.get(signal.get("source"), 10)

    # 3. Confluence (NEW)
    confirmations = signal.get("confirmations", 1)
    score += min((confirmations - 1) * 15, 15)
    if signal.get("analysis"):
        score += 5  # Has breakdown

    # 4. Volume
    vol = signal.get("volume", 0)
    if vol > 1_000_000:
        score += 20
    elif vol > 500_000:
        score += 15
    elif vol > 100_000:
        score += 10

    return min(score, 100)
```

**Confidence:** HIGH - Formula follows industry-standard multi-factor scoring

## Polymarket Market Discovery

### Current Implementation

Currently using Gamma `/markets` endpoint:
```python
requests.get(
    f"{GAMMA_API}/markets",
    params={"active": True, "limit": 50}
)
```

### Available Discovery Methods

**1. By Tag (earnings, politics, sports, crypto):**
```python
GET /markets?tag=earnings&active=true&limit=50
```

**2. By Event:**
```python
GET /events?active=true&closed=false&limit=20
```

**3. By Search:**
```python
GET /public-search?q=bitcoin&limit=10
```

**4. Sort Options:**
| Parameter | Values |
|-----------|--------|
| order | volume_24hr, volume, liquidity, start_date, end_date |

**5. Tags endpoint:**
```python
GET /tags  # Returns ranked categories
```

### Recommended Discovery Strategy

```python
def get_markets_for_agent(agent_type: str) -> list:
    """Get relevant markets based on agent type."""
    params = {"active": True, "closed": False, "limit": 50}

    if agent_type == "earnings":
        params["tag"] = "earnings"
    elif agent_type == "crypto":
        params["tag"] = "crypto"
    elif agent_type == "news":
        # News agent scans all active, filters by keyword overlap
        params["limit"] = 100
    elif agent_type == "momentum":
        # All active - momentum scans broadly
        params["limit"] = 50
    elif agent_type == "arb":
        params["tag"] = "crypto,politics"  # Look for inefficiencies

    r = requests.get(f"{GAMMA_API}/markets", params=params, timeout=10)
    return r.json()
```

### Polymarket API Rate Limits

| Endpoint | Limit | Burst |
|----------|-------|-------|
| General | 4000/10s | 5000 |
| /events | 500/10s | 600 |
| /markets | 300/10s | 400 |
| /search | 350/10s | 400 |

**Recommendation:** Cache market list for 30 seconds to avoid hitting limits

**Confidence:** HIGH - Gamma API is well-documented and stable

## Analysis Breakdown Structure

### Current Signal Fields

Each agent produces signals with varying fields:

**MomentumAgent:**
- token_id, side, market_prob, model_prob, edge, label, source, analysis, volume

**EarningsAgent:**
- token_id, ticker, side, market_prob, model_prob, edge, label, source, analysis, volume

**NewsAgent:**
- token_id, side, market_prob, model_prob, edge, label, source, analysis, volume

### Recommended Structured Analysis

All signals should include:

```python
{
    # Required fields
    "token_id": "...",
    "side": "BUY|SELL",
    "market_prob": 0.45,      # Current Polymarket price
    "model_prob": 0.65,       # Our estimated probability
    "edge": 0.20,             # model_prob - market_prob
    "label": "Will AAPL beat earnings?",
    "source": "earnings",       # Which agent

    # NEW: Confidence (0-100)
    "confidence": 75,

    # NEW: Structured analysis breakdown
    "analysis_breakdown": {
        "primary": "Daloopa shows 75% beat rate over 12 quarters",
        "secondary": [
            {"factor": "yahoo", "value": "0.71", "weight": 2},
            {"factor": "alpha_vantage", "value": "0.68", "weight": 1}
        ],
        "sentiment": "positive",        # For news signals
        "price_deviation": "+12%",      # For momentum signals
        "volume": 250000,
        "liquidity_rating": "medium"   # low/medium/high
    },

    # NEW: Timestamps
    "signal_time": "2026-04-16T10:30:00Z",
    "market_update_time": "2026-04-16T10:29:00Z",

    # Metadata
    "confirmations": 1,
    "volume": 250000,
}
```

### Analysis Breakdown by Agent

**EarningsAgent breakdown:**
```python
"analysis_breakdown": {
    "primary": "Beat {beats}/{total} quarters ({source})",
    "secondary": [
        {"source": "daloopa", "beat_rate": 0.75, "weight": 3, "quarters": 12},
        {"source": "yahoo", "beat_rate": 0.71, "weight": 2, "quarters": 7},
        {"source": "alpha_vantage", "beat_rate": 0.68, "weight": 1, "quarters": 4}
    ],
    "weighted_avg": 0.71,
    "consensus": "BEAT"
}
```

**NewsAgent breakdown:**
```python
"analysis_breakdown": {
    "headline": "Apple reports record iPhone sales",
    "sentiment": "positive",  # positive/negative/neutral
    "sentiment_words": ["record", "beats", "surpasses"],
    "market_overlap": 3,  # Word overlap with market question
    "estimated_impact": "+25% probability shift"
}
```

**MomentumAgent breakdown:**
```python
"analysis_breakdown": {
    "current_price": 0.42,
    "rolling_avg": 0.50,
    "deviation": "-16%",
    "window_size": 10,
    "direction": "BUY",  # Mean reversion direction
    "trend": "oversold"  # oversold/overbought
}
```

**Confidence:** HIGH - Structured format follows industry patterns

## Architecture Patterns

### Signal Flow

```
Agent.scan() → Signal Queue → Orchestrator._score_signal()
                                    ↓
                          Confidence scoring (0-100)
                                    ↓
                          Threshold check (>= 50)
                                    ↓
                    ThreadPoolExecutor → ApprovalGate → Execute
```

### Cross-Agent Confluence Detection

To detect when multiple agents agree on the same market:

```python
def _detect_confluence(self, signal: dict) -> dict:
    """Check if other agents agree on this market."""
    token_id = signal["token_id"]
    confirmations = 1

    # Check recent signals from other agents
    for other_signal in self._recent_signals:
        if other_signal["token_id"] == token_id:
            confirmations += 1

    signal["confirmations"] = confirmations
    return signal
```

### Error Handling

- All API calls have try/except with timeout
- Graceful degradation: if source fails, use fallback
- Rate limit handling: sleep(0.1) between calls

**Confidence:** HIGH - Patterns are proven in existing code

## Common Pitfalls

### Pitfall 1: Signals Too Weak
**What:** Many signals with edge < 8% getting filtered
**Why:** Low EDGE_THRESHOLD or no quality signals
**How to avoid:** Log scores, monitor threshold effectiveness

### Pitfall 2: API Rate Limits
**What:** 429 errors from Polymarket
**Why:** Too many requests
**How to avoid:** Cache market list, add delays between calls

### Pitfall 3: Duplicate Signals
**What:** Same market signaled by different agents
**Why:** No cross-agent deduplication
**How to avoid:** Use seen_tokens set with thread lock

### Pitfall 4: Stale Prices
**What:** Midpoint doesn't reflect current orderbook
**Why:** Cached or delayed prices
**How to avoid:** Fetch prices fresh, warn on staleness

### Pitfall 5: News False Positives
**What:** News matches market but unrelated
**Why:** Keyword overlap is shallow
**How to avoid:** Require higher word overlap (5+ words), verify causality

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Price fetching | Custom scraper | CLOB /midpoint | Official API, real-time |
| Market discovery | Web scraping | Gamma API | Official, rate-limited |
| Earnings data | Manual entry | Daloopa API | Accurate, auto-updated |
| News sentiment | Simple keyword count | NewsAPI + NLP | Structured, scalable |

## Code Examples

### Get Midpoint Price (verified from CLOB API)

```python
# Source: Polymarket CLOB API docs
import requests

def get_midpoint(token_id: str) -> float:
    try:
        r = requests.get(
            "https://clob.polymarket.com/midpoint",
            params={"token_id": token_id},
            timeout=5
        )
        return float(r.json().get("mid", 0))
    except Exception:
        return 0.0
```

### Discover Markets by Tag

```python
# Source: Polymarket Gamma API
import requests

def get_markets_by_tag(tag: str, limit: int = 50) -> list:
    r = requests.get(
        "https://gamma-api.polymarket.com/markets",
        params={
            "active": True,
            "closed": False,
            "tag": tag,
            "limit": limit
        },
        timeout=10
    )
    return [m for m in r.json() if m.get("tokens")]
```

### Multi-Factor Scoring (enhanced)

```python
def _score_signal(self, signal: dict) -> int:
    """Score 0-100 with multi-factor weighing."""
    score = 0
    edge = abs(signal.get("edge", 0))

    # Edge score (0-40)
    if edge >= 0.25: score += 40
    elif edge >= 0.18: score += 30
    elif edge >= 0.12: score += 20
    elif edge >= 0.08: score += 10

    # Source reliability (0-25)
    source_scores = {
        "earnings": 25,
        "news+momentum": 20,
        "news": 18,
        "momentum": 15,
        "crypto": 12,
        "arb": 10,
    }
    score += source_scores.get(signal.get("source"), 10)

    # Confluence (0-15)
    confirmations = signal.get("confirmations", 1)
    score += min((confirmations - 1) * 15, 15)
    if signal.get("analysis_breakdown"):
        score += 5

    # Volume (0-20)
    vol = signal.get("volume", 0)
    if vol > 1_000_000: score += 20
    elif vol > 500_000: score += 15
    elif vol > 100_000: score += 10

    return min(score, 100)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Single-source earnings | Multi-source weighted | Phase 1 | More accurate beat probability |
| Price-only momentum | Rolling window mean-reversion | Phase 0 | Captures reversions |
| Basic threshold | Multi-factor scoring | Phase 3 | Better signal quality |
| No confluence | Cross-agent detection | Phase 3 | Higher conviction |

**Deprecated/outdated:**
- Static edge thresholds (all agents same) → Dynamic per-agent scoring
- Single API source → Fallback chain (Daloopa → Yahoo → Alpha Vantage)

## Open Questions

1. **Should MomentumAgent use price history from CLOB API?**
   - What we know: Current rolling window is in-memory only
   - What's unclear: Would historical /prices-history add value?
   - Recommendation: Keep in-memory for now, evaluate after Phase 3

2. **How to weight news + momentum confluence?**
   - What we know: Both can signal same market
   - What's unclear: 50/50 weight vs weighted average
   - Recommendation: Use 60/40 (news/momentum) but require both sources

3. **What's the optimal confidence threshold?**
   - What we know: Current is 50 (half of max score)
   - What's unclear: Should be 60 or 70?
   - Recommendation: Start at 50, adjust based on signal volume

## Sources

### Primary (HIGH confidence)
- Polymarket Gamma API docs (pm.wiki) - endpoints, rate limits
- Polymarket CLOB API docs (docs.polymarket.com) - pricing endpoints
- Official Polymarket API Guide 2026 - market discovery

### Secondary (MEDIUM confidence)
- WebSearch: trading signal confidence scoring - multi-factor formulas
- WebSearch: Polymarket market discovery API - current practices
- Industry patterns: Numerai Alpha, Thrive confidence scoring

### Tertiary (LOW confidence)
- Community discussions on Polymarket Discord - rate limit updates

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Official APIs well-documented
- Architecture: HIGH - Proven patterns from existing codebase
- Pitfalls: HIGH - Identified from Phase 0-2 learnings
- Scoring algorithm: MEDIUM - Industry-informed but needs validation
- Market discovery: HIGH - Gamma API is stable

**Research date:** 2026-04-16
**Valid until:** 90 days (Polymarket APIs are stable)