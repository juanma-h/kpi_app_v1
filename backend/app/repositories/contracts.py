from __future__ import annotations

from datetime import datetime
from typing import Any, Protocol, Sequence

from app.models.activity_event import ActivityEvent
from app.models.allowlist_domain import AllowlistDomain
from app.models.session import Session as WorkSession
from app.models.shift import Shift
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
