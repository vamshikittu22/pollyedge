#!/usr/bin/env python3
"""
PollyEdge v2.0 — Swarm Bot Entry Point
Starts the 5-agent orchestrator with human approval gate.
"""

import os, sys, logging, signal, threading
from dotenv import load_dotenv

load_dotenv()

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("logs/pollyedge.log")],
)

from bot.orchestrator import Orchestrator
from bot.risk_manager import RiskManager
from bot.notifier import notify
from bot.position_monitor import monitor_positions

DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"
BALANCE = float(os.getenv("STARTING_BALANCE", 10))


def init_client():
    if DRY_RUN:
        return None
    from py_clob_client.client import ClobClient

    c = ClobClient(
        "https://clob.polymarket.com",
        key=os.getenv("PRIVATE_KEY"),
        chain_id=int(os.getenv("CHAIN_ID", 137)),
        signature_type=1,
        funder=os.getenv("FUNDER"),
    )
    c.set_api_creds(c.create_or_derive_api_creds())
    return c


if __name__ == "__main__":
    logging.getLogger("PollyEdge").info(
        f"PollyEdge v2.0 | Balance: ${BALANCE} | "
        f"{'DRY RUN' if DRY_RUN else 'LIVE TRADING'}"
    )
    notify(
        f"v2.0 Swarm started\n"
        f"Balance: ${BALANCE}\n"
        f"Mode: {'DRY RUN' if DRY_RUN else 'LIVE'}\n"
        f"Approval: REQUIRED",
        "🤖",
    )

    client = init_client()

    def handle_exit(sig, frame):
        notify("Bot stopped manually", "🔴")
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    # Start position monitor daemon thread
    monitor_thread = threading.Thread(
        target=monitor_positions, args=(DRY_RUN,), daemon=True, name="PositionMonitor"
    )
    monitor_thread.start()

    orchestrator = Orchestrator(client, BALANCE, DRY_RUN)
    orchestrator.start()
