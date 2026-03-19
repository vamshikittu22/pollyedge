"""
Earnings Agent — Combines Daloopa + Yahoo Finance + Alpha Vantage
to build a beat probability, then compares vs Polymarket crowd.
Falls back gracefully if any source is unavailable.
"""
import os, re, time, requests
from bot.agents.base_agent import BaseAgent

DALOOPA_KEY    = os.getenv("DALOOPA_API_KEY")
AV_KEY         = os.getenv("ALPHA_VANTAGE_KEY")
GAMMA_API      = "https://gamma-api.polymarket.com"
CLOB_API       = "https://clob.polymarket.com"

class EarningsAgent(BaseAgent):
    def __init__(self, q):
        super().__init__(q, "EarningsAgent", interval=180)  # Every 3 min

    def scan(self) -> list[dict]:
        markets = self._get_earnings_markets()
        signals = []

        for mkt in markets[:20]:
            try:
                label   = mkt.get("question", "")
                tokens  = mkt.get("tokens", [])
                yes_tok = tokens[0].get("token_id") if tokens else None
                ticker  = self._extract_ticker(label)

                if not yes_tok or not ticker:
                    continue

                yes_mid  = self._get_midpoint(yes_tok)
                model_p  = self._aggregate_beat_probability(ticker)

                if not model_p or yes_mid <= 0:
                    continue

                edge = model_p - yes_mid
                if abs(edge) >= 0.08:
                    signals.append({
                        "token_id":    yes_tok,
                        "ticker":      ticker,
                        "side":        "BUY" if edge > 0 else "SELL",
                        "market_prob": yes_mid,
                        "model_prob":  model_p,
                        "edge":        round(edge, 4),
                        "label":       label[:50],
                        "source":      "earnings",
                        "volume":      float(mkt.get("volume", 0) or 0),
                    })
                time.sleep(0.3)
            except Exception as e:
                self.log.warning(f"EarningsAgent error: {e}")
                continue

        return sorted(signals, key=lambda x: abs(x["edge"]), reverse=True)

    def _aggregate_beat_probability(self, ticker: str) -> float | None:
        """
        Combine multiple sources into one beat probability.
        Priority: Daloopa > Yahoo Finance > Alpha Vantage > Simple estimate
        """
        probabilities = []
        weights       = []

        # Source 1: Daloopa (highest weight — institutional data)
        d = self._daloopa_beat_rate(ticker)
        if d:
            probabilities.append(d)
            weights.append(3)

        # Source 2: Yahoo Finance surprise history
        y = self._yahoo_eps_surprise(ticker)
        if y:
            probabilities.append(y)
            weights.append(2)

        # Source 3: Alpha Vantage earnings data
        a = self._alpha_vantage_earnings(ticker)
        if a:
            probabilities.append(a)
            weights.append(1)

        if not probabilities:
            return None

        # Weighted average
        total_weight = sum(weights)
        return round(sum(p * w for p, w in zip(probabilities, weights)) / total_weight, 4)

    def _daloopa_beat_rate(self, ticker: str) -> float | None:
        if not DALOOPA_KEY:
            return None
        try:
            resp = requests.get(
                "https://api.daloopa.com/v1/earnings/history",
                headers={"Authorization": f"Bearer {DALOOPA_KEY}"},
                params={"ticker": ticker, "periods": 12},
                timeout=8
            )
            quarters = resp.json().get("quarters", [])
            if len(quarters) < 4:
                return None
            beats = sum(1 for q in quarters if q.get("beat_miss") == "beat")
            return beats / len(quarters)
        except Exception:
            return None

    def _yahoo_eps_surprise(self, ticker: str) -> float | None:
        """Fetch Yahoo Finance earnings history for beat rate."""
        try:
            url  = f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}"
            resp = requests.get(
                url,
                params={"modules": "earningsHistory"},
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=8
            )
            history = (resp.json()
                       .get("quoteSummary", {})
                       .get("result", [{}])[0]
                       .get("earningsHistory", {})
                       .get("history", []))
            if len(history) < 2:
                return None
            beats = sum(1 for q in history
                       if q.get("surprisePercent", {}).get("raw", 0) > 0)
            return beats / len(history)
        except Exception:
            return None

    def _alpha_vantage_earnings(self, ticker: str) -> float | None:
        if not AV_KEY:
            return None
        try:
            resp = requests.get(
                "https://www.alphavantage.co/query",
                params={"function": "EARNINGS", "symbol": ticker, "apikey": AV_KEY},
                timeout=8
            )
            quarters = resp.json().get("quarterlyEarnings", [])[:8]
            if len(quarters) < 2:
                return None
            beats = sum(1 for q in quarters
                       if float(q.get("surprisePercentage", 0) or 0) > 0)
            return beats / len(quarters)
        except Exception:
            return None

    def _get_earnings_markets(self) -> list:
        try:
            r = requests.get(f"{GAMMA_API}/markets",
                             params={"active": True, "tag": "earnings", "limit": 50},
                             timeout=10)
            return [m for m in r.json() if m.get("tokens")]
        except Exception:
            return []

    def _get_midpoint(self, token_id: str) -> float:
        try:
            r = requests.get(f"{CLOB_API}/midpoint",
                             params={"token_id": token_id}, timeout=5)
            return float(r.json().get("mid", 0))
        except Exception:
            return 0.0

    def _extract_ticker(self, question: str) -> str | None:
        match = re.search(r"\b([A-Z]{2,5})\b", question)
        return match.group(1) if match else None
