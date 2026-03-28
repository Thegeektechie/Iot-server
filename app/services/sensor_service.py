from datetime import datetime
from app.models.sensor import SensorPayload
from app.core.security import decrypt_value
from app.store.memory_store import device_store
from app.store.file_store import append_record

def process_sensor_data(payload: SensorPayload):
    decrypted = {}

    for key, value in payload.data.items():
        if value:
            try:
                decrypted[key] = decrypt_value(value)
            except:
                decrypted[key] = "ERR"

    record = {
        "timestamp": payload.timestamp,
        "received_at": datetime.utcnow().isoformat(),
        "data": decrypted
    }

    device_store.add(payload.device_id, record)
    append_record(payload.device_id, record)

    return record