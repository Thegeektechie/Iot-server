from fastapi import APIRouter, HTTPException, Request
from app.models.sensor import SensorPayload
from app.services.sensor_service import process_sensor_data
from app.core.security import decrypt_value
from app.core.logger import get_logger
from app.store.memory_store import device_store
from datetime import datetime

logger = get_logger(__name__)

router = APIRouter()


@router.post("/sensor")
async def receive_sensor_data(request: Request):
    """
    Receives encrypted sensor payload from frontend
    Decrypts -> Processes -> Stores -> Streams
    Supports plain JSON temporarily for testing
    """

    logger.info(f"Sensor request: {request.method} {request.url}")
    
    try:
        body = await request.json()
        logger.info(f"Request body: {body}")

        # 🔐 STEP 1: Decrypt (or plain data TEMP)
        if "payload" not in body:
            logger.warning("Plain data received (TEMP support - add encryption in frontend)")
            # Generate device_id if missing
            plain_device_id = body.get("device_id", f"plain_device_{hash(str(body)) % 10000}")
            decrypted_data = {
                "device_id": plain_device_id,
                "data": body
            }
            logger.info(f"Using plain device_id: {plain_device_id}")
        else:
            encrypted_payload = body["payload"]
            try:
                decrypted_data = decrypt_value(encrypted_payload)
                logger.info("Payload decrypted successfully")
            except Exception as e:
                logger.error(f"Decryption failed: {e}")
                raise HTTPException(status_code=400, detail="Invalid encryption")

        # 🔎 STEP 2: Validate structure
        if "device_id" not in decrypted_data or "data" not in decrypted_data:
            raise HTTPException(status_code=400, detail="Invalid payload structure")

        device_id = decrypted_data["device_id"]

        # 🧠 STEP 3: Process
        record = process_sensor_data(
            SensorPayload(
                device_id=device_id,
                data=decrypted_data["data"]
            )
        )

        # 📡 STEP 4: Register / Update device (defaultdict(deque) handles creation)
        device_store.store[device_id].append(record)

        # Add last seen timestamp
        device_store.store[device_id][-1]["last_seen"] = datetime.utcnow().isoformat()
        
        logger.info(f"Successfully stored data for device: {device_id}. Record count: {len(device_store.store[device_id])}")

        # 🚀 STEP 5: Return response
        return {
            "status": "success",
            "device": device_id,
            "record": record
        }

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))