"""
bot/db.py — SQLite database layer for PollyEdge bot.
Uses stdlib sqlite3, reads/writes data/pollyedge.db.
Thread-safe via threading.Lock.
"""

import json
import os
import sqlite3
import threading
from contextlib import contextmanager
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "pollyedge.db")

_db_lock = threading.Lock()


def _get_db_path() -> str:
    return os.path.abspath(DB_PATH)


@contextmanager
def _conn():
    """Thread-safe database connection context manager."""
    path = _get_db_path()
    Path("data").mkdir(exist_ok=True)
    with _db_lock:
        conn = sqlite3.connect(path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()


def init_db() -> None:
    """Create all tables if they do not exist, seed default bot_state."""
    with _conn() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS bot_state ("
            "key TEXT PRIMARY KEY,"
            "value TEXT NOT NULL)"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS open_positions ("
            "token_id TEXT PRIMARY KEY,"
            "side TEXT NOT NULL,"
            "size REAL NOT NULL,"
            "entry_price REAL NOT NULL,"
            "label TEXT NOT NULL,"
            "opened_at TEXT NOT NULL)"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS agent_status ("
            "name TEXT PRIMARY KEY,"
            "status TEXT NOT NULL,"
            "last_scan TEXT NOT NULL,"
            "signals_found INTEGER NOT NULL DEFAULT 0)"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS pending_approvals ("
            "id TEXT PRIMARY KEY,"
            "label TEXT NOT NULL,"
            "side TEXT NOT NULL,"
            "size REAL NOT NULL,"
            "edge REAL NOT NULL,"
            "source TEXT NOT NULL,"
            "score INTEGER NOT NULL,"
            "market_prob REAL NOT NULL,"
            "model_prob REAL NOT NULL,"
            "timestamp TEXT NOT NULL,"
            "status TEXT NOT NULL DEFAULT 'pending')"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS trades ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "token_id TEXT NOT NULL,"
            "label TEXT NOT NULL,"
            "exit_price REAL NOT NULL,"
            "pnl REAL NOT NULL,"
            "closed_at TEXT NOT NULL)"
        )
        conn.commit()

        # Seed default bot_state if empty
        cur = conn.execute("SELECT COUNT(*) AS cnt FROM bot_state")
        if cur.fetchone()["cnt"] == 0:
            defaults = {
                "daily_pnl": 0.0,
                "daily_date": str(date.today()),
                "total_trades": 0,
                "all_time_pnl": 0.0,
                "bot_active": True,
                "balance": 10.0,
            }
            for k, v in defaults.items():
                conn.execute(
                    "INSERT OR IGNORE INTO bot_state (key, value) VALUES (?, ?)",
                    (k, json.dumps(v)),
                )
            conn.commit()


# ----------------------------------------------------------------------
# Bot State — key/value store (values JSON-encoded for Python types)
# ----------------------------------------------------------------------


def get_bot_state() -> dict:
    """
    Return the full bot state as a dict with Python types.
    Keys: daily_pnl, daily_date, total_trades, all_time_pnl, bot_active, balance.
    """
    with _conn() as conn:
        rows = conn.execute("SELECT key, value FROM bot_state").fetchall()
        state = {}
        for row in rows:
            try:
                state[row["key"]] = json.loads(row["value"])
            except json.JSONDecodeError:
                state[row["key"]] = row["value"]
        return state


def set_bot_state(key: str, value) -> None:
    """Upsert a single key into bot_state (value is JSON-serialized)."""
    with _conn() as conn:
        conn.execute(
            "INSERT INTO bot_state (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, json.dumps(value)),
        )


def get_config() -> dict:
    """Alias for get_bot_state — returns all config/state rows."""
    return get_bot_state()


def set_config(key: str, value) -> None:
    """Alias for set_bot_state — stores a config key."""
    set_bot_state(key, value)


# ----------------------------------------------------------------------
# Open Positions
# ----------------------------------------------------------------------


def get_open_positions() -> dict[str, dict]:
    """
    Return open positions as a dict keyed by token_id.
    Each value: {token_id, side, size, entry_price, label, opened_at}
    """
    with _conn() as conn:
        rows = conn.execute("SELECT * FROM open_positions").fetchall()
        return {row["token_id"]: dict(row) for row in rows}


def add_position(
    token_id: str,
    side: str,
    size: float,
    entry_price: float,
    label: str,
) -> None:
    """Insert a new open position."""
    with _conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO open_positions "
            "(token_id, side, size, entry_price, label, opened_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (token_id, side, size, entry_price, label, datetime.now(timezone.utc).isoformat()),
        )


def remove_position(token_id: str) -> Optional[dict]:
    """
    Delete a position by token_id and return the deleted row (or None).
    """
    with _conn() as conn:
        row = conn.execute(
            "SELECT * FROM open_positions WHERE token_id = ?", (token_id,)
        ).fetchone()
        if row:
            conn.execute("DELETE FROM open_positions WHERE token_id = ?", (token_id,))
            return dict(row)
        return None


# ----------------------------------------------------------------------
# Pending Approvals
# ----------------------------------------------------------------------


def add_pending_approval(entry: dict) -> None:
    """Insert a new pending approval entry. Keeps only the last 20."""
    with _conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO pending_approvals "
            "(id, label, side, size, edge, source, score, market_prob, model_prob, timestamp, status) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                entry["id"],
                entry.get("label", "Unknown"),
                entry.get("side", "unknown"),
                float(entry.get("size", 0)),
                float(entry.get("edge", 0)),
                entry.get("source", "unknown"),
                int(entry.get("score", 0)),
                float(entry.get("market_prob", 0)),
                float(entry.get("model_prob", 0)),
                entry.get("timestamp", datetime.now(timezone.utc).isoformat()),
                entry.get("status", "pending"),
            ),
        )
        _prune_approvals(conn, keep=20)


def _prune_approvals(conn: sqlite3.Connection, keep: int = 20) -> None:
    """Delete oldest entries beyond the keep limit (runs within an existing transaction)."""
    cursor = conn.execute(
        "SELECT id FROM pending_approvals ORDER BY timestamp DESC LIMIT -1 OFFSET ?",
        (keep,),
    )
    old_ids = [row["id"] for row in cursor]
    if old_ids:
        placeholders = ",".join("?" * len(old_ids))
        conn.execute(f"DELETE FROM pending_approvals WHERE id IN ({placeholders})", old_ids)


def get_pending_approvals(status: Optional[str] = "pending") -> list[dict]:
    """Return pending approval entries. By default only status=pending, ordered newest first."""
    with _conn() as conn:
        if status:
            cursor = conn.execute(
                "SELECT * FROM pending_approvals WHERE status = ? ORDER BY timestamp DESC",
                (status,),
            )
        else:
            cursor = conn.execute("SELECT * FROM pending_approvals ORDER BY timestamp 
# ----------------------------------------------------------------------
# Agent Status
# ----------------------------------------------------------------------


def get_agent_status() -> list[dict]:
    """Return all agent statuses from the agent_status table, ordered by name."""
    with _conn() as conn:
        cursor = conn.execute(
            "SELECT name, status, last_scan, signals_found FROM agent_status ORDER BY name"
        )
        return [dict(row) for row in cursor]


def update_agent_status(name: str, status: str, signals_found: int) -> None:
    """Upsert an agent's runtime status into agent_status.

    Auto-generates last_scan timestamp from UTC now.

    Args:
        name:           Agent name (primary key)
        status:         Current status string (e.g. "running", "error", "stopped")
        signals_found:  Number of signals found in the last scan
    """
    now = datetime.now(timezone.utc).isoformat()
    with _conn() as conn:
        conn.execute(
            "INSERT INTO agent_status (name, status, last_scan, signals_found) "
            "VALUES (?, ?, ?, ?) "
            "ON CONFLICT(name) DO UPDATE SET "
            "status=excluded.status, last_scan=excluded.last_scan, "
            "signals_found=excluded.signals_found",
            (name, status, now, signals_found),
        )


# Backward-compatibility aliases
def upsert_agent_status(name: str, status: str, last_scan: str, signals_found: int) -> None:
    """Legacy alias for update_agent_status (preserves original signature)."""
    with _conn() as conn:
        conn.execute(
            "INSERT INTO agent_status (name, status, last_scan, signals_found) "
            "VALUES (?, ?, ?, ?) "
            "ON CONFLICT(name) DO UPDATE SET "
            "status=excluded.status, last_scan=excluded.last_scan, "
            "signals_found=excluded.signals_found",
            (name, status, last_scan, signals_found),
        )


def get_all_agent_status() -> list[dict]:
    """Alias for get_agent_status."""
    return get_agent_status()


# ----------------------------------------------------------------------
# Trades
# ----------------------------------------------------------------------


def log_trade(token_id: str, label: str, exit_price: float, pnl: float) -> None:
    """Insert a new closed trade."""
    with _conn() as conn:
        conn.execute(
            "INSERT INTO trades (token_id, label, exit_price, pnl, closed_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (token_id, label, exit_price, pnl, datetime.now(timezone.utc).isoformat()),
        )


def get_trades(limit: int = 50) -> list[dict]:
    """Return recent closed trades, newest first."""
    with _conn() as conn:
        cursor = conn.execute(
            "SELECT * FROM trades ORDER BY closed_at DESC LIMIT ?", (limit,)
        )
        return [dict(row) for row in cursor]
