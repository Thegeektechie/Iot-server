from pydantic import BaseModel
from typing import Optional

class SensorPayload(BaseModel):
    device_id: str
    data: str   # encrypted JSON string
    timestamp: Optional[str] = None