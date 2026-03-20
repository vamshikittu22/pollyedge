"""
PollyEdge Position Monitor — Daemon thread that watches open positions.
Checks every 30s and exits them when PROFIT_TARGET or STOP_LOSS is hit.
P&L is calculated and logged at close time (not entry time).
"""

import os
import time
import logging
import requests
import threading
from dotenv import load_dotenv

load_dotenv()  # MUST be first!

from bot.risk_manager import load_state, save_state, RiskManager
from bot.logger import log_trade
from bot.notifier import notify

log = logging.getLogger("PositionMonitor")

# Thresholds — percentage of entry price
PROFIT_TARGET = float(os.getenv("PROFIT_TARGET", 0.30))  # +30% exit
STOP_LOSS = float(os.getenv("STOP_LOSS", 0.10))  # -10% exit

# Polymarket CLOB API
CLOB_API = "https://clob.polymarket.com"

CHECK_INTERVAL = 30  # seconds between checks


def _get_live_balance() -> float:
    """Reload balance from bot_state.json on every call."""
    state = load_state()
    starting = float(os.getenv("STARTING_BALANCE", 10))
    return starting + state.get("all_time_pnl", 0.0)


def _fetch_midpoint(token_id: str) -> float | None:
    """Fetch current midpoint price for a token from Polymarket CLOB."""
    try:
        resp = requests.get(
            f"{CLOB_API}/midpoint",
            params={"token_id": token_id},
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            # Polymarket returns {"price": "0.xxxx"} or just the price
            price = data.get("price") or data
            if price is not None:
                return float(price)
    except Exception as e:
        log.warning(f"Failed to fetch midpoint for {token_id}: {e}")
    return None


def _calc_pnl_pct(side: str, entry_price: float, exit_price: float) -> float:
    """
    Calculate P&L percentage for a position.

    For BUY:  pnl_pct = (exit - entry) / entry
    For SELL: pnl_pct = (entry - exit) / entry
    """
    if entry_price <= 0:
        return 0.0
    if side == "BUY":
        return (exit_price - entry_price) / entry_price
    else:  # SELL
        return (entry_price - exit_price) / entry_price


def monitor_positions(dry_run: bool = True) -> None:
    """
    Infinite loop: check open positions every 30s.
    Exit them when PROFIT_TARGET or STOP_LOSS threshold is hit.

    P&L is calculated at close time and passed to log_trade().
    Telegram notification sent on every close.
    """
    log.info(
        f"PositionMonitor started | PROFIT_TARGET={PROFIT_TARGET:.0%} | "
        f"STOP_LOSS={STOP_LOSS:.0%} | dry_run={dry_run}"
    )

    while True:
        try:
            state = load_state()
            balance = _get_live_balance()
            open_positions = state.get("open_positions", {})

            if not open_positions:
                time.sleep(CHECK_INTERVAL)
                continue

            rm = RiskManager(balance)
            closed_any = False

            for token_id, pos in list(open_positions.items()):
                side = pos.get("side", "BUY")
                entry_price = pos.get("entry_price", 0.0)
                size = pos.get("size", 0.0)
                label = pos.get("label", token_id)

                if entry_price <= 0:
                    log.warning(
                        f"Skipping {token_id}: invalid entry_price={entry_price}"
                    )
                    continue

                # Fetch current market price
                exit_price = _fetch_midpoint(token_id)
                if exit_price is None:
                    log.debug(f"No price for {token_id}, skipping this cycle")
                    continue

                # Calculate P&L %
                pnl_pct = _calc_pnl_pct(side, entry_price, exit_price)
                pnl = pnl_pct * size

                log.debug(
                    f"{label} | entry={entry_price:.4f} | "
                    f"mid={exit_price:.4f} | pnl%={pnl_pct:.2%} | "
                    f"pnl=${pnl:.4f}"
                )

                # Check exit conditions
                close_reason = None
                if pnl_pct >= PROFIT_TARGET:
                    close_reason = "PROFIT TARGET"
                elif pnl_pct <= -STOP_LOSS:
                    close_reason = "STOP LOSS"

                if close_reason:
                    log.info(
                        f"EXIT [{close_reason}]: {label} | "
                        f"entry={entry_price:.4f} → {exit_price:.4f} | "
                        f"pnl%={pnl_pct:.2%} | pnl=${pnl:.4f}"
                    )

                    # Record close in state
                    rm.record_trade_close(token_id, exit_price)

                    # Log trade with ACTUAL P&L (not 0.0)
                    log_trade(token_id, label, exit_price, pnl)

                    # Telegram notification
                    emoji = "💰" if pnl >= 0 else "🔴"
                    reason_emoji = "🎯" if close_reason == "PROFIT TARGET" else "🛑"
                    notify(
                        f"{label}\n"
                        f"{reason_emoji} {close_reason}\n"
                        f"Entry: {entry_price:.4f} → Exit: {exit_price:.4f}\n"
                        f"P&L: {pnl_pct:.2%} (${pnl:.4f})\n"
                        f"{'[DRY RUN]' if dry_run else '[LIVE]'}",
                        emoji,
                    )

                    closed_any = True

            if closed_any:
                log.info(f"PositionMonitor cycle complete — positions updated")

        except Exception as e:
            log.error(f"PositionMonitor error: {e}")

        time.sleep(CHECK_INTERVAL)
