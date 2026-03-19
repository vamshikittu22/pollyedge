#!/usr/bin/env python3
"""
PollyEdge MVP v1.0 — Main Bot Engine
Runs 24/7, scans every 30s, uses Daloopa signals + mean-reversion.
START WITH DRY_RUN=true FOR AT LEAST 7 DAYS.
"""
import logging
import os
import signal
import sys
import time
from collections import deque

import requests
from dotenv import load_dotenv

load_dotenv()

from bot.risk_manager import RiskManager, load_state, save_state
from bot.signal_engine import get_midpoint, scan_earnings_edges
from bot.notifier import notify
from bot.logger import log_trade

# ── CONFIG ──────────────────────────────────────────────
DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"
SCAN_INTERVAL = int(os.getenv("SCAN_INTERVAL", 30))
EDGE_THRESH = float(os.getenv("MIN_EDGE", 0.08))
PROFIT_TARGET = 0.04  # Exit when +4% gain
STOP_LOSS = 0.02      # Exit when -2% loss
CLOB_API = "https://clob.polymarket.com"
GAMMA_API = "https://gamma-api.polymarket.com"

# ── LOGGING ─────────────────────────────────────────────
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/pollyedge.log"),
    ],
)
log = logging.getLogger("PollyEdge")

# ── PRICE HISTORY for mean-reversion ────────────────────
price_history: dict[str, deque] = {}


# ── CLIENT INIT ──────────────────────────────────────────
def init_clob_client():
    """Initialize the Polymarket CLOB client (or None for dry run)."""
    if DRY_RUN:
        log.info("DRY RUN MODE — Zero real money at risk")
        return None
    try:
        from py_clob_client.client import ClobClient

        client = ClobClient(
            CLOB_API,
            key=os.getenv("PRIVATE_KEY"),
            chain_id=int(os.getenv("CHAIN_ID", 137)),
            signature_type=1,
            funder=os.getenv("FUNDER"),
        )
        client.set_api_creds(client.create_or_derive_api_creds())
        log.info("CLOB client authenticated")
        return client
    except Exception as e:
        log.error(f"CLOB client init failed: {e}")
        return None


# ── BALANCE ──────────────────────────────────────────────
def get_wallet_balance() -> float:
    """Get current wallet balance (simulated in dry run)."""
    if DRY_RUN:
        state = load_state()
        return float(os.getenv("STARTING_BALANCE", 500)) + state["all_time_pnl"]
    try:
        r = requests.get(f"{CLOB_API}/balance", timeout=5)
        return float(r.json().get("balance", 0))
    except Exception:
        return 0.0


# ── ENTRY / EXIT ─────────────────────────────────────────
def enter_trade(client, rm: RiskManager, token_id, side, price, label):
    """Attempt to enter a new trade position."""
    allowed, reason = rm.can_trade()
    if not allowed:
        log.info(f"Blocked: {reason}")
        return False

    size = rm.position_size()

    if DRY_RUN:
        log.info(f"[DRY] {side} {label} @ {price:.4f} | size=${size:.2f}")
        rm.record_trade_open(token_id, side, size, price, label)
        notify(f"[DRY] {side} {label} | ${size:.2f} @ {price:.4f}", "🧪")
        return True

    try:
        from py_clob_client.clob_types import MarketOrderArgs, OrderType

        order = client.create_market_order(
            MarketOrderArgs(token_id=token_id, amount=size)
        )
        resp = client.post_order(order, OrderType.FOK)
        if resp.get("status") == "matched":
            rm.record_trade_open(token_id, side, size, price, label)
            notify(f"ENTERED {side} {label} | ${size:.2f} @ {price:.4f}", "💰")
            log.info(f"ENTERED {side} {label} @ {price:.4f}")
            return True
        else:
            log.warning(f"Order not filled: {resp}")
            return False
    except Exception as e:
        log.error(f"Entry error: {e}")
        notify(f"Entry failed: {e}", "🚨")
        return False


def exit_trade(client, rm: RiskManager, token_id, exit_price):
    """Exit an open position and log the result."""
    state = load_state()
    pos = state.get("open_positions", {}).get(token_id, {})
    label = pos.get("label", token_id[:12])

    pnl = rm.record_trade_close(token_id, exit_price)
    state = load_state()

    emoji = "+" if pnl > 0 else "-"
    log.info(f"{emoji} EXIT {label} | P&L: ${pnl:+.2f}")
    notify(
        f"{'Win' if pnl > 0 else 'Loss'} EXIT {label} | "
        f"P&L=${pnl:+.2f} | Daily=${state['daily_pnl']:+.2f}"
    )
    log_trade(token_id, label, exit_price, pnl)

    if DRY_RUN:
        return
    try:
        from py_clob_client.clob_types import MarketOrderArgs, OrderType

        order = client.create_market_order(
            MarketOrderArgs(token_id=token_id, amount=0)
        )
        client.post_order(order, OrderType.FOK)
    except Exception as e:
        log.error(f"Exit order error: {e}")


