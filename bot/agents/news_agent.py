"""
News Agent — Scans NewsAPI for breaking news that affects Polymarket markets.
Cross-references with active markets to find crowd pricing lag.
"""
import os, requests
from bot.agents.base_agent import BaseAgent

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
GAMMA_API   = "https://gamma-api.polymarket.com"
CLOB_API    = "https://clob.polymarket.com"

POSITIVE_WORDS = {"beats","surpasses","record","rallies","soars","gains","up","bullish","approved"}
NEGATIVE_WORDS = {"misses","falls","drops","crash","below","down","bearish","denied","fails"}

class NewsAgent(BaseAgent):
    def __init__(self, q):
        super().__init__(q, "NewsAgent", interval=120)

    def scan(self) -> list[dict]:
        if not NEWSAPI_KEY:
            return []

        # Fetch top financial news
        try:
            resp = requests.get(
                "https://newsapi.org/v2/top-headlines",
                params={"category": "business", "language": "en",
                        "pageSize": 20, "apiKey": NEWSAPI_KEY},
                timeout=10
            )
            articles = resp.json().get("articles", [])
        except Exception:
            return []

        signals = []
        markets = self._get_active_markets()

        for article in articles:
            headline = (article.get("title", "") + " " + article.get("description", "")).lower()
            words    = set(headline.split())

            sentiment = None
            if words & POSITIVE_WORDS:
                sentiment = "positive"
            elif words & NEGATIVE_WORDS:
                sentiment = "negative"
            else:
                continue

            # Find matching Polymarket market
            for mkt in markets:
                question = mkt.get("question", "").lower()
                tokens   = mkt.get("tokens", [])
                if not tokens:
                    continue

                # Check if news is relevant to this market
                overlap = len(set(question.split()) & set(headline.split()))
                if overlap < 3:
                    continue

                try:
                    yes_tok = tokens[0].get("token_id")
                    yes_mid = self._get_midpoint(yes_tok)
                    if yes_mid <= 0:
                        continue

                    # Positive news -> YES underpriced, Negative -> YES overpriced
                    if sentiment == "positive" and yes_mid < 0.60:
                        edge = 0.70 - yes_mid  # Estimate crowd should be at 70%+
                        signals.append({
                            "token_id":    yes_tok,
                            "side":        "BUY",
                            "market_prob": yes_mid,
                            "model_prob":  0.70,
                            "edge":        round(edge, 4),
                            "label":       mkt["question"][:50],
                            "source":      "news",
                            "volume":      float(mkt.get("volume", 0) or 0),
                            "headline":    article.get("title", "")[:60],
                        })
                    elif sentiment == "negative" and yes_mid > 0.40:
                        edge = yes_mid - 0.30
                        signals.append({
                            "token_id":    yes_tok,
                            "side":        "SELL",
                            "market_prob": yes_mid,
                            "model_prob":  0.30,
                            "edge":        round(edge, 4),
                            "label":       mkt["question"][:50],
                            "source":      "news",
                            "volume":      float(mkt.get("volume", 0) or 0),
                        })
                except Exception:
                    continue

        return signals

    def _get_active_markets(self) -> list:
        try:
            r = requests.get(f"{GAMMA_API}/markets",
                             params={"active": True, "limit": 100}, timeout=10)
            return r.json()
        except Exception:
            return []

    def _get_midpoint(self, token_id: str) -> float:
        try:
            r = requests.get(f"{CLOB_API}/midpoint",
                             params={"token_id": token_id}, timeout=5)
            return float(r.json().get("mid", 0))
        except Exception:
            return 0.0
