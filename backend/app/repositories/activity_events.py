from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.models.activity_event import ActivityEvent
from app.repositories.contracts import ActivityEventRepositoryProtocol


class ActivityEventRepository(ActivityEventRepositoryProtocol):
    def __init__(self, db: Session):
        self.db = db

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
    ) -> list[ActivityEvent]:
        query = self.db.query(ActivityEvent)

        if user_id is not None:
            query = query.filter(ActivityEvent.user_id == user_id)
        if shift_id is not None:
            query = query.filter(ActivityEvent.shift_id == shift_id)
        if session_id is not None:
            query = query.filter(ActivityEvent.session_id == session_id)
        if allowlist_domain_id is not None:
            query = query.filter(ActivityEvent.allowlist_domain_id == allowlist_domain_id)
        if event_type is not None:
            query = query.filter(ActivityEvent.event_type == event_type)
        if occurred_from is not None:
            query = query.filter(ActivityEvent.occurred_at >= occurred_from)
        if occurred_to is not None:
            query = query.filter(ActivityEvent.occurred_at <= occurred_to)

        return (
            query.order_by(ActivityEvent.occurred_at.desc(), ActivityEvent.id.desc())
            .limit(limit)
            .all()
        )

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
        event_data: dict[str, object] | None,
    ) -> ActivityEvent:
        event = ActivityEvent(
            user_id=user_id,
            shift_id=shift_id,
            session_id=session_id,
            allowlist_domain_id=allowlist_domain_id,
            event_type=event_type,
            source_url=source_url,
            source_domain=source_domain,
            page_title=page_title,
            occurred_at=occurred_at,
            duration_seconds=duration_seconds,
            event_data=event_data,
        )
        self.db.add(event)
        return event

    def commit(self) -> None:
        self.db.commit()

    def refresh(self, instance: object) -> None:
        self.db.refresh(instance)
