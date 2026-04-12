from __future__ import annotations

from datetime import date, datetime
from typing import Any, Protocol, Sequence

from app.models.activity_event import ActivityEvent
from app.models.allowlist_domain import AllowlistDomain
from app.models.novelty import Novelty
from app.models.novelty_log import NoveltyLog
from app.models.operational_area import OperationalArea
from app.models.schedule_template import ScheduleTemplate
from app.models.schedule_template_slot import ScheduleTemplateSlot
from app.models.session import Session as WorkSession
from app.models.shift import Shift
from app.models.source_system import SourceSystem
from app.models.user_schedule_assignment import UserScheduleAssignment
from app.models.user import User


class UserRepositoryProtocol(Protocol):
    def list_all(
        self,
        *,
        is_active: bool | None = None,
        role: str | None = None,
    ) -> Sequence[User]: ...

    def get_by_id(self, user_id: int) -> User | None: ...

    def get_by_email(self, email: str) -> User | None: ...

    def create(
        self,
        *,
        name: str,
        email: str,
        password_hash: str,
        role: str,
        is_active: bool,
    ) -> User: ...

    def commit(self) -> None: ...

    def refresh(self, instance: Any) -> None: ...


class ShiftWorkRepositoryProtocol(Protocol):
    def get_open_shift_for_user(self, user_id: int) -> Shift | None: ...

    def get_open_session_for_shift(self, shift_id: int) -> WorkSession | None: ...

    def create_shift(self, *, user_id: int, start_at: datetime, status: str) -> Shift: ...

    def create_session(
        self,
        *,
        user_id: int,
        shift_id: int,
        start_at: datetime,
        status: str,
        device_label: str | None,
    ) -> WorkSession: ...

    def commit(self) -> None: ...

    def refresh(self, instance: Any) -> None: ...


class AllowlistDomainRepositoryProtocol(Protocol):
    def list_all(self) -> Sequence[AllowlistDomain]: ...

    def get_by_id(self, domain_id: int) -> AllowlistDomain | None: ...

    def get_by_domain(self, domain: str) -> AllowlistDomain | None: ...

    def create(
        self,
        *,
        domain: str,
        description: str | None,
        created_by_user_id: int | None,
    ) -> AllowlistDomain: ...

    def commit(self) -> None: ...

    def refresh(self, instance: Any) -> None: ...


class ActivityEventRepositoryProtocol(Protocol):
    def list_all(
        self,
        *,
        user_id: int | None = None,
        shift_id: int | None = None,
        session_id: int | None = None,
        allowlist_domain_id: int | None = None,
        event_type: str | None = None,
        occurred_from: datetime | None = None,
        occurred_to: datetime | None = None,
        limit: int = 100,
    ) -> Sequence[ActivityEvent]: ...

    def create(
        self,
        *,
        user_id: int,
        shift_id: int,
        session_id: int,
        allowlist_domain_id: int,
        event_type: str,
        source_url: str,
        source_domain: str,
        page_title: str | None,
        occurred_at: datetime,
        duration_seconds: int | None,
        event_data: dict[str, Any] | None,
    ) -> ActivityEvent: ...

    def commit(self) -> None: ...

    def refresh(self, instance: Any) -> None: ...


class OperationalKpiRepositoryProtocol(Protocol):
    def get_user_by_id(self, user_id: int) -> User | None: ...

    def get_shift_by_id(self, shift_id: int) -> Shift | None: ...

    def list_shifts(
        self,
        *,
        user_id: int | None = None,
        started_from: datetime | None = None,
        started_to: datetime | None = None,
        limit: int = 200,
    ) -> Sequence[Shift]: ...

    def list_sessions(
        self,
        *,
        user_id: int | None = None,
        shift_ids: Sequence[int] | None = None,
    ) -> Sequence[WorkSession]: ...

    def list_events(
        self,
        *,
        user_id: int | None = None,
        shift_ids: Sequence[int] | None = None,
    ) -> Sequence[ActivityEvent]: ...


