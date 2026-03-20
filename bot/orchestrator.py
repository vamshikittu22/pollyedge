"""
PollyEdge Orchestrator — Manages 5 parallel signal agents.
Each agent runs in its own thread, sends signals to approval queue.
Non-blocking approval via ThreadPoolExecutor so one pending approval
doesn't freeze the entire signal pipeline.
"""

import os
from dotenv import load_dotenv
import threading
import queue
import time
import logging
import concurrent.futures
from datetime import datetime

from bot.agents.earnings_agent import EarningsAgent
from bot.agents.news_agent import NewsAgent
from bot.agents.momentum_agent import MomentumAgent
from bot.agents.arb_agent import ArbAgent
from bot.agents.crypto_agent import CryptoAgent
from bot.risk_manager import RiskManager, load_state
from bot.approval_gate import ApprovalGate
from bot.notifier import notify

log = logging.getLogger("Orchestrator")

load_dotenv()  # Load environment variables before any os.getenv() calls


def _get_live_balance() -> float:
    """Reload balance from bot_state.json on every call."""
    state = load_state()
    starting = float(os.getenv("STARTING_BALANCE", 10))
    return starting + state.get("all_time_pnl", 0)


class Orchestrator:
    def __init__(self, client, balance: float, dry_run: bool):
        self.client = client
        self.dry_run = dry_run
        self.signal_q = queue.Queue()  # Agents post signals here
        self.seen_tokens = set()  # Dedup: don't double-enter
        self._seen_lock = threading.Lock()  # Protect seen_tokens from race conditions
        self.approval = ApprovalGate()
        self._pending_futures: dict[str, concurrent.futures.Future] = {}

        self.agents = [
            EarningsAgent(self.signal_q),
            NewsAgent(self.signal_q),
            MomentumAgent(self.signal_q),
            ArbAgent(self.signal_q),
            CryptoAgent(self.signal_q),
        ]

    def start(self):
        """Launch all agents in parallel threads."""
        log.info(f"Starting swarm of {len(self.agents)} agents...")
        notify(f"Swarm started — {len(self.agents)} agents hunting edges", "🚀")

        for agent in self.agents:
            t = threading.Thread(target=agent.run, daemon=True, name=agent.name)
            t.start()
            log.info(f"  {agent.name} launched")
            time.sleep(3)  # Stagger start to avoid rate limits

        self._process_signals()  # Main thread processes approval queue

    def _process_signals(self):
        """Main loop: read signals, deduplicate, send for non-blocking approval."""
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=3)

        while True:
            try:
                # Clean up completed futures
                done_keys = [k for k, f in self._pending_futures.items() if f.done()]
                for k in done_keys:
                    del self._pending_futures[k]

                signal = self.signal_q.get(timeout=1)

                # Skip duplicates (already traded or pending approval)
                with self._seen_lock:
                    if signal["token_id"] in self.seen_tokens:
                        continue
                if signal["token_id"] in self._pending_futures:
                    continue

                # Risk check with LIVE balance (Bug 3 fix)
                current_balance = _get_live_balance()
                rm = RiskManager(current_balance)
                allowed, reason = rm.can_trade()
                if not allowed:
                    log.info(f"Signal blocked by risk: {reason}")
                    continue

                # Score signals (higher is better)
                signal["score"] = self._score_signal(signal)
                if signal["score"] < 50:
                    log.info(
                        f"Signal too weak (score={signal['score']}): {signal['label']}"
                    )
                    continue

                log.info(
                    f"Signal queued for approval: {signal['label']} | "
                    f"edge={signal.get('edge', 0):.1%} | score={signal['score']}"
                )

                # Non-blocking: submit approval to thread pool (Bug 6 fix)
                future = executor.submit(self._approve_and_execute, signal)
                self._pending_futures[signal["token_id"]] = future

            except queue.Empty:
                # Still clean up completed futures during idle
                done_keys = [k for k, f in self._pending_futures.items() if f.done()]
                for k in done_keys:
                    del self._pending_futures[k]
                continue
            except Exception as e:
                log.error(f"Orchestrator error: {e}")
                time.sleep(5)

    def _approve_and_execute(self, signal: dict):
        """Run approval + execution in a background thread."""
        try:
            # Re-check live balance right before approval
            current_balance = _get_live_balance()
            rm = RiskManager(current_balance)
            size = rm.position_size()

            approved = self.approval.request_approval(signal, size)

            if approved:
                self._execute(signal, rm)
                with self._seen_lock:
                    self.seen_tokens.add(signal["token_id"])
            else:
                log.info(f"Rejected: {signal['label']}")
                notify(f"Rejected: {signal['label']}", "🚫")
        except Exception as e:
            log.error(f"Approve/execute error: {e}")

    def _score_signal(self, signal: dict) -> int:
        """Score 0-100. Higher = better trade opportunity."""
        score = 0
        edge = abs(signal.get("edge", 0))

        if edge >= 0.20:
            score += 40
        elif edge >= 0.15:
            score += 30
        elif edge >= 0.10:
            score += 20
        elif edge >= 0.08:
            score += 10

        # Boost by source reliability
        source_scores = {
            "earnings": 25,  # Daloopa fundamental data
            "underpriced": 15,  # YES+NO sum discount (not true arb)
            "news": 20,  # News sentiment
            "momentum": 15,  # Price momentum
            "crypto": 15,  # Crypto signals
        }
        score += source_scores.get(signal.get("source", ""), 10)

        # Boost for high volume markets (more liquidity)
        vol = signal.get("volume", 0)
        if vol > 500_000:
            score += 20
        elif vol > 100_000:
            score += 10

        # Boost if multiple agents agree on same market
        confirmations = signal.get("confirmations", 1)
        score += (confirmations - 1) * 15

        return min(score, 100)

    def _execute(self, signal: dict, rm: RiskManager):
        """Execute approved trade and log it."""
        size = rm.position_size()
        token = signal["token_id"]
        side = signal["side"]
        price = signal.get("market_prob", 0.5)
        label = signal["label"]

        rm.record_trade_open(token, side, size, price, label)

        if self.dry_run:
            log.info(f"[DRY] EXECUTED: {side} {label} | ${size:.2f} @ {price:.4f}")
            notify(f"[DRY] {side} {label} | ${size:.2f} @ {price:.4f}", "🧪")
            return

        try:
            from py_clob_client.clob_types import MarketOrderArgs, OrderType

            order = self.client.create_market_order(
                MarketOrderArgs(token_id=token, amount=size)
            )
            resp = self.client.post_order(order, OrderType.FOK)
            if resp.get("status") == "matched":
                notify(f"LIVE TRADE: {side} {label} | ${size:.2f}", "✅")
            else:
                rm.record_trade_close(token, price)  # Undo open
                notify(f"FOK not filled: {label}", "⚠️")
        except Exception as e:
            log.error(f"Execution error: {e}")
            rm.record_trade_close(token, price)
            notify(f"Execution failed: {e}", "🚨")
