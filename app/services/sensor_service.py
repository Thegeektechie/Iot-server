from datetime import datetime
import json

from app.models.sensor import SensorPayload
from app.core.security import decrypt_value
from app.core.logger import get_logger
from app.store.memory_store import device_store
from app.store.file_store import append_record

logger = get_logger(__name__)


def process_sensor_data(payload: SensorPayload):
    try:
        if isinstance(payload.data, str):
            logger.info("Processing encrypted data")
            # Decrypt full payload
            decrypted_str = decrypt_value(payload.data)
            # Convert to JSON
            decrypted_data = json.loads(decrypted_str)
        else:
            logger.info("Processing plain data (TEMP)")
            decrypted_data = payload.data  # already dict

    except Exception as e:
        logger.error(f"Data processing failed: {e}")
        decrypted_data = {
            "error": "PROCESSING_FAILED",
            "message": str(e)
        }

    record = {
        "timestamp": getattr(payload, 'timestamp', datetime.utcnow().isoformat()),
        "received_at": datetime.utcnow().isoformat(),
        "data": decrypted_data
    }

    # Store in memory
    device_store.add(payload.device_id, record)

    # Persist to file
    append_record(payload.device_id, record)

    logger.info(f"Processed record for {payload.device_id}")
    return record
