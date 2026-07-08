import unittest
from datetime import datetime, timedelta, timezone

from tests.bootstrap import configure_test_environment

configure_test_environment()

from app.core.exceptions import ConflictError, ValidationError
from app.domain.enums import ActivityEventType, SessionStatus, ShiftStatus
from app.models.activity_event import ActivityEvent
from app.models.allowlist_domain import AllowlistDomain
from app.models.session import Session as WorkSession
from app.models.shift import Shift
from app.services.activity_events import ActivityEventService


class FakeActivityEventRepository:
    def __init__(self, events: list[ActivityEvent] | None = None):
        self.events = events or []
        self.commits = 0
        self._next_id = max((event.id for event in self.events), default=0) + 1

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
        events = list(self.events)
        if user_id is not None:
            events = [event for event in events if event.user_id == user_id]
        if shift_id is not None:
            events = [event for event in events if event.shift_id == shift_id]
        if session_id is not None:
            events = [event for event in events if event.session_id == session_id]
        if allowlist_domain_id is not None:
            events = [event for event in events if event.allowlist_domain_id == allowlist_domain_id]
        if event_type is not None:
            events = [event for event in events if event.event_type == event_type]
        if occurred_from is not None:
            events = [event for event in events if event.occurred_at >= occurred_from]
        if occurred_to is not None:
            events = [event for event in events if event.occurred_at <= occurred_to]
        return sorted(events, key=lambda event: (event.occurred_at, event.id), reverse=True)[:limit]

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
        event_data: dict[str, str | int | float | bool | None] | None,
    ) -> ActivityEvent:
        event = ActivityEvent(
            id=self._next_id,
            user_id=user_id,
            shift_id=shift_id,
            session_id=session_id,
            allowlist_domain_id=allowlist_domain_id,
            event_type=event_type,
            source_url=source_url,
            source_domain=source_domain,
            page_title=page_title,
            occurred_at=occurred_at,
            recorded_at=datetime.now(timezone.utc),
            duration_seconds=duration_seconds,
            event_data=event_data,
        )
        self._next_id += 1
        self.events.append(event)
        return event

    def commit(self) -> None:
        self.commits += 1

    def refresh(self, instance: object) -> None:
        return None


class FakeShiftWorkRepository:
    def __init__(self, shift: Shift | None = None, session: WorkSession | None = None):
        self.shift = shift
        self.session = session

    def get_open_shift_for_user(self, user_id: int) -> Shift | None:
        if self.shift and self.shift.user_id == user_id and self.shift.status == ShiftStatus.OPEN.value:
            return self.shift
        return None

    def get_open_session_for_shift(self, shift_id: int) -> WorkSession | None:
        if self.session and self.session.shift_id == shift_id and self.session.status == SessionStatus.OPEN.value:
            return self.session
        return None


class FakeAllowlistRepository:
    def __init__(self, entries: list[AllowlistDomain]):
        self.entries = entries

    def list_all(self) -> list[AllowlistDomain]:
        return list(self.entries)


def build_shift(*, shift_id: int, user_id: int) -> Shift:
    return Shift(
        id=shift_id,
        user_id=user_id,
        start_at=datetime.now(timezone.utc),
        status=ShiftStatus.OPEN.value,
    )


def build_session(*, session_id: int, user_id: int, shift_id: int) -> WorkSession:
    return WorkSession(
        id=session_id,
        user_id=user_id,
        shift_id=shift_id,
        start_at=datetime.now(timezone.utc),
        status=SessionStatus.OPEN.value,
        device_label="PC-01",
    )


def build_allowlist_domain(*, domain_id: int, domain: str, is_active: bool = True) -> AllowlistDomain:
    now = datetime.now(timezone.utc)
    return AllowlistDomain(
        id=domain_id,
        domain=domain,
        description=None,
        is_active=is_active,
        created_by_user_id=1,
        created_at=now,
        updated_at=now,
    )


