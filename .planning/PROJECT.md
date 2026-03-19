# Pollyedge

## What This Is

A high-conviction trading command center. Bot researches opportunities across Polymarket, crypto, and stocks using multiple signals (trends, news, patterns), filters for only the best setups, and presents them for human approval before execution.

## Core Value

You spend 5 minutes a day approving trades the bot already vetted.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Research engine scans multiple markets and signals
- [ ] Conviction filter only surfaces high-confidence opportunities
- [ ] Web dashboard shows live opportunities with analysis
- [ ] One-click approve/reject for trades
- [ ] Trade history and performance tracking

### Out of Scope

- Telegram notifications — defer to v2 (website first)
- Autonomous execution — human approval always required
- Stocks integration — start with Polymarket and crypto only

## Context

Starting from scratch. No existing bot, no Telegram setup. Building the full pipeline: research → filter → dashboard → approval → execution.

## Constraints

- **Approval required**: No fully autonomous trades — human must approve every trade
- **High conviction only**: Bot filters aggressively, surfaces only the best setups
- **Start focused**: Polymarket and crypto first, stocks later

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Website before Telegram | Foundation first, notification layer later | — Pending |
| Polymarket + crypto first | Most data available, faster to validate thesis | — Pending |
| Approval-based workflow | User controls risk, bot does the work | — Pending |

---
*Last updated: 2026-03-19 after initialization*
