from fastapi import APIRouter, HTTPException, Request
from app.models.sensor import SensorPayload
from app.services.sensor_service import process_sensor_data
from app.core.security import decrypt_value
from app.core.logger import get_logger
from app.store.memory_store import device_store
from datetime import datetime
import json

logger = get_logger(__name__)

router = APIRouter()


@router.post("/sensor")
async def receive_sensor_data(request: Request):
    """ 
    Receives sensor payload from frontend.

    Supported input formats (to handle current frontend/backend mismatch):

    1) Legacy wrapper (TEMP): {"payload": "<backend-aes-gcm-b64>"}
    2) Preferred format (recommended):
       {
         "device_id": "...",
         "data": { "noise": <encrypted|plain>, "people": <encrypted|plain>, "motion": <encrypted|plain> }
       }

    Note:
    - Current frontend uses CryptoJS AES with a passphrase (different from backend AES-256-GCM).
    - This endpoint attempts backend decrypt and, if it fails, treats values as TEMP plain fields.
    """

    logger.info(f"Sensor request: {request.method} {request.url}")

    try:
        body = await request.json()
        logger.info(f"Request body: {body}")

        decrypted_data = None

        # ----------------------------
        # Case 1: legacy wrapper
        # ----------------------------
        if isinstance(body, dict) and "payload" in body:
            encrypted_payload = body.get("payload")
            try:
                decrypted_payload = decrypt_value(encrypted_payload)
                logger.info("Legacy payload decrypted successfully")
                decrypted_data = json.loads(decrypted_payload)
            except Exception as e:
                logger.error(f"Decryption failed (legacy wrapper): {e}")
                raise HTTPException(status_code=400, detail="Invalid encryption")

        # ----------------------------
        # Case 2: preferred wrapper
        # ----------------------------
        elif isinstance(body, dict) and "device_id" in body and "data" in body:
            device_id_from_body = body.get("device_id")
            incoming = body.get("data")

            if not isinstance(incoming, dict):
                raise HTTPException(status_code=400, detail="Invalid payload structure: data must be an object")

            decrypted_fields = {}
            decrypt_errors = []

            # Attempt decrypt each field if it is a string.
            for k, v in incoming.items():
                if isinstance(v, str):
                    try:
                        plain = decrypt_value(v)  # backend AES-256-GCM expects this format

                        # If decrypt_value returns a JSON string, parse it.
                        try:
                            decrypted_fields[k] = json.loads(plain)
                        except Exception:
                            decrypted_fields[k] = plain
                    except Exception as e:
                        # TEMP passthrough: keep raw value
                        decrypt_errors.append(f"{k}:{str(e)[:80]}")
                        decrypted_fields[k] = v
                else:
                    decrypted_fields[k] = v

            decrypted_data = {
                "device_id": device_id_from_body,
                "data": decrypted_fields,
            }

            if decrypt_errors:
                logger.warning(
                    "Some fields could not be decrypted (TEMP passthrough). "
                    f"Errors: {decrypt_errors}"
                )

        # ----------------------------
        # Case 3: TEMP plain JSON
        # ----------------------------
        elif isinstance(body, dict):
            logger.warning("Plain data received (TEMP support)")
            plain_device_id = body.get("device_id", f"plain_device_{hash(str(body)) % 10000}")
            decrypted_data = {
                "device_id": plain_device_id,
                "data": body,
            }

        else:
            raise HTTPException(status_code=400, detail="Invalid request body")

        # ----------------------------
        # Validate structure
        # ----------------------------
        if not isinstance(decrypted_data, dict) or "device_id" not in decrypted_data or "data" not in decrypted_data:
            raise HTTPException(status_code=400, detail="Invalid payload structure")

        device_id = decrypted_data["device_id"]

        # ----------------------------
        # Process
        # ----------------------------
        record = process_sensor_data(
            SensorPayload(
                device_id=device_id,
                data=decrypted_data["data"],
            )
        )

        # ----------------------------
        # Store + metadata
        # ----------------------------
        device_store.store[device_id].append(record)
        device_store.store[device_id][-1]["last_seen"] = datetime.utcnow().isoformat()

        logger.info(
            "Successfully stored data for device: %s. Record count: %s",
            device_id,
            len(device_store.store[device_id]),
        )

        return {"status": "success", "device": device_id, "record": record}

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception("Sensor endpoint failed")
        raise HTTPException(status_code=500, detail=str(e))

