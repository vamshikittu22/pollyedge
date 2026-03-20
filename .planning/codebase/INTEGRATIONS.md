# External Integrations

**Analysis Date:** 2026-03-19

## APIs & External Services

**Prediction Markets:**
- Polymarket CLOB API
  - SDK: `py-clob-client` 0.24.0
  - Endpoint: `https://clob.polymarket.com`
  - Auth: `PRIVATE_KEY`, `FUNDER` env vars
  - Chain: Polygon (chain_id 137)

**Market Data:**
- Polymarket Gamma API
  - Endpoint: `https://gamma-api.polymarket.com`
  - Used by: MomentumAgent for market listings
- NewsAPI
  - Used by: NewsAgent for sentiment
  - Auth: `NEWSAPI_KEY` env var
- Alpha Vantage
  - Used by: EarningsAgent
  - Auth: `ALPHA_VANTAGE_KEY` env var
- CoinGecko API
  - Used by: CryptoAgent
  - Auth: `COINGECKO_API_KEY` env var
- Daloopa
  - Used by: EarningsAgent for fundamental data
  - Auth: `DALOOPA_API_KEY` env var

**Messaging:**
- Telegram Bot API
  - Used by: ApprovalGate for trade approval workflow
  - Auth: `TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID` env vars
  - Features: Send messages, inline keyboard buttons for approve/reject

## Data Storage

**Databases:**
- PostgreSQL
  - Connection: `DATABASE_URL` env var (implied by `pg` and `drizzle-orm`)
  - Client: `drizzle-orm` with `pg` driver
  - ORM: Drizzle ORM 0.39.3
  - Sessions: `connect-pg-simple` for Express sessions

**File Storage:**
- Local JSON files (bot state IPC)
  - `bot_state.json` - Bot active state, positions, P&L
  - `pending_approvals.json` - Pending trade approvals
  - `agent_status.json` - Agent run status
  - `bot_rules.json` - Trading rule configuration
- Local CSV files
  - `logs/trades.csv` - Trade history log
- Local logs
  - `logs/pollyedge.log` - Python bot logging

**Caching:**
- Memory store
  - Implementation: `memorystore` 1.6.7
  - Used for: Express session storage

## Authentication & Identity

**Auth Provider:**
- Custom session-based auth
  - Implementation: Passport.js with local strategy
  - Session: Express-session with PostgreSQL store

**Wallet:**
- Polygon wallet (MetaMask-derived)
  - Keys: `PRIVATE_KEY`, `FUNDER` env vars
  - Used for: Signing Polymarket trades

## Monitoring & Observability

**Error Tracking:**
- Not detected (no Sentry, LogRocket, etc.)

**Logs:**
- Python: `logging` module with file + console handlers
  - Location: `logs/pollyedge.log`
- Node.js: Console logging in `server/index.ts`
  - Format: Timestamp + source + message

## CI/CD & Deployment

**Hosting:**
- Not detected (no Docker, Vercel, Railway configs visible)

**CI Pipeline:**
- Not detected (no GitHub Actions, Travis, CircleCI configs)

## Environment Configuration

**Required env vars:**
- `PORT` - Server port (default: 5000)
- `NODE_ENV` - `development` or `production`
- `PRIVATE_KEY` - Wallet private key
- `FUNDER` - Polymarket proxy wallet
- `CHAIN_ID` - Polygon (137)
- `STARTING_BALANCE` - Initial capital
- `DRY_RUN` - Demo mode (`true`/`false`)
- `REQUIRE_APPROVAL` - Human approval required
- `APPROVAL_TIMEOUT_SEC` - Approval timeout (default: 120)
- `MAX_TRADE_PCT` - Position size limit
- `DAILY_LOSS_CAP` - Daily loss limit
- `MAX_POSITIONS` - Max open positions
- `MIN_EDGE` - Minimum edge threshold
- `TELEGRAM_TOKEN` - Telegram bot token
- `TELEGRAM_CHAT_ID` - Telegram chat ID
- `NEWSAPI_KEY` - News API key
- `ALPHA_VANTAGE_KEY` - Alpha Vantage key
- `COINGECKO_API_KEY` - CoinGecko key
- `DALOOPA_API_KEY` - Daloopa key

**Secrets location:**
- `.env` file (gitignored)
- `.env.example` for template (no real values)

## Webhooks & Callbacks

**Incoming:**
- Telegram callback queries
  - Handled by: `approval_gate.py` polling `getUpdates`
  - Pattern: Inline keyboard button clicks

**Outgoing:**
- Telegram sendMessage
  - Used for: Approval requests and trade notifications
- Polymarket CLOB API
  - Used for: Order submission

---

*Integration audit: 2026-03-19*
