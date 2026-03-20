"""
Human-in-the-loop approval gate.
Every signal gets sent to YOUR Telegram with APPROVE/REJECT buttons.
Bot waits up to 2 minutes for your response.
"""

import os, time, datetime, logging, requests
from dotenv import load_dotenv
from bot.db import (
    init_db,
    add_pending_approval,
    resolve_pending_approval,
)

load_dotenv()

# Initialize SQLite database on module load
init_db()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TIMEOUT = int(os.getenv("APPROVAL_TIMEOUT_SEC", 120))
REQUIRE = os.getenv("REQUIRE_APPROVAL", "true").lower() == "true"

log = logging.getLogger("ApprovalGate")


class ApprovalGate:
    def __init__(self):
        self._last_update_id = 0

    def request_approval(self, signal: dict, size: float) -> bool:
        """
        Send trade proposal to Telegram with inline APPROVE/REJECT buttons.
        Block until user responds or timeout.
        Returns True if approved, False if rejected/timeout.
        """
        if not REQUIRE:
            return True  # Auto-approve if disabled

        if not TOKEN or not CHAT_ID:
            log.warning("No Telegram config — auto-approving")
            return True

        label = signal["label"]
        side = signal["side"]
        edge = signal.get("edge", 0)
        model_p = signal.get("model_prob", 0)
        market_p = signal.get("market_prob", 0)
        source = signal.get("source", "unknown")
        score = signal.get("score", 0)
        msg_id_key = f"{signal['token_id'][:8]}_{int(time.time())}"

        msg = (
            f"🎯 *TRADE PROPOSAL*\n\n"
            f"📌 *Market:* {label}\n"
            f"📊 *Side:* {side}\n"
            f"💰 *Size:* ${size:.2f}\n"
            f"🔢 *Edge:* {edge:+.1%}  (model={model_p:.0%} vs market={market_p:.0%})\n"
            f"🤖 *Source:* {source.upper()} agent\n"
            f"⭐ *Score:* {score}/100\n\n"
            f"⏱ Auto-reject in {TIMEOUT}s"
        )

        try:
            resp = requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                json={
                    "chat_id": CHAT_ID,
                    "text": msg,
                    "parse_mode": "Markdown",
                    "reply_markup": {
                        "inline_keyboard": [
                            [
                                {
                                    "text": "✅ APPROVE",
                                    "callback_data": f"approve_{msg_id_key}",
                                },
                                {
                                    "text": "❌ REJECT",
                                    "callback_data": f"reject_{msg_id_key}",
                                },
                            ]
                        ]
                    },
                },
                timeout=10,
            ).json()

            message_id = resp.get("result", {}).get("message_id")
            if not message_id:
                log.error("Failed to send approval message")
                return False

            # Write pending approval to SQLite before poll loop
            entry = {
                "id": msg_id_key,
                "label": signal.get("label", "Unknown"),
                "side": signal.get("side", "unknown"),
                "size": size,
                "edge": signal.get("edge", 0),
                "source": signal.get("source", "unknown"),
                "score": signal.get("score", 0),
                "market_prob": signal.get("market_prob", 0),
                "model_prob": signal.get("model_prob", 0),
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "status": "pending",
            }
            add_pending_approval(entry)

            # Poll for callback answer
            start = time.time()
            while time.time() - start < TIMEOUT:
                decision = self._poll_callback(msg_id_key, message_id)
                if decision is not None:
                    resolve_pending_approval(
                        msg_id_key, "approved" if decision else "rejected"
                    )
                    return decision
                time.sleep(2)

            # Timeout — auto reject
            log.info(f"Approval timeout for {label}")
            self._edit_message(
                message_id, f"⏱ *TIMED OUT* — {label}\nAuto-rejected after {TIMEOUT}s"
            )
            resolve_pending_approval(msg_id_key, "expired")
            return False

        except Exception as e:
            log.error(f"Approval gate error: {e}")
            return False  # Fail safe: reject on error

    def _poll_callback(self, key: str, message_id: int):
        """Check Telegram for user's button click."""
        try:
            resp = requests.get(
                f"https://api.telegram.org/bot{TOKEN}/getUpdates",
                params={
                    "offset": self._last_update_id + 1,
                    "timeout": 1,
                    "allowed_updates": ["callback_query"],
                },
                timeout=5,
            ).json()

            for update in resp.get("result", []):
                self._last_update_id = max(
                    self._last_update_id, update.get("update_id", 0)
                )
                cb = update.get("callback_query", {})
                data = cb.get("data", "")

                if key in data:
                    # Answer the callback to remove "loading" spinner
                    requests.post(
                        f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery",
                        json={"callback_query_id": cb["id"]},
                        timeout=5,
                    )
                    approved = data.startswith("approve_")
                    status = "✅ APPROVED" if approved else "❌ REJECTED"
                    self._edit_message(message_id, f"{status} — {key[:8]}…")
                    return approved
        except Exception:
            pass
        return None

    def _edit_message(self, message_id: int, text: str):
        try:
            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/editMessageText",
                json={"chat_id": CHAT_ID, "message_id": message_id, "text": text},
                timeout=5,
            )
        except Exception:
            pass