class ActivityEventServiceTests(unittest.TestCase):
    def test_register_event_links_current_shift_session_and_allowlist(self) -> None:
        repository = FakeActivityEventRepository()
        service = ActivityEventService(
            activity_event_repository=repository,
            shift_work_repository=FakeShiftWorkRepository(
                shift=build_shift(shift_id=11, user_id=7),
                session=build_session(session_id=31, user_id=7, shift_id=11),
            ),
            allowlist_repository=FakeAllowlistRepository(
                [build_allowlist_domain(domain_id=5, domain="example.com")]
            ),
        )

        event = service.register_event(
            user_id=7,
            event_type=ActivityEventType.PAGE_VIEW,
            source_url="https://portal.example.com/reportes",
            page_title="  Reporte diario  ",
            occurred_at=datetime.now(timezone.utc) - timedelta(minutes=1),
            duration_seconds=None,
            event_data={"section": "daily"},
        )

        self.assertEqual(event.user_id, 7)
        self.assertEqual(event.shift_id, 11)
        self.assertEqual(event.session_id, 31)
        self.assertEqual(event.allowlist_domain_id, 5)
        self.assertEqual(event.source_domain, "portal.example.com")
        self.assertEqual(event.page_title, "Reporte diario")
        self.assertEqual(repository.commits, 1)

    def test_register_event_requires_open_shift(self) -> None:
        service = ActivityEventService(
            activity_event_repository=FakeActivityEventRepository(),
            shift_work_repository=FakeShiftWorkRepository(),
            allowlist_repository=FakeAllowlistRepository(
                [build_allowlist_domain(domain_id=5, domain="example.com")]
            ),
        )

        with self.assertRaisesRegex(ConflictError, "turno activo"):
            service.register_event(
                user_id=7,
                event_type=ActivityEventType.PAGE_VIEW,
                source_url="https://example.com/home",
                page_title=None,
                occurred_at=datetime.now(timezone.utc),
                duration_seconds=None,
                event_data=None,
            )

    def test_register_event_rejects_domain_outside_allowlist(self) -> None:
        service = ActivityEventService(
            activity_event_repository=FakeActivityEventRepository(),
            shift_work_repository=FakeShiftWorkRepository(
                shift=build_shift(shift_id=11, user_id=7),
                session=build_session(session_id=31, user_id=7, shift_id=11),
            ),
            allowlist_repository=FakeAllowlistRepository(
                [build_allowlist_domain(domain_id=5, domain="example.com", is_active=False)]
            ),
        )

        with self.assertRaisesRegex(ValidationError, "allowlist"):
            service.register_event(
                user_id=7,
                event_type=ActivityEventType.PAGE_VIEW,
                source_url="https://portal.example.com/reportes",
                page_title=None,
                occurred_at=datetime.now(timezone.utc),
                duration_seconds=None,
                event_data=None,
            )

    def test_register_event_requires_duration_for_heartbeat(self) -> None:
        service = ActivityEventService(
            activity_event_repository=FakeActivityEventRepository(),
            shift_work_repository=FakeShiftWorkRepository(
                shift=build_shift(shift_id=11, user_id=7),
                session=build_session(session_id=31, user_id=7, shift_id=11),
            ),
            allowlist_repository=FakeAllowlistRepository(
                [build_allowlist_domain(domain_id=5, domain="example.com")]
            ),
        )

        with self.assertRaisesRegex(ValidationError, "duration_seconds"):
            service.register_event(
                user_id=7,
                event_type=ActivityEventType.HEARTBEAT,
                source_url="https://example.com/home",
                page_title=None,
                occurred_at=datetime.now(timezone.utc),
                duration_seconds=None,
                event_data=None,
            )

    def test_list_events_supports_basic_filters(self) -> None:
        now = datetime.now(timezone.utc)
        repository = FakeActivityEventRepository(
            events=[
                ActivityEvent(
                    id=1,
                    user_id=7,
                    shift_id=11,
                    session_id=31,
                    allowlist_domain_id=5,
                    event_type=ActivityEventType.PAGE_VIEW.value,
                    source_url="https://example.com/home",
                    source_domain="example.com",
                    page_title="Home",
                    occurred_at=now,
                    recorded_at=now,
                    duration_seconds=None,
                    event_data=None,
                ),
                ActivityEvent(
                    id=2,
                    user_id=8,
                    shift_id=12,
                    session_id=32,
                    allowlist_domain_id=5,
                    event_type=ActivityEventType.HEARTBEAT.value,
                    source_url="https://example.com/dashboard",
                    source_domain="example.com",
                    page_title="Dashboard",
                    occurred_at=now - timedelta(minutes=5),
                    recorded_at=now,
                    duration_seconds=60,
                    event_data=None,
                ),
            ]
        )
        service = ActivityEventService(
            activity_event_repository=repository,
            shift_work_repository=FakeShiftWorkRepository(),
            allowlist_repository=FakeAllowlistRepository([]),
        )

        events = service.list_events(
            user_id=7,
            event_type=ActivityEventType.PAGE_VIEW,
            limit=10,
        )

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].id, 1)


if __name__ == "__main__":
    unittest.main()
