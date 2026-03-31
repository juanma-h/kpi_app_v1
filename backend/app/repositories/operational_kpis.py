from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.activity_event import ActivityEvent
from app.models.session import Session as WorkSession
from app.models.shift import Shift
from app.models.user import User
from app.repositories.contracts import OperationalKpiRepositoryProtocol


class OperationalKpiRepository(OperationalKpiRepositoryProtocol):
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_shift_by_id(self, shift_id: int) -> Shift | None:
        return self.db.get(Shift, shift_id)

    def list_shifts(
        self,
        *,
        user_id: int | None = None,
        started_from: datetime | None = None,
        started_to: datetime | None = None,
        limit: int = 200,
    ) -> list[Shift]:
        query = self.db.query(Shift)

        if user_id is not None:
            query = query.filter(Shift.user_id == user_id)
        if started_from is not None:
            query = query.filter(Shift.start_at >= started_from)
        if started_to is not None:
            query = query.filter(Shift.start_at <= started_to)

        return query.order_by(Shift.start_at.desc(), Shift.id.desc()).limit(limit).all()

    def list_sessions(
        self,
        *,
        user_id: int | None = None,
        shift_ids: Sequence[int] | None = None,
    ) -> list[WorkSession]:
        query = self.db.query(WorkSession)

        if user_id is not None:
            query = query.filter(WorkSession.user_id == user_id)
        if shift_ids is not None:
            if not shift_ids:
                return []
            query = query.filter(WorkSession.shift_id.in_(shift_ids))

        return query.order_by(WorkSession.start_at.desc(), WorkSession.id.desc()).all()

    def list_events(
        self,
        *,
        user_id: int | None = None,
        shift_ids: Sequence[int] | None = None,
    ) -> list[ActivityEvent]:
        query = self.db.query(ActivityEvent)

        if user_id is not None:
            query = query.filter(ActivityEvent.user_id == user_id)
        if shift_ids is not None:
            if not shift_ids:
                return []
            query = query.filter(ActivityEvent.shift_id.in_(shift_ids))

        return query.order_by(ActivityEvent.occurred_at.desc(), ActivityEvent.id.desc()).all()
