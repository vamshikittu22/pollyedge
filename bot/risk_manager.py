"""
PollyEdge Risk Manager — ALL safety rules in one place.
These run before EVERY single trade — no exceptions.
"""

import os
from datetime import date
from dotenv import load_dotenv

load_dotenv()

from bot.db import (
    get_bot_state,
    set_bot_state,
    get_open_positions,
    add_position,
    remove_position,
    init_db,
)

MAX_TRADE_PCT = float(os.getenv("MAX_TRADE_PCT", 0.03))  # 3% per trade
DAILY_LOSS_CAP = float(os.getenv("DAILY_LOSS_CAP", 0.10))  # Stop if -10% today
MAX_POSITIONS = int(os.getenv("MAX_POSITIONS", 3))  # Max 3 open at once
MIN_EDGE = float(os.getenv("MIN_EDGE", 0.08))  # Need 8%+ edge to enter
MIN_TRADE_USD = 1.0  # Never trade below $1

# Initialise the database on module load (creates tables + seeds defaults)
init_db()


def reset_daily_if_needed() -> None:
    """Reset daily P&L counter at midnight (persisted to SQLite)."""
    today = str(date.today())
    state = get_bot_state()
    if state.get("daily_date") != today:
        set_bot_state("daily_date", today)
        set_bot_state("daily_pnl", 0.0)


class RiskManager:
    """
    Master safety gate. Every trade must pass through can_trade()
    before execution. No exceptions, no overrides.
    """

    def __init__(self, balance: float):
        self.balance = balance
        # Load state from SQLite
        self.state = get_bot_state()
        # Ensure daily reset check runs
        reset_daily_if_needed()
        # Refresh after potential reset
        self.state = get_bot_state()
        # Track open positions in memory (backed by DB)
        self._positions = get_open_positions()

    def can_trade(self) -> tuple[bool, str]:
        """Master gate — returns (allowed, reason)."""

        # Rule 1: Bot manually stopped
        if not self.state.get("bot_active", False):
            return False, "Bot manually stopped via dashboard"

        # Rule 2: Daily loss cap
        if self.balance > 0:
            daily_pnl = self.state.get("daily_pnl", 0.0)
            daily_loss_pct = abs(daily_pnl) / self.balance
            if daily_pnl < 0 and daily_loss_pct >= DAILY_LOSS_CAP:
                return False, (
                    f"Daily loss cap hit: ${daily_pnl:.2f} ({daily_loss_pct:.1%})"
                )

        # Rule 3: Max open positions
        if len(self._positions) >= MAX_POSITIONS:
            return False, f"Max positions reached ({MAX_POSITIONS})"

        # Rule 4: Balance too low ($1 minimum — supports $10 starting capital)
        if self.balance < 1:
            return False, f"Balance critically low: ${self.balance:.2f}"

        return True, "OK"

    def position_size(self) -> float:
        """Calculate safe trade size — never more than MAX_TRADE_PCT of balance."""
        size = self.balance * MAX_TRADE_PCT
        return max(round(size, 2), MIN_TRADE_USD)

    def validate_edge(
        self, model_prob: float, market_prob: float
    ) -> tuple[bool, float]:
        """Only trade if edge is big enough to matter."""
        edge = abs(model_prob - market_prob)
        if edge < MIN_EDGE:
            return False, edge
        return True, edge

    def record_trade_open(
        self,
        token_id: str,
        side: str,
        size: float,
        price: float,
        label: str,
    ) -> None:
        """Record a new open position in SQLite."""
        # Add to open_positions table
        add_position(token_id, side, size, price, label)
        # Increment total_trades counter
        total = self.state.get("total_trades", 0) + 1
        set_bot_state("total_trades", total)
        # Refresh in-memory state
        self.state = get_bot_state()
        self._positions = get_open_positions()

    def record_trade_close(self, token_id: str, exit_price: float) -> float:
        """Close a position and calculate P&L (persisted to SQLite)."""
        pos = remove_position(token_id)
        if not pos:
            return 0.0

        entry_price = pos["entry_price"]
        size = pos["size"]
        side = pos["side"]

        if side == "BUY":
            pnl = (exit_price - entry_price) / entry_price * size
        else:
            pnl = (entry_price - exit_price) / entry_price * size

        # Update daily and all-time P&L in DB
        daily_pnl = self.state.get("daily_pnl", 0.0) + pnl
        all_time_pnl = self.state.get("all_time_pnl", 0.0) + pnl
        set_bot_state("daily_pnl", daily_pnl)
        set_bot_state("all_time_pnl", all_time_pnl)
        # Refresh in-memory state
        self.state = get_bot_state()
        self._positions = get_open_positions()
        return pnl

    def kill_switch(self, reason: str = "Manual") -> str:
        """Emergency stop — immediately halt all trading."""
        set_bot_state("bot_active", False)
        self.state = get_bot_state()
        return f"KILL SWITCH ACTIVATED: {reason}"
