from datetime import datetime
import json

from app.models.sensor import SensorPayload
from app.core.security import decrypt_value
from app.store.memory_store import device_store
from app.store.file_store import append_record


def process_sensor_data(payload: SensorPayload):
    try:
        # Decrypt full payload
        decrypted_str = decrypt_value(payload.data)

        # Convert to JSON
        decrypted_data = json.loads(decrypted_str)

    except Exception as e:
        decrypted_data = {
            "error": "DECRYPTION_FAILED",
            "message": str(e)
        }

    record = {
        "timestamp": payload.timestamp,
        "received_at": datetime.utcnow().isoformat(),
        "data": decrypted_data
    }

    # Store in memory
    device_store.add(payload.device_id, record)

    # Persist to file
    append_record(payload.device_id, record)

    return record