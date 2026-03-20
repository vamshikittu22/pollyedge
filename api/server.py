"""
PollyEdge FastAPI Backend — serves bot state to the dashboard.
Run: uvicorn api.server:app --port 8000
"""

import csv
import json
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI(title="PollyEdge API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def read_state() -> dict:
    """Read bot state from the shared JSON file."""
    try:
        with open("bot_state.json") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "daily_pnl": 0.0,
            "daily_date": "",
            "open_positions": {},
            "total_trades": 0,
            "all_time_pnl": 0.0,
            "bot_active": False,
        }


def read_trades() -> list:
    """Read last 50 trades from the CSV log."""
    try:
        with open("logs/trades.csv") as f:
            return list(csv.DictReader(f))[-50:]
    except FileNotFoundError:
        return []


@app.get("/api/bot/status")
def status():
    """Return full bot status for the dashboard."""
    state = read_state()
    trades = read_trades()
    starting_balance = float(os.getenv("STARTING_BALANCE", 10))
    return {
        "bot_active": state.get("bot_active", False),
        "daily_pnl": state.get("daily_pnl", 0),
        "all_time_pnl": state.get("all_time_pnl", 0),
        "balance": starting_balance + state.get("all_time_pnl", 0),
        "dry_run": os.getenv("DRY_RUN", "true").lower() == "true",
        "total_trades": state.get("total_trades", 0),
        "open_positions": state.get("open_positions", {}),
        "trades": trades,
        "rules": {
            "max_trade_pct": os.getenv("MAX_TRADE_PCT", "0.03"),
            "daily_loss_cap": os.getenv("DAILY_LOSS_CAP", "0.10"),
            "max_positions": os.getenv("MAX_POSITIONS", "3"),
            "min_edge": os.getenv("MIN_EDGE", "0.08"),
        },
    }


@app.post("/api/bot/toggle")
def toggle():
    """Toggle bot active/inactive state."""
    state = read_state()
    state["bot_active"] = not state.get("bot_active", True)
    with open("bot_state.json", "w") as f:
        json.dump(state, f, indent=2)
    return {"bot_active": state["bot_active"]}


RULES_FILE = "bot_rules.json"


def read_rules() -> dict:
    """Read saved rules from disk."""
    try:
        with open(RULES_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_rules(rules: dict) -> None:
    """Persist rules to disk."""
    with open(RULES_FILE, "w") as f:
        json.dump(rules, f, indent=2)


@app.post("/api/bot/rules")
def update_rules(rules: dict):
    """Update bot trading rules — persists to bot_rules.json."""
    existing = read_rules()
    existing.update(rules)
    save_rules(existing)
    return {"status": "ok", "rules": existing}
