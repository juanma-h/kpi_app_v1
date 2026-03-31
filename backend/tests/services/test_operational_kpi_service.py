import unittest
from datetime import datetime, timedelta, timezone

from bootstrap import configure_test_environment

configure_test_environment()

from app.core.exceptions import NotFoundError, ValidationError
from app.domain.enums import ActivityEventType, SessionStatus, ShiftStatus, UserRole
from app.models.activity_event import ActivityEvent
from app.models.session import Session as WorkSession
from app.models.shift import Shift
from app.models.user import User
from app.services.operational_kpis import OperationalKpiService


def build_user(*, user_id: int, role: UserRole = UserRole.EMPLOYEE) -> User:
    return User(
        id=user_id,
        name=f"User {user_id}",
        email=f"user{user_id}@kpi.com",
        password_hash="hashed",
        role=role.value,
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )


class FakeOperationalKpiRepository:
    def __init__(
        self,
        *,
        users: list[User] | None = None,
        shifts: list[Shift] | None = None,
        sessions: list[WorkSession] | None = None,
        events: list[ActivityEvent] | None = None,
    ):
        self.users = users or []
        self.shifts = shifts or []
        self.sessions = sessions or []
        self.events = events or []

    def get_user_by_id(self, user_id: int) -> User | None:
        return next((user for user in self.users if user.id == user_id), None)

    def get_shift_by_id(self, shift_id: int) -> Shift | None:
        return next((shift for shift in self.shifts if shift.id == shift_id), None)

    def list_shifts(
        self,
        *,
        user_id: int | None = None,
        started_from: datetime | None = None,
        started_to: datetime | None = None,
        limit: int = 200,
    ) -> list[Shift]:
        shifts = list(self.shifts)
        if user_id is not None:
            shifts = [shift for shift in shifts if shift.user_id == user_id]
        if started_from is not None:
            shifts = [shift for shift in shifts if shift.start_at >= started_from]
        if started_to is not None:
            shifts = [shift for shift in shifts if shift.start_at <= started_to]
        return sorted(shifts, key=lambda shift: (shift.start_at, shift.id), reverse=True)[:limit]

    def list_sessions(
        self,
        *,
        user_id: int | None = None,
        shift_ids: list[int] | None = None,
    ) -> list[WorkSession]:
        sessions = list(self.sessions)
        if user_id is not None:
            sessions = [session for session in sessions if session.user_id == user_id]
        if shift_ids is not None:
            sessions = [session for session in sessions if session.shift_id in shift_ids]
        return sessions

    def list_events(
        self,
        *,
        user_id: int | None = None,
        shift_ids: list[int] | None = None,
    ) -> list[ActivityEvent]:
        events = list(self.events)
        if user_id is not None:
            events = [event for event in events if event.user_id == user_id]
        if shift_ids is not None:
            events = [event for event in events if event.shift_id in shift_ids]
        return events


