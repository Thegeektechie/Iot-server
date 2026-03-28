import os
import json
from threading import Lock
from datetime import datetime
from app.config import settings

# Ensure data directory exists
os.makedirs(settings.DATA_DIR, exist_ok=True)

lock = Lock()


def _sanitize_device_id(device_id: str) -> str:
    """
    Prevent path traversal and invalid filenames
    """
    return "".join(c for c in device_id if c.isalnum() or c in ("-", "_"))


def append_record(device_id: str, record: dict):
    """
    Append a record safely to a JSONL file
    """

    safe_device_id = _sanitize_device_id(device_id)

    path = os.path.join(settings.DATA_DIR, f"{safe_device_id}.jsonl")

    try:
        with lock:
            with open(path, "a", encoding="utf-8") as f:
                json.dump(record, f)
                f.write("\n")
                f.flush()  # ensure write
                os.fsync(f.fileno())  # force disk write

    except Exception as e:
        # Minimal fallback logging (avoid circular import)
        print(f"[FILE_STORE_ERROR] Failed to write record: {str(e)}")