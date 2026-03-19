import time, logging, queue
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    def __init__(self, signal_queue: queue.Queue, name: str, interval: int = 30):
        self.q        = signal_queue
        self.name     = name
        self.interval = interval
        self.log      = logging.getLogger(name)

    def run(self):
        self.log.info(f"{self.name} started")
        while True:
            try:
                signals = self.scan()
                for s in (signals or []):
                    s["agent"] = self.name
                    self.q.put(s)
                    self.log.info(f"Signal: {s['label'][:40]} | edge={s.get('edge',0):+.1%}")
            except Exception as e:
                self.log.error(f"{self.name} scan error: {e}")
            time.sleep(self.interval)

    @abstractmethod
    def scan(self) -> list[dict]:
        """Return list of signal dicts. Each needs: token_id, label, side, edge, source."""
        pass
