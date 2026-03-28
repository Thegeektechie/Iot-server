from pydantic import BaseModel
from typing import Dict, Optional


class SensorPayload(BaseModel):
    device_id: str
    timestamp: int
    data: Dict[str, Optional[str]]