import os
import json
from threading import Lock
from app.config import settings

os.makedirs(settings.DATA_DIR, exist_ok=True)
lock = Lock()

def append_record(device_id: str, record: dict):
    path = os.path.join(settings.DATA_DIR, f"{device_id}.jsonl")

    with lock:
        with open(path, "a") as f:
            f.write(json.dumps(record) + "\n")