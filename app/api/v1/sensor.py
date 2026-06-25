from fastapi import APIRouter, HTTPException, Request
from app.models.sensor import SensorPayload
from app.services.sensor_service import process_sensor_data
from app.core.logger import get_logger
from app.store.memory_store import device_store
from app.api.v1.stream import push_sse_event
from app.store.session_store import session_store
from datetime import datetime
import json


logger = get_logger(__name__)


router = APIRouter()


@router.post("/sensor")
async def receive_sensor_data(request: Request):

    """ 
    Receives sensor payload from frontend.

    Frontend must send exact raw captured data (no encryption on the frontend).

    Expected format:
       {
         "device_id": "...",
         "data": { "noise": <number|string>, "people": <number|string>, "motion": <string> }
       }

    Backend is responsible for encryption/decryption.
    """

    logger.info(f"Sensor request: {request.method} {request.url}")

    try:
        body = await request.json()
        logger.info(f"Request body: {body}")


        decrypted_data = None

        # ----------------------------
        # Preferred wrapper: frontend sends exact raw captured values (no encryption on frontend)
        if isinstance(body, dict) and "device_id" in body and "data" in body:
            device_id_from_body = body.get("device_id")
            incoming = body.get("data")

            if not isinstance(incoming, dict):
                raise HTTPException(status_code=400, detail="Invalid payload structure: data must be an object")

            # Backend takes raw values and encrypts internally (via process_sensor_data / storage layer)
            decrypted_data = {
                "device_id": device_id_from_body,
                "data": incoming,
            }

        else:
            raise HTTPException(status_code=400, detail="Invalid request body")


        # ----------------------------
        # Validate structure
        # ----------------------------
        if not isinstance(decrypted_data, dict) or "device_id" not in decrypted_data or "data" not in decrypted_data:
            raise HTTPException(status_code=400, detail="Invalid payload structure")

        device_id = decrypted_data["device_id"]
        if not isinstance(device_id, str) or not device_id.strip():
            raise HTTPException(status_code=400, detail="Invalid device_id")

        # ----------------------------
        # Process
        # ----------------------------
        # session_id resolution (connection-scoped); frontend should send x-session-id
        session_id = request.headers.get("x-session-id")
        if not session_id:
            # fallback session: still allows decrypt to work, but is shared per missing header
            session_id = f"{device_id}-default"

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
        # register this record for the active session
        session_store.create_or_get(session_id=session_id, device_id=device_id)
        session_store.add_record_for_session(session_id=session_id, record_key=record["record_id"])

        push_sse_event({"device": device_id, "record": record})


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

