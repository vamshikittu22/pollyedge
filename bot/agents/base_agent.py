import time
import logging
import queue
from abc import ABC, abstractmethod
from datetime import datetime, timezone

from bot.db import update_agent_status


class BaseAgent(ABC):
    def __init__(self, signal_queue: queue.Queue, name: str, interval: int = 30):
        self.q = signal_queue
        self.name = name
        self.interval = interval
        self.log = logging.getLogger(name)

    def run(self):
        self.log.info(f"{self.name} started")
        self._write_status("running", 0)
        while True:
            try:
                signals = self.scan()
                count = len(signals or [])
                self._write_status("running", count)
                for s in signals or []:
                    s["agent"] = self.name
                    self.q.put(s)
                    self.log.info(
                        f"Signal: {s['label'][:40]} | edge={s.get('edge', 0):+.1%}"
                    )
            except Exception as e:
                self.log.error(f"{self.name} scan error: {e}")
                self._write_status("error", 0)
            time.sleep(self.interval)

    def _write_status(self, status: str, signals_found: int):
        """Write this agent's status to SQLite."""
        update_agent_status(self.name, status, signals_found)

    @abstractmethod
    def scan(self) -> list[dict]:
        """Return list of signal dicts. Each needs: token_id, label, side, edge, source."""
        pass
