# PollyEdge — Polymarket Trading Bot + Dashboard

A self-contained Polymarket trading system with a live web dashboard, automated Python bot, Daloopa signal engine, and wallet integration.

## Architecture

```
┌─────────────────────────────────────────────┐
│  1. DASHBOARD (Website)                     │
│     React + Express — live P&L, balance,    │
│     start/stop bot, trade history           │
├─────────────────────────────────────────────┤
│  2. BOT ENGINE (Brain)                      │
│     Python backend — scans Polymarket,      │
│     uses Daloopa signals, places trades     │
├─────────────────────────────────────────────┤
│  3. WALLET (Money)                          │
│     MetaMask + USDC on Polygon —            │
│     funds all trades automatically          │
└─────────────────────────────────────────────┘
```

## Quick Start

### 1. Install Dependencies

```bash
# Dashboard (Node.js)
npm install

# Bot (Python)
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Fill in your wallet private key, Daloopa API key, Telegram bot token
```

### 3. Wallet Approval (one-time)

```bash
python setup/approve_wallet.py
```

### 4. Run the Bot

```bash
# Start with DRY_RUN=true for at least 7 days
python -m bot.pollyedge_bot
```

### 5. Run the Dashboard

```bash
# Development
npm run dev

# Production
npm run build
NODE_ENV=production node dist/index.cjs
```

## Project Structure

```
pollyedge-dashboard/
├── bot/                     # Python trading bot
│   ├── pollyedge_bot.py     # Main bot loop
│   ├── signal_engine.py     # Daloopa earnings signal
│   ├── risk_manager.py      # All safety rules
│   ├── notifier.py          # Telegram alerts
│   └── logger.py            # CSV trade logging
├── api/
│   └── server.py            # FastAPI backend (standalone)
├── setup/
│   └── approve_wallet.py    # One-time wallet approval
├── client/                  # React dashboard frontend
│   └── src/
│       ├── pages/dashboard.tsx
│       └── components/
│           ├── BalanceCard.tsx
│           ├── BotStatusCard.tsx
│           ├── PnLChart.tsx
│           ├── TradesTable.tsx
│           ├── OpenPositions.tsx
│           └── RulesPanel.tsx
├── server/                  # Express backend for dashboard
│   ├── routes.ts
│   └── storage.ts
├── shared/
│   └── schema.ts            # Shared TypeScript types
├── .env.example
├── requirements.txt
└── README.md
```

## Safety Rules

All trades pass through the Risk Manager before execution:

| Rule             | Default | Description                        |
|------------------|---------|------------------------------------|
| Max per trade    | 3%      | Never risk more than 3% of balance |
| Daily loss cap   | 10%     | Stop trading if down 10% today     |
| Max positions    | 3       | Maximum 3 concurrent positions     |
| Min edge         | 8%      | Only trade if model edge > 8%      |
| Kill switch      | —       | Stop all trading instantly         |

## Trading Strategies

### 1. Earnings Signal (Daloopa)
- Pulls historical earnings beat rates from Daloopa API
- Compares beat probability vs. Polymarket crowd pricing
- Trades when model probability diverges from market by > 8%

### 2. Mean Reversion
- Tracks rolling 5-sample price history for crypto markets
- Enters when price deviates > 3% from moving average
- Exits at +4% profit target or -2% stop loss

## 7-Day Pre-Live Checklist

- [ ] Day 1: Setup everything, confirm Telegram alerts working
- [ ] Day 2: Watch trade log — are signals firing?
- [ ] Day 3: Review trades.csv — win rate > 50%?
- [ ] Day 4: Stress test — pull internet, confirm bot recovers
- [ ] Day 5: Test daily loss cap manually
- [ ] Day 6: Verify dashboard numbers updating correctly
- [ ] Day 7: If win rate >= 52% → flip `DRY_RUN=false` with $100 only

## Requirements

- Node.js 20+
- Python 3.11+
- MetaMask wallet with USDC on Polygon
- Daloopa API key
- Telegram bot token (optional, for alerts)

## Warning

Start with $100 only. Keep `DRY_RUN=true` for 7 full days without exception. Prediction markets carry real financial risk regardless of bot quality. Never store your private key anywhere except your local `.env` file.
