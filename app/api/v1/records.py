from fastapi import APIRouter
from app.store.memory_store import device_store

router = APIRouter()


@router.delete("/records")
async def clear_records():
    """Clear all in-memory records for all devices.

    NOTE: This only affects memory_store used by SSE.
    File persistence is not deleted to keep audit trail for school project.
    """

    device_store.store.clear()
    device_store.meta.clear()

    return {"status": "success", "cleared": True}

