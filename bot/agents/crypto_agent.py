"""
Crypto Agent — Uses CoinGecko to find BTC/ETH/SOL momentum signals,
cross-references with Polymarket crypto binary markets.
Needs zero API key for basic use.
"""
import requests
from bot.agents.base_agent import BaseAgent

COINGECKO = "https://api.coingecko.com/api/v3"
GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API  = "https://clob.polymarket.com"

CRYPTO_MAP = {
    "bitcoin": ["BTC", "bitcoin"],
    "ethereum": ["ETH", "ethereum"],
    "solana": ["SOL", "solana"],
}

class CryptoAgent(BaseAgent):
    def __init__(self, q):
        super().__init__(q, "CryptoAgent", interval=60)

    def scan(self) -> list[dict]:
        signals = []
        try:
            # Get 24h price changes for major cryptos
            resp = requests.get(
                f"{COINGECKO}/simple/price",
                params={"ids": "bitcoin,ethereum,solana",
                        "vs_currencies": "usd",
                        "include_24hr_change": "true"},
                timeout=10
            )
            prices = resp.json()
        except Exception:
            return []

        poly_markets = self._get_crypto_markets()

        for coin_id, coin_data in prices.items():
            change_24h = coin_data.get("usd_24h_change", 0)
            keywords   = CRYPTO_MAP.get(coin_id, [])

            # Strong momentum: >3% move in 24h
            if abs(change_24h) < 3.0:
                continue

            bullish = change_24h > 0

            for mkt in poly_markets:
                question = mkt.get("question", "").lower()
                if not any(kw.lower() in question for kw in keywords):
                    continue

                tokens  = mkt.get("tokens", [])
                yes_tok = tokens[0].get("token_id") if tokens else None
                if not yes_tok:
                    continue

                yes_mid = self._get_mid(yes_tok)
                if yes_mid <= 0:
                    continue

                # Momentum says price going up -> YES should be priced higher
                if bullish and yes_mid < 0.55:
                    model_p = min(0.55 + abs(change_24h) / 100, 0.85)
                    edge    = model_p - yes_mid
                    if edge >= 0.08:
                        signals.append({
                            "token_id":    yes_tok,
                            "side":        "BUY",
                            "market_prob": yes_mid,
                            "model_prob":  round(model_p, 3),
                            "edge":        round(edge, 4),
                            "label":       mkt.get("question","")[:50],
                            "source":      "crypto",
                            "change_24h":  change_24h,
                            "volume":      float(mkt.get("volume", 0) or 0),
                        })
                elif not bullish and yes_mid > 0.45:
                    model_p = max(0.45 - abs(change_24h) / 100, 0.15)
                    edge    = yes_mid - model_p
                    if edge >= 0.08:
                        signals.append({
                            "token_id":    yes_tok,
                            "side":        "SELL",
                            "market_prob": yes_mid,
                            "model_prob":  round(model_p, 3),
                            "edge":        round(edge, 4),
                            "label":       mkt.get("question","")[:50],
                            "source":      "crypto",
                            "volume":      float(mkt.get("volume", 0) or 0),
                        })

        return signals

    def _get_crypto_markets(self) -> list:
        try:
            r = requests.get(f"{GAMMA_API}/markets",
                             params={"active": True, "tag": "crypto",
                                     "limit": 50}, timeout=10)
            return r.json()
        except Exception:
            return []

    def _get_mid(self, tid: str) -> float:
        try:
            r = requests.get(f"{CLOB_API}/midpoint",
                             params={"token_id": tid}, timeout=4)
            return float(r.json().get("mid", 0))
        except Exception:
            return 0.0
