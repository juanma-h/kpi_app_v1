from __future__ import annotations

from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums import Weekday


class ScheduleTemplateSlotCreate(BaseModel):
    weekday: Weekday
    start_time: time
    end_time: time


class ScheduleTemplateSlotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    weekday: Weekday
    start_time: time
    end_time: time


class ScheduleTemplateCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=255)
    timezone_name: str = Field(min_length=1, max_length=64)
    grace_minutes: int = Field(default=0, ge=0, le=180)
    is_active: bool = True
    slots: list[ScheduleTemplateSlotCreate]


class ScheduleTemplateUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=255)
    timezone_name: str | None = Field(default=None, min_length=1, max_length=64)
    grace_minutes: int | None = Field(default=None, ge=0, le=180)
    slots: list[ScheduleTemplateSlotCreate] | None = None


class ScheduleTemplateStatusUpdate(BaseModel):
    is_active: bool


class ScheduleTemplateSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    timezone_name: str
    grace_minutes: int
    is_active: bool


class ScheduleTemplateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None
    timezone_name: str
    grace_minutes: int
    is_active: bool
    created_by_user_id: int | None = None
    created_at: datetime
    updated_at: datetime
    slots: list[ScheduleTemplateSlotResponse]


class ScheduleAssignmentCreate(BaseModel):
    user_id: int
    schedule_template_id: int
    effective_from: date
    effective_to: date | None = None
    is_active: bool = True
    notes: str | None = Field(default=None, max_length=255)


class ScheduleAssignmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    schedule_template_id: int
    effective_from: date
    effective_to: date | None = None
    is_active: bool
    notes: str | None = None
    assigned_by_user_id: int | None = None
    created_at: datetime
    updated_at: datetime
    schedule_template: ScheduleTemplateSummaryResponse


class ScheduleResolutionResponse(BaseModel):
    user_id: int
    target_date: date
    is_scheduled: bool
    resolution_reason: str | None = None
    assignment_id: int | None = None
    schedule_template_id: int | None = None
    schedule_template_name: str | None = None
    timezone_name: str | None = None
    weekday: Weekday
    expected_start_time: time | None = None
    expected_end_time: time | None = None
    expected_start_at: datetime | None = None
    expected_end_at: datetime | None = None
    grace_deadline_at: datetime | None = None
    grace_minutes: int | None = None
    effective_from: date | None = None
    effective_to: date | None = None
    notes: str | None = None
