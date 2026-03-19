"""
PollyEdge Telegram Notifier — sends alerts on every trade.
Never crashes the bot over a notification failure.
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def notify(msg: str, emoji: str = "📊") -> None:
    """Send a Telegram alert. Fails silently — never crashes the bot."""
    if not TOKEN or not CHAT_ID:
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={
                "chat_id": CHAT_ID,
                "text": f"{emoji} PollyEdge: {msg}",
            },
            timeout=5,
        )
    except Exception:
        pass  # Never crash the bot over a notification failure
