from collections import defaultdict
from typing import List, Dict

class DeviceStore:
    def __init__(self):
        self.store: Dict[str, List[dict]] = defaultdict(list)

    def add(self, device_id: str, record: dict):
        self.store[device_id].append(record)

    def get(self, device_id: str):
        return self.store.get(device_id, [])

device_store = DeviceStore()