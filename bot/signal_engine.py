"""
PollyEdge Signal Engine — Daloopa-powered earnings signal.
Compares company beat probability vs Polymarket's crowd price.
"""
import os
import re
import time

import requests
from dotenv import load_dotenv

load_dotenv()

DALOOPA_KEY = os.getenv("DALOOPA_API_KEY")
GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"


def get_earnings_markets() -> list:
    """Fetch active Polymarket earnings markets."""
    try:
        resp = requests.get(
            f"{GAMMA_API}/markets",
            params={"active": True, "tag": "earnings", "limit": 50},
            timeout=10,
        )
        return [m for m in resp.json() if m.get("tokens")]
    except Exception as e:
        print(f"[Signal] Market fetch error: {e}")
        return []


def get_midpoint(token_id: str) -> float:
    """Get current midpoint price for a token."""
    try:
        r = requests.get(
            f"{CLOB_API}/midpoint",
            params={"token_id": token_id},
            timeout=5,
        )
        return float(r.json().get("mid", 0))
    except Exception:
        return 0.0


def get_daloopa_beat_probability(ticker: str) -> float | None:
    """
    Pull historical earnings beat rate from Daloopa API.
    Returns probability (0.0-1.0) or None if unavailable.
    """
    if not DALOOPA_KEY:
        return None
    try:
        resp = requests.get(
            "https://api.daloopa.com/v1/earnings/history",
            headers={"Authorization": f"Bearer {DALOOPA_KEY}"},
            params={"ticker": ticker, "periods": 12},
            timeout=10,
        )
        data = resp.json()
        quarters = data.get("quarters", [])
        if len(quarters) < 4:
            return None
        beats = sum(1 for q in quarters if q.get("beat_miss") == "beat")
        return round(beats / len(quarters), 4)
    except Exception as e:
        print(f"[Signal] Daloopa error for {ticker}: {e}")
        return None


def extract_ticker(question: str) -> str | None:
    """Try to extract ticker from market question string."""
    match = re.search(r"\b([A-Z]{2,5})\b", question)
    return match.group(1) if match else None


def scan_earnings_edges(min_edge: float = 0.08) -> list:
    """
    Main signal function. Returns list of edge opportunities.
    Each item: {token_id, ticker, side, market_prob, model_prob, edge, label}
    """
    markets = get_earnings_markets()
    edges: list[dict] = []

    for market in markets:
        try:
            label = market.get("question", "")
            tokens = market.get("tokens", [])
            yes_tok = tokens[0].get("token_id") if tokens else None
            ticker = market.get("ticker") or extract_ticker(label)

            if not yes_tok or not ticker:
                continue

            yes_mid = get_midpoint(yes_tok)
            model_p = get_daloopa_beat_probability(ticker)

            if not model_p or yes_mid <= 0:
                continue

            edge = model_p - yes_mid
            if abs(edge) >= min_edge:
                edges.append({
                    "token_id": yes_tok,
                    "ticker": ticker,
                    "side": "BUY" if edge > 0 else "SELL",
                    "market_prob": yes_mid,
                    "model_prob": model_p,
                    "edge": round(edge, 4),
                    "label": label[:50],
                })

            time.sleep(0.3)  # rate limit

        except Exception as e:
            print(f"[Signal] Error on {label}: {e}")
            continue

    return sorted(edges, key=lambda x: abs(x["edge"]), reverse=True)
