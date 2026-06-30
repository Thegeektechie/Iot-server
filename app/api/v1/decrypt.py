from fastapi import APIRouter, HTTPException, Request
from app.core.security import decrypt_value
from app.core.logger import get_logger
from app.store.memory_store import device_store
from app.store.session_store import session_store
from datetime import datetime


router = APIRouter()
logger = get_logger(__name__)

PASSCODE = "9910"


@router.post("/decrypt")
async def decrypt_current_session(request: Request):
    """Decrypt all encrypted fields received in the current connection/session.

    Passcode required: 9910

    Client must send JSON:
      {
        "passcode": "9910",
        "session_id": "..."   (optional; if omitted, server will use a fallback header)
      }

    The server decrypts the encrypted `record.data` fields in memory for the session's device.
    """

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    passcode = body.get("passcode")
    if passcode != PASSCODE:
        raise HTTPException(status_code=403, detail="Invalid passcode")

    # session_id resolution
    session_id = body.get("session_id")
    if not session_id:
        # allow dashboard to send a header; not required by the assignment, but safe fallback
        session_id = request.headers.get("x-session-id")

    if not session_id:
        raise HTTPException(status_code=400, detail="Missing session_id")

    sess = session_store.get_session(session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")

    device_id = sess.device_id

    sess_records = sess.records_received
    if not sess_records:
        raise HTTPException(status_code=404, detail="No records for this session")

    updated = []

    # Build a lookup for record_id -> record reference
    # device_store holds dict records inside a deque
    for record in device_store.store.get(device_id, []):
        if record.get("record_id") not in set(sess_records):
            continue

        data_obj = record.get("data")
        if not isinstance(data_obj, dict):
            continue

        def _decrypt_any(value):
            if isinstance(value, str):
                try:
                    return decrypt_value(value)
                except Exception:
                    return value
            if isinstance(value, dict):
                return {k: _decrypt_any(v) for k, v in value.items()}
            if isinstance(value, list):
                return [_decrypt_any(v) for v in value]
            return value

        decrypted_obj = _decrypt_any(data_obj)

        # Update timestamps after decryption as requested
        record["timestamp"] = datetime.utcnow().isoformat()
        record["decrypted_at"] = datetime.utcnow().isoformat()
        record["data"] = decrypted_obj
        updated.append(record)


    # clear session records after decrypt
    session_store.clear_session_records(session_id)

    return {"status": "success", "device": device_id, "decrypted_records": updated}

