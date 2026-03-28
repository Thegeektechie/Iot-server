from fastapi import APIRouter, HTTPException, Request
from app.models.sensor import SensorPayload
from app.services.sensor_service import process_sensor_data
from app.core.security import decrypt_payload
from app.store.memory_store import device_store
from datetime import datetime

router = APIRouter()


@router.post("/sensor")
async def receive_sensor_data(request: Request):
    """
    Receives encrypted sensor payload from frontend
    Decrypts -> Processes -> Stores -> Streams
    """

    try:
        body = await request.json()

        # Validate payload existence
        if "payload" not in body:
            raise HTTPException(status_code=400, detail="Missing encrypted payload")

        encrypted_payload = body["payload"]

        # 🔐 STEP 1: Decrypt
        try:
            decrypted_data = decrypt_payload(encrypted_payload)
        except Exception:
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

        # 📡 STEP 4: Register / Update device
        device_store.store.setdefault(device_id, [])
        device_store.store[device_id].append(record)

        # Add last seen timestamp
        device_store.store[device_id][-1]["last_seen"] = datetime.utcnow().isoformat()

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