import unittest
from datetime import date, datetime, time, timedelta, timezone

from bootstrap import configure_test_environment

configure_test_environment()

from app.core.exceptions import NotFoundError, ValidationError
from app.domain.enums import ActivityEventType, SessionStatus, ShiftStatus, UserRole, Weekday
from app.models.activity_event import ActivityEvent
from app.models.schedule_template import ScheduleTemplate
from app.models.schedule_template_slot import ScheduleTemplateSlot
from app.models.session import Session as WorkSession
from app.models.shift import Shift
from app.models.user import User
from app.models.user_schedule_assignment import UserScheduleAssignment
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


class FakeScheduleRepository:
    def __init__(self, assignments: list[UserScheduleAssignment] | None = None):
        self.assignments = assignments or []

    def list_assignments(
        self,
        *,
        user_id: int | None = None,
        is_active: bool | None = None,
    ) -> list[UserScheduleAssignment]:
        assignments = list(self.assignments)
        if user_id is not None:
            assignments = [assignment for assignment in assignments if assignment.user_id == user_id]
        if is_active is not None:
            assignments = [assignment for assignment in assignments if assignment.is_active == is_active]
        return assignments


def build_assignment(
    *,
    assignment_id: int,
    user_id: int,
    effective_from: date,
    effective_to: date | None,
    weekday: Weekday,
    start_time: time,
    end_time: time,
    grace_minutes: int = 10,
) -> UserScheduleAssignment:
    now = datetime.now(timezone.utc)
    template = ScheduleTemplate(
        id=100 + assignment_id,
        name=f"Template {assignment_id}",
        description=None,
        timezone_name="America/Bogota",
        grace_minutes=grace_minutes,
        is_active=True,
        created_by_user_id=1,
        created_at=now,
        updated_at=now,
    )
    template.slots = [
        ScheduleTemplateSlot(
            id=200 + assignment_id,
            schedule_template_id=template.id,
            weekday=weekday.value,
            start_time=start_time,
            end_time=end_time,
        )
    ]
    assignment = UserScheduleAssignment(
        id=assignment_id,
        user_id=user_id,
        schedule_template_id=template.id,
        effective_from=effective_from,
        effective_to=effective_to,
        is_active=True,
        notes=None,
        assigned_by_user_id=1,
        created_at=now,
        updated_at=now,
    )
    assignment.schedule_template = template
    return assignment


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
        service = OperationalKpiService(
            operational_kpi_repository=repository,
            schedule_repository=FakeScheduleRepository(
                assignments=[
                    build_assignment(
                        assignment_id=1,
                        user_id=7,
                        effective_from=start_at.date(),
                        effective_to=None,
                        weekday=Weekday.TUESDAY,
                        start_time=datetime(2026, 3, 31, 4, 50, tzinfo=timezone.utc).time(),
                        end_time=datetime(2026, 3, 31, 13, 50, tzinfo=timezone.utc).time(),
                        grace_minutes=10,
                    )
                ]
            ),
        )

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
        self.assertTrue(summary["punctuality_supported"])
        self.assertEqual(summary["scheduled_shift_count"], 1)
        self.assertEqual(summary["punctual_shift_count"], 1)
        self.assertEqual(summary["late_shift_count"], 0)
        self.assertEqual(summary["unscheduled_shift_count"], 0)
        self.assertAlmostEqual(summary["punctuality_rate"], 1.0)

    def test_get_shift_overview_includes_device_labels(self) -> None:
        start_at = datetime(2026, 3, 31, 14, 30, tzinfo=timezone.utc)
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
        service = OperationalKpiService(
            operational_kpi_repository=repository,
            schedule_repository=FakeScheduleRepository(
                assignments=[
                    build_assignment(
                        assignment_id=1,
                        user_id=7,
                        effective_from=start_at.date(),
                        effective_to=None,
                        weekday=Weekday.TUESDAY,
                        start_time=datetime(2026, 3, 31, 8, 0, tzinfo=timezone.utc).time(),
                        end_time=datetime(2026, 3, 31, 17, 0, tzinfo=timezone.utc).time(),
                        grace_minutes=10,
                    )
                ]
            ),
        )

        summary = service.get_shift_overview(shift_id=11)

        self.assertEqual(summary["shift_id"], 11)
        self.assertEqual(summary["shift_status"], ShiftStatus.OPEN.value)
        self.assertEqual(summary["device_labels"], ["PC-01", "PC-02"])
        self.assertTrue(summary["is_scheduled"])
        self.assertFalse(summary["is_punctual"])
        self.assertEqual(summary["late_by_minutes"], 80)
        self.assertEqual(summary["schedule_template_name"], "Template 1")

    def test_get_user_overview_rejects_invalid_date_range(self) -> None:
        repository = FakeOperationalKpiRepository(users=[build_user(user_id=7)])
        service = OperationalKpiService(
            operational_kpi_repository=repository,
            schedule_repository=FakeScheduleRepository(),
        )

        with self.assertRaisesRegex(ValidationError, "rango"):
            service.get_user_overview(
                user_id=7,
                started_from=datetime(2026, 3, 31, 12, 0, tzinfo=timezone.utc),
                started_to=datetime(2026, 3, 31, 10, 0, tzinfo=timezone.utc),
            )

    def test_get_shift_overview_requires_existing_shift(self) -> None:
        service = OperationalKpiService(
            operational_kpi_repository=FakeOperationalKpiRepository(),
            schedule_repository=FakeScheduleRepository(),
        )

        with self.assertRaisesRegex(NotFoundError, "turno solicitado"):
            service.get_shift_overview(shift_id=999)

    def test_get_overview_counts_unscheduled_shifts(self) -> None:
        start_at = datetime(2026, 4, 1, 13, 0, tzinfo=timezone.utc)
        repository = FakeOperationalKpiRepository(
            users=[build_user(user_id=7)],
            shifts=[
                Shift(
                    id=11,
                    user_id=7,
                    start_at=start_at,
                    end_at=start_at + timedelta(hours=8),
                    status=ShiftStatus.CLOSED.value,
                )
            ],
        )
        service = OperationalKpiService(
            operational_kpi_repository=repository,
            schedule_repository=FakeScheduleRepository(),
        )

        summary = service.get_overview()

        self.assertEqual(summary["scheduled_shift_count"], 0)
        self.assertEqual(summary["unscheduled_shift_count"], 1)
        self.assertEqual(summary["punctuality_rate"], 0.0)


if __name__ == "__main__":
    unittest.main()
