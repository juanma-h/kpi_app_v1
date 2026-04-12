from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums import NoveltyLogType, NoveltyPriority, NoveltyStatus, UserRole

NoveltyExtraData = dict[str, str | int | float | bool | None]


class UserSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    role: UserRole


class AllowlistDomainSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    domain: str
    description: str | None = None
    is_active: bool


class OperationalAreaCreate(BaseModel):
    code: str = Field(min_length=2, max_length=40)
    name: str = Field(min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=255)
    is_active: bool = True


class OperationalAreaStatusUpdate(BaseModel):
    is_active: bool


class OperationalAreaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    description: str | None = None
    is_active: bool
    created_by_user_id: int | None = None
    created_at: datetime
    updated_at: datetime


class SourceSystemCreate(BaseModel):
    code: str = Field(min_length=2, max_length=40)
    name: str = Field(min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=255)
    allowlist_domain_id: int | None = None
    is_active: bool = True


class SourceSystemStatusUpdate(BaseModel):
    is_active: bool


class SourceSystemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    description: str | None = None
    allowlist_domain_id: int | None = None
    is_active: bool
    created_by_user_id: int | None = None
    created_at: datetime
    updated_at: datetime
    allowlist_domain: AllowlistDomainSummaryResponse | None = None


class OperationalAreaSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    is_active: bool


class SourceSystemSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    is_active: bool
    allowlist_domain: AllowlistDomainSummaryResponse | None = None


class NoveltyCreate(BaseModel):
    area_id: int
    source_system_id: int
    assigned_user_id: int | None = None
    external_reference: str | None = Field(default=None, max_length=120)
    order_reference: str | None = Field(default=None, max_length=120)
    customer_reference: str | None = Field(default=None, max_length=120)
    title: str = Field(min_length=5, max_length=160)
    description: str = Field(min_length=10, max_length=4000)
    novelty_type: str = Field(min_length=2, max_length=80)
    priority: NoveltyPriority = NoveltyPriority.MEDIUM
    reported_at: datetime | None = None
    extra_data: NoveltyExtraData | None = None


class NoveltyUpdate(BaseModel):
    area_id: int | None = None
    source_system_id: int | None = None
    external_reference: str | None = Field(default=None, max_length=120)
    order_reference: str | None = Field(default=None, max_length=120)
    customer_reference: str | None = Field(default=None, max_length=120)
    title: str | None = Field(default=None, min_length=5, max_length=160)
    description: str | None = Field(default=None, min_length=10, max_length=4000)
    novelty_type: str | None = Field(default=None, min_length=2, max_length=80)
    priority: NoveltyPriority | None = None
    extra_data: NoveltyExtraData | None = None


class NoveltyAssignmentUpdate(BaseModel):
    assigned_user_id: int | None = None
    note: str | None = Field(default=None, max_length=1000)


class NoveltyStatusUpdate(BaseModel):
    status: NoveltyStatus
    note: str | None = Field(default=None, max_length=1000)


class NoveltyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    area_id: int
    source_system_id: int
    reported_by_user_id: int
    assigned_user_id: int | None = None
    reported_shift_id: int | None = None
    reported_session_id: int | None = None
    external_reference: str | None = None
    order_reference: str | None = None
    customer_reference: str | None = None
    title: str
    description: str
    novelty_type: str
    priority: NoveltyPriority
    status: NoveltyStatus
    extra_data: NoveltyExtraData | None = None
    reported_at: datetime
    first_action_at: datetime | None = None
    resolved_at: datetime | None = None
    closed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    area: OperationalAreaSummaryResponse
    source_system: SourceSystemSummaryResponse
    reported_by: UserSummaryResponse
    assigned_user: UserSummaryResponse | None = None


class NoveltyLogCreate(BaseModel):
    work_date: date | None = None
    log_type: NoveltyLogType = NoveltyLogType.DAILY_UPDATE
    content: str = Field(min_length=5, max_length=4000)
    worked_minutes: int | None = Field(default=None, ge=1, le=720)
    status_after: NoveltyStatus | None = None


class NoveltyLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    novelty_id: int
    author_user_id: int
    shift_id: int | None = None
    session_id: int | None = None
    work_date: date
    log_type: NoveltyLogType
    content: str
    worked_minutes: int | None = None
    status_after: NoveltyStatus | None = None
    logged_at: datetime
    author: UserSummaryResponse


class NoveltyKpiBreakdownResponse(BaseModel):
    key: str
    label: str
    count: int


class NoveltyKpiOverviewResponse(BaseModel):
    user_id: int | None = None
    user_name: str | None = None
    user_email: str | None = None
    user_role: UserRole | None = None
    total_novelties: int
    open_count: int
    in_progress_count: int
    blocked_count: int
    resolved_count: int
    closed_count: int
    backlog_count: int
    assigned_count: int
    unassigned_count: int
    log_entry_count: int
    logged_novelty_count: int
    total_logged_minutes: int
    average_logged_minutes_per_novelty: float
    average_time_to_first_action_minutes: float
    average_resolution_minutes: float
    first_reported_at: datetime | None = None
    last_reported_at: datetime | None = None
    priorities: list[NoveltyKpiBreakdownResponse]
    statuses: list[NoveltyKpiBreakdownResponse]
    areas: list[NoveltyKpiBreakdownResponse]
    source_systems: list[NoveltyKpiBreakdownResponse]
    novelty_types: list[NoveltyKpiBreakdownResponse]
