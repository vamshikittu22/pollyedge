import json
import os
import time
import logging
import queue
import threading
from abc import ABC, abstractmethod
from datetime import datetime, timezone

AGENTS_FILE = "agent_status.json"
_file_lock = threading.Lock()


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
        """Write this agent's status to agent_status.json atomically (temp file + rename)."""
        with _file_lock:
            try:
                existing = []
                if os.path.exists(AGENTS_FILE):
                    with open(AGENTS_FILE) as f:
                        existing = json.load(f)

                entry = {
                    "name": self.name,
                    "status": status,
                    "last_scan": datetime.now(timezone.utc).isoformat(),
                    "signals_found": signals_found,
                }

                # Replace this agent's entry or append
                existing = [e for e in existing if e.get("name") != self.name]
                existing.append(entry)

                # Atomic write: write to temp file, then rename
                temp_path = AGENTS_FILE + ".tmp"
                with open(temp_path, "w") as f:
                    json.dump(existing, f, indent=2)
                os.replace(
                    temp_path, AGENTS_FILE
                )  # Atomic on POSIX, best-effort on Windows
            except Exception:
                pass

    @abstractmethod
    def scan(self) -> list[dict]:
        """Return list of signal dicts. Each needs: token_id, label, side, edge, source."""
        pass
