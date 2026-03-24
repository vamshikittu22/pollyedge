"""
PollyEdge Trade Logger — SQLite primary with CSV backup for trade history.
"""

import csv
import os
from datetime import datetime, timezone

from bot.db import log_trade_to_db


LOG_DIR = "logs"
TRADE_FILE = os.path.join(LOG_DIR, "trades.csv")
HEADERS = ["timestamp", "token_id", "label", "exit_price", "pnl"]


def ensure_log_dir() -> None:
    """Create log directory if it doesn't exist."""
    os.makedirs(LOG_DIR, exist_ok=True)


def ensure_csv_header() -> None:
    """Create CSV file with headers if it doesn't exist."""
    ensure_log_dir()
    if not os.path.exists(TRADE_FILE):
        with open(TRADE_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(HEADERS)


def log_trade(
    token_id: str,
    label: str,
    exit_price: float,
    pnl: float,
) -> None:
    """Log a completed trade to SQLite (primary) and CSV (backup)."""
    # Primary: SQLite database (for dashboard)
    log_trade_to_db(token_id, label, exit_price, pnl)

    # Backup: CSV file (for external analysis)
    ensure_csv_header()
    with open(TRADE_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                datetime.now(timezone.utc).isoformat(),
                token_id,
                label,
                f"{exit_price:.4f}",
                f"{pnl:.4f}",
            ]
        )
