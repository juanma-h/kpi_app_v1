from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums import ActivityEventType

ActivityEventData = dict[str, str | int | float | bool | None]


class ActivityEventCreate(BaseModel):
    event_type: ActivityEventType
    source_url: str = Field(min_length=10, max_length=2048)
    page_title: str | None = Field(default=None, max_length=255)
    occurred_at: datetime | None = None
    duration_seconds: int | None = Field(default=None, ge=1, le=3600)
    event_data: ActivityEventData | None = None


class ActivityEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    shift_id: int
    session_id: int
    allowlist_domain_id: int
    event_type: ActivityEventType
    source_url: str
    source_domain: str
    page_title: str | None = None
    occurred_at: datetime
    recorded_at: datetime
    duration_seconds: int | None = None
    event_data: ActivityEventData | None = None
