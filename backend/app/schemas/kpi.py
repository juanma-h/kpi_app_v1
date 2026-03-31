from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.domain.enums import ActivityEventType, ShiftStatus, UserRole


class KpiDomainBreakdownResponse(BaseModel):
    source_domain: str
    event_count: int
    page_view_count: int
    heartbeat_count: int
    idle_event_count: int
    active_seconds: int
    idle_seconds: int


class KpiEventTypeBreakdownResponse(BaseModel):
    event_type: ActivityEventType
    count: int
    tracked_seconds: int


class OperationalKpiOverviewResponse(BaseModel):
    user_id: int | None = None
    user_name: str | None = None
    user_email: str | None = None
    user_role: UserRole | None = None
    shift_count: int
    closed_shift_count: int
    open_shift_count: int
    session_count: int
    open_session_count: int
    total_shift_seconds: int
    total_session_seconds: int
    total_active_seconds: int
    total_idle_seconds: int
    total_tracked_seconds: int
    total_untracked_session_seconds: int
    activity_coverage_rate: float
    active_rate: float
    idle_rate: float
    event_count: int
    page_view_count: int
    heartbeat_count: int
    idle_event_count: int
    resume_count: int
    distinct_domain_count: int
    first_activity_at: datetime | None = None
    last_activity_at: datetime | None = None
    punctuality_supported: bool
    punctuality_reason: str | None = None
    scheduled_shift_count: int
    punctuality_evaluated_shift_count: int
    punctual_shift_count: int
    late_shift_count: int
    unscheduled_shift_count: int
    punctuality_rate: float
    average_late_by_minutes: float
    max_late_by_minutes: int
    average_start_delay_minutes: float
    max_start_delay_minutes: int
    domains: list[KpiDomainBreakdownResponse]
    event_types: list[KpiEventTypeBreakdownResponse]


class ShiftKpiResponse(OperationalKpiOverviewResponse):
    shift_id: int
    shift_status: ShiftStatus
    shift_started_at: datetime
    shift_ended_at: datetime | None = None
    device_labels: list[str]
    is_scheduled: bool
    is_punctual: bool | None = None
    late_by_minutes: int | None = None
    start_delay_minutes: int | None = None
    scheduled_start_at: datetime | None = None
    scheduled_end_at: datetime | None = None
    grace_deadline_at: datetime | None = None
    schedule_template_id: int | None = None
    schedule_template_name: str | None = None
    schedule_timezone_name: str | None = None