class ScheduleRepositoryProtocol(Protocol):
    def list_templates(self, *, is_active: bool | None = None) -> Sequence[ScheduleTemplate]: ...

    def get_template_by_id(self, template_id: int) -> ScheduleTemplate | None: ...

    def get_template_by_name(self, name: str) -> ScheduleTemplate | None: ...

    def create_template(
        self,
        *,
        name: str,
        description: str | None,
        timezone_name: str,
        grace_minutes: int,
        is_active: bool,
        created_by_user_id: int | None,
    ) -> ScheduleTemplate: ...

    def replace_template_slots(
        self,
        *,
        template: ScheduleTemplate,
        slots: Sequence[dict[str, Any]],
    ) -> None: ...

    def list_assignments(
        self,
        *,
        user_id: int | None = None,
        is_active: bool | None = None,
    ) -> Sequence[UserScheduleAssignment]: ...

    def create_assignment(
        self,
        *,
        user_id: int,
        schedule_template_id: int,
        effective_from: date,
        effective_to: date | None,
        is_active: bool,
        notes: str | None,
        assigned_by_user_id: int | None,
    ) -> UserScheduleAssignment: ...

    def get_user_by_id(self, user_id: int) -> User | None: ...

    def commit(self) -> None: ...

    def refresh(self, instance: Any) -> None: ...


class NoveltyRepositoryProtocol(Protocol):
    def list_areas(self, *, is_active: bool | None = None) -> Sequence[OperationalArea]: ...

    def get_area_by_id(self, area_id: int) -> OperationalArea | None: ...

    def get_area_by_code(self, code: str) -> OperationalArea | None: ...

    def get_area_by_name(self, name: str) -> OperationalArea | None: ...

    def create_area(
        self,
        *,
        code: str,
        name: str,
        description: str | None,
        is_active: bool,
        created_by_user_id: int | None,
    ) -> OperationalArea: ...

    def list_source_systems(self, *, is_active: bool | None = None) -> Sequence[SourceSystem]: ...

    def get_source_system_by_id(self, source_system_id: int) -> SourceSystem | None: ...

    def get_source_system_by_code(self, code: str) -> SourceSystem | None: ...

    def get_source_system_by_name(self, name: str) -> SourceSystem | None: ...

    def create_source_system(
        self,
        *,
        code: str,
        name: str,
        description: str | None,
        allowlist_domain_id: int | None,
        is_active: bool,
        created_by_user_id: int | None,
    ) -> SourceSystem: ...

    def get_allowlist_domain_by_id(self, allowlist_domain_id: int) -> AllowlistDomain | None: ...

    def list_novelties(
        self,
        *,
        involved_user_id: int | None = None,
        area_id: int | None = None,
        source_system_id: int | None = None,
        assigned_user_id: int | None = None,
        reported_by_user_id: int | None = None,
        status: str | None = None,
        priority: str | None = None,
        novelty_type: str | None = None,
        reported_from: datetime | None = None,
        reported_to: datetime | None = None,
        limit: int | None = 200,
    ) -> Sequence[Novelty]: ...

    def get_novelty_by_id(self, novelty_id: int) -> Novelty | None: ...

    def create_novelty(
        self,
        *,
        area_id: int,
        source_system_id: int,
        reported_by_user_id: int,
        assigned_user_id: int | None,
        reported_shift_id: int | None,
        reported_session_id: int | None,
        external_reference: str | None,
        order_reference: str | None,
        customer_reference: str | None,
        title: str,
        description: str,
        novelty_type: str,
        priority: str,
        status: str,
        extra_data: dict[str, Any] | None,
        reported_at: datetime,
    ) -> Novelty: ...

    def list_logs(self, *, novelty_id: int) -> Sequence[NoveltyLog]: ...

    def list_logs_for_novelties(self, *, novelty_ids: Sequence[int]) -> Sequence[NoveltyLog]: ...

    def get_log_by_id(self, log_id: int) -> NoveltyLog | None: ...

    def create_log(
        self,
        *,
        novelty_id: int,
        author_user_id: int,
        shift_id: int | None,
        session_id: int | None,
        work_date: date,
        log_type: str,
        content: str,
        worked_minutes: int | None,
        status_after: str | None,
        logged_at: datetime,
    ) -> NoveltyLog: ...

    def get_user_by_id(self, user_id: int) -> User | None: ...

    def commit(self) -> None: ...

    def refresh(self, instance: Any) -> None: ...
