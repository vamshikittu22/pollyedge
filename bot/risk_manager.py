"""
PollyEdge Risk Manager — ALL safety rules in one place.
These run before EVERY single trade — no exceptions.
"""
import json
import os
from datetime import date
from dotenv import load_dotenv

load_dotenv()

MAX_TRADE_PCT  = float(os.getenv("MAX_TRADE_PCT", 0.03))   # 3% per trade
DAILY_LOSS_CAP = float(os.getenv("DAILY_LOSS_CAP", 0.10))  # Stop if -10% today
MAX_POSITIONS  = int(os.getenv("MAX_POSITIONS", 3))         # Max 3 open at once
MIN_EDGE       = float(os.getenv("MIN_EDGE", 0.08))         # Need 8%+ edge to enter
MIN_TRADE_USD  = 1.0                                         # Never trade below $1
STATE_FILE     = "bot_state.json"


def load_state() -> dict:
    """Load bot state from disk, or create fresh state if not found."""
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        state = {
            "daily_pnl": 0.0,
            "daily_date": str(date.today()),
            "open_positions": {},
            "total_trades": 0,
            "all_time_pnl": 0.0,
            "bot_active": True
        }
        save_state(state)
        return state


def save_state(state: dict) -> None:
    """Persist bot state to disk."""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def reset_daily_if_needed(state: dict) -> dict:
    """Reset daily P&L counter at midnight."""
    today = str(date.today())
    if state["daily_date"] != today:
        state["daily_pnl"] = 0.0
        state["daily_date"] = today
        save_state(state)
    return state


class RiskManager:
    """
    Master safety gate. Every trade must pass through can_trade()
    before execution. No exceptions, no overrides.
    """

    def __init__(self, balance: float):
        self.balance = balance
        self.state = load_state()
        self.state = reset_daily_if_needed(self.state)

    def can_trade(self) -> tuple[bool, str]:
        """Master gate — returns (allowed, reason)."""

        # Rule 1: Bot manually stopped
        if not self.state["bot_active"]:
            return False, "Bot manually stopped via dashboard"

        # Rule 2: Daily loss cap
        if self.balance > 0:
            daily_loss_pct = abs(self.state["daily_pnl"]) / self.balance
            if self.state["daily_pnl"] < 0 and daily_loss_pct >= DAILY_LOSS_CAP:
                return False, (
                    f"Daily loss cap hit: ${self.state['daily_pnl']:.2f} "
                    f"({daily_loss_pct:.1%})"
                )

        # Rule 3: Max open positions
        if len(self.state["open_positions"]) >= MAX_POSITIONS:
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
        """Record a new open position."""
        self.state["open_positions"][token_id] = {
            "side": side,
            "size": size,
            "entry_price": price,
            "label": label,
        }
        self.state["total_trades"] += 1
        save_state(self.state)

    def record_trade_close(self, token_id: str, exit_price: float) -> float:
        """Close a position and calculate P&L."""
        pos = self.state["open_positions"].pop(token_id, None)
        if not pos:
            return 0.0

        if pos["side"] == "BUY":
            pnl = (
                (exit_price - pos["entry_price"])
                / pos["entry_price"]
                * pos["size"]
            )
        else:
            pnl = (
                (pos["entry_price"] - exit_price)
                / pos["entry_price"]
                * pos["size"]
            )

        self.state["daily_pnl"] += pnl
        self.state["all_time_pnl"] += pnl
        save_state(self.state)
        return pnl

    def kill_switch(self, reason: str = "Manual") -> str:
        """Emergency stop — immediately halt all trading."""
        self.state["bot_active"] = False
        save_state(self.state)
        return f"KILL SWITCH ACTIVATED: {reason}"
