"""
Underpriced Agent — Scans all active markets for YES+NO < $0.97.
When the pair sum is well below $1.00, one or both sides are underpriced.
Note: This buys only the YES leg, so it's a directional bet on YES
resolving — NOT a risk-free arb (that would require buying both legs).
"""
import requests, time
from bot.agents.base_agent import BaseAgent

GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API  = "https://clob.polymarket.com"

class ArbAgent(BaseAgent):
    def __init__(self, q):
        super().__init__(q, "ArbAgent", interval=15)  # Fastest agent

    def scan(self) -> list[dict]:
        signals = []
        try:
            r = requests.get(f"{GAMMA_API}/markets",
                             params={"active": True, "limit": 100}, timeout=10)
            markets = r.json()
        except Exception:
            return []

        for mkt in markets:
            try:
                tokens = mkt.get("tokens", [])
                if len(tokens) < 2:
                    continue

                yes_tok = tokens[0].get("token_id")
                no_tok  = tokens[1].get("token_id")

                yes_mid = self._get_mid(yes_tok)
                no_mid  = self._get_mid(no_tok)

                if yes_mid <= 0 or no_mid <= 0:
                    continue

                pair_sum = yes_mid + no_mid
                if pair_sum < 0.97:
                    arb_edge = 1.0 - pair_sum
                    signals.append({
                        "token_id":    yes_tok,
                        "token_no":    no_tok,
                        "side":        "BUY",
                        "market_prob": yes_mid,
                        "model_prob":  1.0,
                        "edge":        round(arb_edge, 4),
                        "pair_sum":    pair_sum,
                        "label":       f"CHEAP: {mkt.get('question','')[:38]}",
                        "source":      "underpriced",
                        "volume":      float(mkt.get("volume", 0) or 0),
                    })
                time.sleep(0.2)

            except Exception:
                continue

        return sorted(signals, key=lambda x: x["edge"], reverse=True)

    def _get_mid(self, token_id: str) -> float:
        try:
            r = requests.get(f"{CLOB_API}/midpoint",
                             params={"token_id": token_id}, timeout=4)
            return float(r.json().get("mid", 0))
        except Exception:
            return 0.0
