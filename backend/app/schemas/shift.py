from datetime import datetime
from pydantic import BaseModel


class ShiftStartRequest(BaseModel):
    device_label: str | None = None


class ShiftResponse(BaseModel):
    shift_id: int
    session_id: int
    status: str
    start_at: datetime
    end_at: datetime | None = None
