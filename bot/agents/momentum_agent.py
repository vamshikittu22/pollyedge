"""
Momentum Agent — Tracks price movement on active Polymarket markets.
Uses a rolling window of midpoint prices to detect mean-reversion
opportunities where prices deviate significantly from their recent average.
"""
import os
import requests
import time
from collections import deque
from bot.agents.base_agent import BaseAgent

GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API  = "https://clob.polymarket.com"

EDGE_THRESHOLD = float(os.getenv("EDGE_THRESHOLD", 0.03))
WINDOW_SIZE    = 10  # Rolling price window


class MomentumAgent(BaseAgent):
    def __init__(self, q):
        super().__init__(q, "MomentumAgent", interval=30)
        self.price_history: dict[str, deque] = {}

    def scan(self) -> list[dict]:
        signals = []
        markets = self._get_active_markets()

        for mkt in markets:
            try:
                tokens = mkt.get("tokens", [])
                if not tokens:
                    continue

                tok = tokens[0].get("token_id")
                mid = self._get_mid(tok)
                if not mid or mid <= 0:
                    continue

                # Build rolling price history
                if tok not in self.price_history:
                    self.price_history[tok] = deque(maxlen=WINDOW_SIZE)
                self.price_history[tok].append(mid)

                # Need at least 5 data points
                if len(self.price_history[tok]) < 5:
                    continue

                avg = sum(self.price_history[tok]) / len(self.price_history[tok])
                dev = (mid - avg) / avg

                if abs(dev) > EDGE_THRESHOLD:
                    side = "BUY" if dev < 0 else "SELL"
                    label = mkt.get("question", "")[:50]
                    model_p = avg  # Expect reversion to mean
                    edge = abs(dev)

                    signals.append({
                        "token_id":    tok,
                        "side":        side,
                        "market_prob": mid,
                        "model_prob":  round(model_p, 4),
                        "edge":        round(edge, 4),
                        "label":       f"MR:{label}",
                        "source":      "momentum",
                        "deviation":   round(dev, 4),
                        "volume":      float(mkt.get("volume", 0) or 0),
                    })

                time.sleep(0.1)
            except Exception:
                continue

        return sorted(signals, key=lambda x: abs(x["edge"]), reverse=True)

    def _get_active_markets(self) -> list:
        try:
            r = requests.get(
                f"{GAMMA_API}/markets",
                params={"active": True, "limit": 50},
                timeout=10
            )
            return r.json()
        except Exception:
            return []

    def _get_mid(self, token_id: str) -> float:
        try:
            r = requests.get(
                f"{CLOB_API}/midpoint",
                params={"token_id": token_id},
                timeout=4
            )
            return float(r.json().get("mid", 0))
        except Exception:
            return 0.0
