from __future__ import annotations

from datetime import datetime
from typing import Any, Protocol, Sequence

from app.models.allowlist_domain import AllowlistDomain
from app.models.session import Session as WorkSession
from app.models.shift import Shift
from app.models.user import User


class UserRepositoryProtocol(Protocol):
    def get_by_id(self, user_id: int) -> User | None: ...

    def get_by_email(self, email: str) -> User | None: ...


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