# ── MAIN LOOP ─────────────────────────────────────────────
def main():
    """Main bot loop — scans every SCAN_INTERVAL seconds."""
    mode = "[DRY RUN]" if DRY_RUN else "[LIVE]"
    log.info(f"PollyEdge starting {mode}")
    notify(f"PollyEdge started — {'DRY RUN' if DRY_RUN else 'LIVE TRADING'}")

    client = init_clob_client()
    cycle = 0

    def graceful_exit(sig, frame):
        log.info("Shutting down gracefully...")
        notify("Bot shut down (manual stop)")
        if client:
            try:
                client.cancel_all()
            except Exception:
                pass
        sys.exit(0)

    signal.signal(signal.SIGINT, graceful_exit)
    signal.signal(signal.SIGTERM, graceful_exit)

    while True:
        try:
            cycle += 1
            balance = get_wallet_balance()
            rm = RiskManager(balance)
            state = load_state()

            log.info(
                f"-- Cycle #{cycle} | Balance: ${balance:.2f} | "
                f"Positions: {len(state['open_positions'])}/"
                f"{int(os.getenv('MAX_POSITIONS', 3))} "
                f"| Daily P&L: ${state['daily_pnl']:+.2f} --"
            )

            allowed, reason = rm.can_trade()
            if not allowed:
                log.warning(f"Trading halted: {reason}")
                if "cap hit" in reason:
                    notify(
                        "Daily loss cap hit — bot paused until tomorrow",
                        "🔴",
                    )
                time.sleep(SCAN_INTERVAL)
                continue

            # ── STRATEGY 1: Earnings Signal (Daloopa) ──────────
            if cycle % 6 == 0:  # Every 3 minutes (less frequent, bigger edge)
                log.info("Scanning earnings signals via Daloopa...")
                edges = scan_earnings_edges(min_edge=EDGE_THRESH)
                for e in edges[:3]:  # Top 3 edges only
                    if e["token_id"] not in state["open_positions"]:
                        log.info(
                            f"Edge: {e['ticker']} | "
                            f"model={e['model_prob']:.0%} "
                            f"market={e['market_prob']:.0%} | "
                            f"edge={e['edge']:+.2%}"
                        )
                        enter_trade(
                            client,
                            rm,
                            e["token_id"],
                            e["side"],
                            e["market_prob"],
                            f"EARN:{e['ticker']}",
                        )

            # ── STRATEGY 2: Mean-Reversion (every cycle) ───────
            try:
                r = requests.get(
                    f"{GAMMA_API}/markets",
                    params={"active": True, "tag": "crypto", "limit": 20},
                    timeout=10,
                )
                markets = r.json()
            except Exception:
                markets = []

            for mkt in markets:
                tokens = mkt.get("tokens", [])
                if not tokens:
                    continue
                tok = tokens[0].get("token_id")
                mid = get_midpoint(tok)
                if not mid:
                    continue

                if tok not in price_history:
                    price_history[tok] = deque(maxlen=10)
                price_history[tok].append(mid)

                if len(price_history[tok]) >= 5:
                    avg = sum(price_history[tok]) / len(price_history[tok])
                    dev = (mid - avg) / avg
                    threshold = float(os.getenv("EDGE_THRESHOLD", 0.03))
                    if abs(dev) > threshold:
                        side = "BUY" if dev < 0 else "SELL"
                        label = mkt.get("question", "")[:35]
                        if tok not in state["open_positions"]:
                            enter_trade(
                                client, rm, tok, side, mid, f"MR:{label}"
                            )

            # ── EXIT CHECK ──────────────────────────────────────
            state = load_state()
            for tid, pos in list(state["open_positions"].items()):
                curr = get_midpoint(tid)
                if not curr:
                    continue
                entry = pos["entry_price"]
                if pos["side"] == "BUY":
                    if (
                        curr >= entry * (1 + PROFIT_TARGET)
                        or curr <= entry * (1 - STOP_LOSS)
                    ):
                        exit_trade(client, rm, tid, curr)
                else:
                    if (
                        curr <= entry * (1 - PROFIT_TARGET)
                        or curr >= entry * (1 + STOP_LOSS)
                    ):
                        exit_trade(client, rm, tid, curr)

            time.sleep(SCAN_INTERVAL)

        except KeyboardInterrupt:
            graceful_exit(None, None)
        except Exception as e:
            log.error(f"Cycle error: {e}")
            notify(f"Cycle error: {e}", "🚨")
            time.sleep(10)


if __name__ == "__main__":
    main()
