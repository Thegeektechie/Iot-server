from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import json
import asyncio
from app.store.memory_store import device_store

router = APIRouter()


async def event_stream():
    """
    Real-time Server Sent Events stream
    Non-blocking, efficient, and scalable
    """

    last_index = {}

    while True:
        has_data = False

        for device_id, records in device_store.store.items():
            index = last_index.get(device_id, 0)

            if index < len(records):
                new_records = records[index:]

                for record in new_records:
                    payload = {
                        "device": device_id,
                        "record": record
                    }

                    yield f"data: {json.dumps(payload)}\n\n"
                    has_data = True

                last_index[device_id] = len(records)

        # ⚡ If no new data, do short async sleep
        if not has_data:
            await asyncio.sleep(0.3)
        else:
            # faster loop when active
            await asyncio.sleep(0.05)


@router.get("/stream")
async def stream():
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )