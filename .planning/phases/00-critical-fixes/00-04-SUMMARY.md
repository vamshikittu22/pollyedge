---
phase: "00-critical-fixes"
plan: "04"
subsystem: "bot"
tags:
  - position-management
  - daemon-thread
  - pnl-tracking
  - telegram
  - risk-exit

dependency_graph:
  requires: ["orchestrator.py", "risk_manager.py", "logger.py", "notifier.py"]
  provides: ["position_monitor.py"]
  affects:
    - "bot/pollyedge_bot.py"
    - "bot/orchestrator.py"

tech_stack:
  added:
    - "threading.Thread (daemon)"
    - "requests (CLOB API calls)"
  patterns:
    - "Daemon thread for background monitoring"
    - "PnL calculation at exit vs entry"
    - "Environment-driven thresholds"

key_files:
  created:
    - path: "bot/position_monitor.py"
      lines: 167
      purpose: "Daemon thread monitoring open positions every 30s"
  modified:
    - path: "bot/pollyedge_bot.py"
      purpose: "Start position monitor thread at bot startup"
    - path: "bot/orchestrator.py"
      purpose: "Remove entry-time log_trade(0.0) call"

key_decisions:
  - "P&L calculated at close time using midpoint price from Polymarket CLOB"
  - "log_trade() removed from entry — now only called at close with real P&L"
  - "Position monitor runs as daemon=True so it exits with main process"
  - "PROFIT_TARGET=30%, STOP_LOSS=10% as env vars with defaults"

metrics:
  duration: "minutes"
  completed: "2026-03-20"
  tasks_completed: 3
  files_created: 1
  files_modified: 2
---

# Phase 00 Plan 04: Position Monitor Daemon + log_trade Timing Fix

## One-Liner

Position monitor daemon thread checks open positions every 30s, exits them at profit target (+30%) or stop loss (-10%), and logs actual P&L at close time instead of entry time.

## What Was Built

### `bot/position_monitor.py` (167 lines)
A daemon thread that:
1. Loads state from `bot_state.json` every 30 seconds
2. Fetches live midpoint prices from Polymarket CLOB API (`https://clob.polymarket.com/midpoint`)
3. Calculates P&L % for each open position:
   - **BUY**: `(exit - entry) / entry`
   - **SELL**: `(entry - exit) / entry`
4. Exits positions when:
   - `pnl_pct >= PROFIT_TARGET` (+30% by default) → "PROFIT TARGET"
   - `pnl_pct <= -STOP_LOSS` (-10% by default) → "STOP LOSS"
5. Calls `rm.record_trade_close(token_id, exit_price)` to update state
6. Calls `log_trade(token_id, label, exit_price, actual_pnl)` with **real P&L** (not 0.0)
7. Sends Telegram notification with emoji (💰 for profit, 🔴 for loss)

### `bot/pollyedge_bot.py` (wired)
- Added `threading` import + `from bot.position_monitor import monitor_positions`
- Starts monitor thread **after signal handlers**, before orchestrator:
  ```python
  monitor_thread = threading.Thread(
      target=monitor_positions, args=(DRY_RUN,), daemon=True, name="PositionMonitor"
  )
  monitor_thread.start()
  ```

### `bot/orchestrator.py` (fixed)
- Removed `log_trade(token, label, price, 0.0)` call from `_execute()` — was logging 0.0 P&L at entry
- Removed unused `from bot.logger import log_trade` import
- `log_trade()` is now only called by `position_monitor.py` at **close time** with actual P&L

## Task Summary

| # | Task | Status | Details |
|---|------|--------|---------|
| 1 | Create position_monitor.py | ✅ | 167 lines, all specs met |
| 2 | Wire into pollyedge_bot.py | ✅ | daemon thread starts at bot startup |
| 3 | Remove log_trade entry call | ✅ | orchestrator no longer calls log_trade with 0.0 |

## Success Criteria: All Met ✅

- [x] Position monitor daemon thread starts with the bot
- [x] Positions close when profit target (+30%) or stop loss (-10%) is hit
- [x] log_trade() logs actual P&L at close (not 0.0)
- [x] Telegram notification sent on close with P&L details
- [x] bot_state.json updated when positions close (via record_trade_close)

## Deviations from Plan

### Auto-fixed Issues

**None** — plan executed exactly as written.

### Implementation Notes

- Used `daemon=True` in both the `monitor_thread` in `pollyedge_bot.py` AND in the `monitor_positions()` function's internal thread loop — double safety that the monitor exits with the main process.
- The `position_monitor.py` imports `RiskManager` to call `record_trade_close()` which already handles P&L calculation and state persistence. The monitor passes the exit price; `record_trade_close()` does the P&L math.
- `_calc_pnl_pct()` is a helper function that calculates percentage P&L (used for threshold comparison) while `record_trade_close()` calculates dollar P&L for state updates.
- Telegram `notify()` is called with full context: label, reason (PROFIT TARGET / STOP LOSS), entry→exit prices, P&L %, and mode (DRY/LIVE).

## Verification

```bash
py -c "from bot.position_monitor import monitor_positions; print('OK')"
# → monitor_positions function exists

grep -n "monitor_thread" bot/pollyedge_bot.py
# → 68:    monitor_thread = threading.Thread(...)

grep -n "log_trade" bot/orchestrator.py
# → (no output — entry-time log_trade removed)

py -c "
from bot.position_monitor import monitor_positions, PROFIT_TARGET, STOP_LOSS
print(f'PROFIT_TARGET={PROFIT_TARGET}, STOP_LOSS={STOP_LOSS}')
# → PROFIT_TARGET=0.3, STOP_LOSS=0.1
"
```

## Commit

```
28e97f8 fix(00-04): add position monitor daemon + fix log_trade timing
```

## Self-Check: PASSED

- [x] `bot/position_monitor.py` exists — 167 lines
- [x] `monitor_positions()` function callable
- [x] `PROFIT_TARGET=0.3`, `STOP_LOSS=0.1` constants correct
- [x] `monitor_thread` wired in `pollyedge_bot.py` at line 68
- [x] `log_trade` removed from `orchestrator.py` (verified with grep)
- [x] Commit `28e97f8` exists in git history
