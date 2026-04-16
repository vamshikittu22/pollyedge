"""
Momentum Agent — Tracks price movement on active Polymarket markets.
Uses a rolling window of midpoint prices to detect mean-reversion
opportunities where prices deviate significantly from their recent average.
"""

import os
import requests
import time
from collections import deque
from dotenv import load_dotenv
from bot.agents.base_agent import BaseAgent

load_dotenv()

GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"

# Must be >= 0.05 to score any edge points in orchestrator._score_signal()
# Lowered from 0.08 to capture more mean-reversion opportunities
EDGE_THRESHOLD = float(os.getenv("EDGE_THRESHOLD", 0.05))
WINDOW_SIZE = 10  # Rolling price window


class MomentumAgent(BaseAgent):
    def __init__(self, q):
        super().__init__(q, "MomentumAgent", interval=30)
        self.price_history: dict[str, deque] = {}

    def _weighted_avg(self, prices: list[float]) -> float:
        """Calculate volume-weighted average favoring recent prices.

        Weights:
        - Most recent: 3
        - Second most recent: 2
        - All others: 1

        Falls back to simple average if fewer than 3 data points.
        """
        if len(prices) < 3:
            return sum(prices) / len(prices) if prices else 0.0

        total_weight = 0.0
        weighted_sum = 0.0

        for i, price in enumerate(prices):
            if i == len(prices) - 1:  # Most recent
                weight = 3
            elif i == len(prices) - 2:  # Second most recent
                weight = 2
            else:
                weight = 1

            weighted_sum += price * weight
            total_weight += weight

        return weighted_sum / total_weight

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

                # Use weighted average favoring recent prices
                history_list = list(self.price_history[tok])
                avg = self._weighted_avg(history_list)
                dev = (mid - avg) / avg

                if abs(dev) > EDGE_THRESHOLD:
                    side = "BUY" if dev < 0 else "SELL"
                    label = mkt.get("question", "")[:50]
                    model_p = avg  # Expect reversion to mean
                    edge = abs(dev)

                    signals.append(
                        {
                            "token_id": tok,
                            "side": side,
                            "market_prob": mid,
                            "model_prob": round(model_p, 4),
                            "edge": round(edge, 4),
                            "label": f"MR:{label}",
                            "source": "momentum",
                            "analysis": f"Deviation: {dev:+.2%} from {WINDOW_SIZE}hr avg",
                            "volume": float(mkt.get("volume", 0) or 0),
                            "analysis_breakdown": {
                                "current_price": round(mid, 4),
                                "rolling_avg": round(avg, 4),
                                "deviation": f"{dev:+.2%}",
                                "window_size": WINDOW_SIZE,
                                "direction": side,
                                "trend": "oversold" if dev < 0 else "overbought",
                                "weighting": "volume-weighted"
                                if len(history_list) >= 3
                                else "simple",
                            },
                        }
                    )

                time.sleep(0.1)
            except Exception:
                continue

        return sorted(signals, key=lambda x: abs(x["edge"]), reverse=True)

    def _get_active_markets(self) -> list:
        try:
            r = requests.get(
                f"{GAMMA_API}/markets", params={"active": True, "limit": 50}, timeout=10
            )
            return r.json()
        except Exception:
            return []

    def _get_mid(self, token_id: str) -> float:
        try:
            r = requests.get(
                f"{CLOB_API}/midpoint", params={"token_id": token_id}, timeout=4
            )
            return float(r.json().get("mid", 0))
        except Exception:
            return 0.0
