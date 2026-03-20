"""
SQLite database layer for the bot.
All bot data goes through here -- shared with TypeScript via the same .db file.
"""

import sqlite3, os, datetime, threading
from datetime import timezone as tz
from contextlib import contextmanager
from typing import Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "pollyedge.db")

_db_lock = threading.Lock()


def _get_db_path() -> str:
    return os.path.abspath(DB_PATH)


@contextmanager
def _conn():
    """Thread-safe database connection context manager."""
    path = _get_db_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with _db_lock:
        conn = sqlite3.connect(path, timeout=10)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()


def init_db():
    """Create all tables if they do not exist."""
    with _conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS bot_state (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS open_positions (
                token_id TEXT PRIMARY KEY,
                side TEXT NOT NULL,
                size REAL NOT NULL,
                entry_price REAL NOT NULL,
                label TEXT NOT NULL,
                opened_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS agent_status (
                name TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                last_scan TEXT NOT NULL,
                signals_found INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS pending_approvals (
                id TEXT PRIMARY KEY,
                label TEXT NOT NULL,
                side TEXT NOT NULL,
                size REAL NOT NULL,
                edge REAL NOT NULL,
                source TEXT NOT NULL,
                score INTEGER NOT NULL,
                market_prob REAL NOT NULL,
                model_prob REAL NOT NULL,
                timestamp TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending'
            );

            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token_id TEXT NOT NULL,
                label TEXT NOT NULL,
                exit_price REAL NOT NULL,
                pnl REAL NOT NULL,
                closed_at TEXT NOT NULL
            );
        """)


# -- Pending Approvals -------------------------------------------


def add_pending_approval(entry: dict) -> None:
    """Insert a new pending approval entry. Keeps only the last 20."""
    with _conn() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO pending_approvals
            (id, label, side, size, edge, source, score, market_prob, model_prob, timestamp, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                entry["id"],
                entry.get("label", "Unknown"),
                entry.get("side", "unknown"),
                entry.get("size", 0),
                entry.get("edge", 0),
                entry.get("source", "unknown"),
                int(entry.get("score", 0)),
                float(entry.get("market_prob", 0)),
                float(entry.get("model_prob", 0)),
                entry.get(
                    "timestamp",
                    datetime.datetime.now(datetime.timezone.utc).isoformat(),
                ),
                entry.get("status", "pending"),
            ),
        )
        _prune_approvals(conn, keep=20)


def _prune_approvals(conn: sqlite3.Connection, keep: int = 20) -> None:
    cursor = conn.execute(
        """
        SELECT id FROM pending_approvals
        ORDER BY timestamp DESC
        LIMIT -1 OFFSET ?
        """,
        (keep,),
    )
    old_ids = [row["id"] for row in cursor]
    if old_ids:
        placeholders = ",".join("?" * len(old_ids))
        conn.execute(
            f"DELETE FROM pending_approvals WHERE id IN ({placeholders})", old_ids
        )


def get_pending_approvals(status: Optional[str] = "pending") -> list[dict]:
    """Return pending approval entries. By default only status=pending, ordered newest first."""
    with _conn() as conn:
        if status:
            cursor = conn.execute(
                "SELECT * FROM pending_approvals WHERE status = ? ORDER BY timestamp DESC",
                (status,),
            )
        else:
            cursor = conn.execute(
                "SELECT * FROM pending_approvals ORDER BY timestamp DESC"
            )
        return [dict(row) for row in cursor]


def resolve_pending_approval(id: str, status: str) -> None:
    """Update the status of a pending approval entry."""
    with _conn() as conn:
        conn.execute(
            "UPDATE pending_approvals SET status = ? WHERE id = ?", (status, id)
        )


def delete_pending_approval(id: str) -> None:
    """Delete a specific pending approval entry."""
    with _conn() as conn:
        conn.execute("DELETE FROM pending_approvals WHERE id = ?", (id,))


# -- Bot State ----------------------------------------------------


def get_bot_state() -> dict:
    """Return the full bot state as a dict."""
    with _conn() as conn:
        rows = conn.execute("SELECT key, value FROM bot_state").fetchall()
        return {row["key"]: row["value"] for row in rows}


def set_bot_state(key: str, value: str) -> None:
    """Set a single bot state key."""
    with _conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO bot_state (key, value) VALUES (?, ?)", (key, value)
        )


# -- Agent Status -------------------------------------------------


def upsert_agent_status(
    name: str, status: str, last_scan: str, signals_found: int
) -> None:
    with _conn() as conn:
        conn.execute(
            """
            INSERT INTO agent_status (name, status, last_scan, signals_found)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                status = excluded.status,
                last_scan = excluded.last_scan,
                signals_found = excluded.signals_found
            """,
            (name, status, last_scan, signals_found),
        )


def get_all_agent_status() -> list[dict]:
    with _conn() as conn:
        cursor = conn.execute("SELECT * FROM agent_status ORDER BY name")
        return [dict(row) for row in cursor]


def get_agent_status() -> list[dict]:
    """Return all agent statuses from the agent_status table, ordered by name."""
    with _conn() as conn:
        cursor = conn.execute(
            "SELECT name, status, last_scan, signals_found FROM agent_status ORDER BY name"
        )
        return [dict(row) for row in cursor]


def update_agent_status(name: str, status: str, signals_found: int) -> None:
    """Upsert an agent's runtime status into agent_status.

    Auto-generates last_scan timestamp. This is the preferred function for
    base_agent.py to call — it matches the original method signature.

    Args:
        name:           Agent name (primary key)
        status:         Current status string (e.g. "running", "error", "stopped")
        signals_found:  Number of signals found in the last scan
    """
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with _conn() as conn:
        conn.execute(
            """
            INSERT INTO agent_status (name, status, last_scan, signals_found)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                status        = excluded.status,
                last_scan     = excluded.last_scan,
                signals_found = excluded.signals_found
            """,
            (name, status, now, signals_found),
        )


# -- Open Positions -----------------------------------------------


def upsert_position(
    token_id: str, side: str, size: float, entry_price: float, label: str
) -> None:
    with _conn() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO open_positions (token_id, side, size, entry_price, label, opened_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                token_id,
                side,
                size,
                entry_price,
                label,
                datetime.datetime.now(tz).isoformat(),
            ),
        )


def delete_position(token_id: str) -> None:
    with _conn() as conn:
        conn.execute("DELETE FROM open_positions WHERE token_id = ?", (token_id,))


def get_all_positions() -> list[dict]:
    with _conn() as conn:
        cursor = conn.execute("SELECT * FROM open_positions")
        return [dict(row) for row in cursor]


# -- Trades -------------------------------------------------------


def log_trade(token_id: str, label: str, exit_price: float, pnl: float) -> None:
    with _conn() as conn:
        conn.execute(
            """
            INSERT INTO trades (token_id, label, exit_price, pnl, closed_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (token_id, label, exit_price, pnl, datetime.datetime.now(tz).isoformat()),
        )


def get_trades(limit: int = 50) -> list[dict]:
    with _conn() as conn:
        cursor = conn.execute(
            "SELECT * FROM trades ORDER BY closed_at DESC LIMIT ?", (limit,)
        )
        return [dict(row) for row in cursor]
