from collections import defaultdict, deque
from threading import Lock
from typing import Dict, List
from datetime import datetime


MAX_RECORDS_PER_DEVICE = 500  # prevent memory overflow


class DeviceStore:
    def __init__(self):
        # Store records with bounded size
        self.store: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=MAX_RECORDS_PER_DEVICE)
        )

        # Track device metadata
        self.meta: Dict[str, dict] = {}

        self.lock = Lock()

    def add(self, device_id: str, record: dict):
        with self.lock:
            self.store[device_id].append(record)

            # Update metadata
            self.meta[device_id] = {
                "last_seen": datetime.utcnow().isoformat(),
                "records": len(self.store[device_id])
            }

    def get(self, device_id: str, limit: int = 50) -> List[dict]:
        with self.lock:
            records = list(self.store.get(device_id, []))
            return records[-limit:]

    def get_all(self, limit: int = 50) -> Dict[str, List[dict]]:
        with self.lock:
            return {
                device_id: list(records)[-limit:]
                for device_id, records in self.store.items()
            }

    def get_devices(self) -> Dict[str, dict]:
        with self.lock:
            return self.meta.copy()


# Singleton instance
device_store = DeviceStore()