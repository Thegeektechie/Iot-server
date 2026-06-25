from datetime import datetime
from app.models.sensor import SensorPayload

from app.core.security import encrypt_value

from app.core.logger import get_logger
from app.store.memory_store import device_store
from app.store.file_store import append_record

logger = get_logger(__name__)


def process_sensor_data(payload: SensorPayload):
    try:
        # Frontend must send exact raw captured values (no encryption on frontend)
        # Backend encrypts after receiving.
        logger.info("Processing raw plain data")
        decrypted_data = payload.data  # type: ignore[assignment]


    except Exception as e:
        logger.error(f"Data processing failed: {e}")
        decrypted_data = {
            "error": "PROCESSING_FAILED",
            "message": str(e)
        }

    def _encrypt_any(value):
        if isinstance(value, (str, int, float)):
            return encrypt_value(str(value))
        if isinstance(value, dict):
            return {k: _encrypt_any(v) for k, v in value.items()}
        if isinstance(value, list):
            return [_encrypt_any(v) for v in value]
        return value

    # Backend owns encryption: store encrypted fields for display/audit
    encrypted_data = decrypted_data
    if isinstance(decrypted_data, (dict, list)):
        encrypted_data = _encrypt_any(decrypted_data)

    record = {
        "record_id": f"{payload.device_id}-{datetime.utcnow().timestamp()}-{id(payload)}",
        "timestamp": getattr(payload, 'timestamp', datetime.utcnow().isoformat()),
        "received_at": datetime.utcnow().isoformat(),
        "data": encrypted_data
    }



    # Store in memory
    device_store.add(payload.device_id, record)

    # Persist to file
    append_record(payload.device_id, record)

    logger.info(f"Processed record for {payload.device_id}")
    return record
