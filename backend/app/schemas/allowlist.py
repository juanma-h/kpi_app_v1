from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AllowlistDomainCreate(BaseModel):
    domain: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


class AllowlistDomainStatusUpdate(BaseModel):
    is_active: bool


class AllowlistDomainResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    domain: str
    description: str | None = None
    is_active: bool
    created_by_user_id: int | None = None
    created_at: datetime
    updated_at: datetime