class OperationalKpiServiceTests(unittest.TestCase):
    def test_get_user_overview_calculates_operational_metrics(self) -> None:
        start_at = datetime(2026, 3, 31, 10, 0, tzinfo=timezone.utc)
        end_at = start_at + timedelta(minutes=10)
        repository = FakeOperationalKpiRepository(
            users=[build_user(user_id=7)],
            shifts=[
                Shift(
                    id=11,
                    user_id=7,
                    start_at=start_at,
                    end_at=end_at,
                    status=ShiftStatus.CLOSED.value,
                )
            ],
            sessions=[
                WorkSession(
                    id=31,
                    user_id=7,
                    shift_id=11,
                    start_at=start_at,
                    end_at=end_at,
                    status=SessionStatus.CLOSED.value,
                    device_label="PC-01",
                )
            ],
            events=[
                ActivityEvent(
                    id=1,
                    user_id=7,
                    shift_id=11,
                    session_id=31,
                    allowlist_domain_id=5,
                    event_type=ActivityEventType.PAGE_VIEW.value,
                    source_url="https://portal.example.com/home",
                    source_domain="portal.example.com",
                    page_title="Home",
                    occurred_at=start_at,
                    recorded_at=start_at,
                    duration_seconds=None,
                    event_data=None,
                ),
                ActivityEvent(
                    id=2,
                    user_id=7,
                    shift_id=11,
                    session_id=31,
                    allowlist_domain_id=5,
                    event_type=ActivityEventType.HEARTBEAT.value,
                    source_url="https://portal.example.com/home",
                    source_domain="portal.example.com",
                    page_title="Home",
                    occurred_at=start_at + timedelta(minutes=2),
                    recorded_at=start_at + timedelta(minutes=2),
                    duration_seconds=120,
                    event_data=None,
                ),
                ActivityEvent(
                    id=3,
                    user_id=7,
                    shift_id=11,
                    session_id=31,
                    allowlist_domain_id=5,
                    event_type=ActivityEventType.HEARTBEAT.value,
                    source_url="https://portal.example.com/home",
                    source_domain="portal.example.com",
                    page_title="Home",
                    occurred_at=start_at + timedelta(minutes=5),
                    recorded_at=start_at + timedelta(minutes=5),
                    duration_seconds=180,
                    event_data=None,
                ),
                ActivityEvent(
                    id=4,
                    user_id=7,
                    shift_id=11,
                    session_id=31,
                    allowlist_domain_id=5,
                    event_type=ActivityEventType.IDLE.value,
                    source_url="https://portal.example.com/home",
                    source_domain="portal.example.com",
                    page_title="Home",
                    occurred_at=start_at + timedelta(minutes=8),
                    recorded_at=start_at + timedelta(minutes=8),
                    duration_seconds=60,
                    event_data=None,
                ),
                ActivityEvent(
                    id=5,
                    user_id=7,
                    shift_id=11,
                    session_id=31,
                    allowlist_domain_id=5,
                    event_type=ActivityEventType.RESUME.value,
                    source_url="https://portal.example.com/home",
                    source_domain="portal.example.com",
                    page_title="Home",
                    occurred_at=start_at + timedelta(minutes=9),
                    recorded_at=start_at + timedelta(minutes=9),
                    duration_seconds=None,
                    event_data=None,
                ),
            ],
        )
        service = OperationalKpiService(operational_kpi_repository=repository)

        summary = service.get_user_overview(user_id=7)

        self.assertEqual(summary["shift_count"], 1)
        self.assertEqual(summary["session_count"], 1)
        self.assertEqual(summary["event_count"], 5)
        self.assertEqual(summary["page_view_count"], 1)
        self.assertEqual(summary["heartbeat_count"], 2)
        self.assertEqual(summary["idle_event_count"], 1)
        self.assertEqual(summary["resume_count"], 1)
        self.assertEqual(summary["total_shift_seconds"], 600)
        self.assertEqual(summary["total_session_seconds"], 600)
        self.assertEqual(summary["total_active_seconds"], 300)
        self.assertEqual(summary["total_idle_seconds"], 60)
        self.assertEqual(summary["total_tracked_seconds"], 360)
        self.assertEqual(summary["total_untracked_session_seconds"], 240)
        self.assertAlmostEqual(summary["activity_coverage_rate"], 0.6)
        self.assertAlmostEqual(summary["active_rate"], 0.8333, places=4)
        self.assertEqual(summary["distinct_domain_count"], 1)
        self.assertEqual(summary["domains"][0]["source_domain"], "portal.example.com")
        self.assertEqual(summary["domains"][0]["active_seconds"], 300)
        self.assertFalse(summary["punctuality_supported"])

    def test_get_shift_overview_includes_device_labels(self) -> None:
        start_at = datetime(2026, 3, 31, 10, 0, tzinfo=timezone.utc)
        repository = FakeOperationalKpiRepository(
            users=[build_user(user_id=7)],
            shifts=[
                Shift(
                    id=11,
                    user_id=7,
                    start_at=start_at,
                    end_at=None,
                    status=ShiftStatus.OPEN.value,
                )
            ],
            sessions=[
                WorkSession(
                    id=31,
                    user_id=7,
                    shift_id=11,
                    start_at=start_at,
                    end_at=None,
                    status=SessionStatus.OPEN.value,
                    device_label="PC-01",
                ),
                WorkSession(
                    id=32,
                    user_id=7,
                    shift_id=11,
                    start_at=start_at + timedelta(minutes=1),
                    end_at=None,
                    status=SessionStatus.OPEN.value,
                    device_label="PC-02",
                ),
            ],
        )
        service = OperationalKpiService(operational_kpi_repository=repository)

        summary = service.get_shift_overview(shift_id=11)

        self.assertEqual(summary["shift_id"], 11)
        self.assertEqual(summary["shift_status"], ShiftStatus.OPEN.value)
        self.assertEqual(summary["device_labels"], ["PC-01", "PC-02"])

    def test_get_user_overview_rejects_invalid_date_range(self) -> None:
        repository = FakeOperationalKpiRepository(users=[build_user(user_id=7)])
        service = OperationalKpiService(operational_kpi_repository=repository)

        with self.assertRaisesRegex(ValidationError, "rango"):
            service.get_user_overview(
                user_id=7,
                started_from=datetime(2026, 3, 31, 12, 0, tzinfo=timezone.utc),
                started_to=datetime(2026, 3, 31, 10, 0, tzinfo=timezone.utc),
            )

    def test_get_shift_overview_requires_existing_shift(self) -> None:
        service = OperationalKpiService(operational_kpi_repository=FakeOperationalKpiRepository())

        with self.assertRaisesRegex(NotFoundError, "turno solicitado"):
            service.get_shift_overview(shift_id=999)


if __name__ == "__main__":
    unittest.main()
