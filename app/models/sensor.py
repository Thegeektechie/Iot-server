from pydantic import BaseModel
from typing import Optional, Union, Any

class SensorPayload(BaseModel):
    device_id: str
    data: Union[str, dict[str, Any]]  # encrypted str or plain dict (TEMP)
    timestamp: Optional[str] = None
