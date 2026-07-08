from datetime import date, datetime, time, timezone
import unittest

from tests.bootstrap import configure_test_environment

configure_test_environment()

from fastapi.testclient import TestClient

from app.core.deps import get_current_user, get_schedule_service
from app.domain.enums import UserRole, Weekday
from app.main import app
from app.models.schedule_template import ScheduleTemplate
from app.models.schedule_template_slot import ScheduleTemplateSlot
from app.models.user import User
from app.models.user_schedule_assignment import UserScheduleAssignment


def build_user(
    *,
    user_id: int,
    email: str,
    role: UserRole,
    is_active: bool = True,
) -> User:
    return User(
        id=user_id,
        name=f"User {user_id}",
        email=email,
        password_hash="hashed",
        role=role.value,
        is_active=is_active,
        created_at=datetime.now(timezone.utc),
    )


class FakeScheduleService:
    def __init__(self):
        now = datetime.now(timezone.utc)
        template = ScheduleTemplate(
            id=1,
            name="Horario oficina",
            description="Lunes a viernes",
            timezone_name="America/Bogota",
            grace_minutes=10,
            is_active=True,
            created_by_user_id=1,
            created_at=now,
            updated_at=now,
        )
        template.slots = [
            ScheduleTemplateSlot(
                id=1,
                schedule_template_id=1,
                weekday=Weekday.MONDAY.value,
                start_time=time(8, 0),
                end_time=time(17, 0),
            )
        ]
        self.template = template

    def list_templates(self, *, is_active=None):
        return [self.template]

    def get_template(self, *, template_id: int):
        return self.template

    def create_template(self, *, name, description, timezone_name, grace_minutes, slots, created_by_user_id, is_active=True):
        template = self.template
        template.name = name
        template.description = description
        template.timezone_name = timezone_name
        template.grace_minutes = grace_minutes
        template.is_active = is_active
        template.created_by_user_id = created_by_user_id
        template.slots = [
            ScheduleTemplateSlot(
                id=index + 1,
                schedule_template_id=template.id,
                weekday=slot["weekday"].value if hasattr(slot["weekday"], "value") else slot["weekday"],
                start_time=slot["start_time"],
                end_time=slot["end_time"],
            )
            for index, slot in enumerate(slots)
        ]
        return template

    def update_template(self, *, template_id, name=None, description=None, timezone_name=None, grace_minutes=None, slots=None):
        return self.template

    def set_template_status(self, *, template_id: int, is_active: bool):
        self.template.is_active = is_active
        return self.template

    def list_assignments(self, *, user_id=None, is_active=None):
        assignment = UserScheduleAssignment(
            id=1,
            user_id=2,
            schedule_template_id=1,
            effective_from=date(2026, 4, 1),
            effective_to=None,
            is_active=True,
            notes=None,
            assigned_by_user_id=1,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        assignment.schedule_template = self.template
        return [assignment]

    def create_assignment(self, *, user_id, schedule_template_id, effective_from, effective_to, notes, assigned_by_user_id, is_active=True):
        assignment = UserScheduleAssignment(
            id=2,
            user_id=user_id,
            schedule_template_id=schedule_template_id,
            effective_from=effective_from,
            effective_to=effective_to,
            is_active=is_active,
            notes=notes,
            assigned_by_user_id=assigned_by_user_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        assignment.schedule_template = self.template
        return assignment

    def resolve_schedule(self, *, user_id: int, target_date: date | None = None):
        return {
            "user_id": user_id,
            "target_date": target_date or date(2026, 4, 1),
            "is_scheduled": True,
            "resolution_reason": None,
            "assignment_id": 1,
            "schedule_template_id": 1,
            "schedule_template_name": "Horario oficina",
            "timezone_name": "America/Bogota",
            "weekday": Weekday.WEDNESDAY,
            "expected_start_time": time(8, 0),
            "expected_end_time": time(17, 0),
            "expected_start_at": datetime(2026, 4, 1, 8, 0, tzinfo=timezone.utc),
            "expected_end_at": datetime(2026, 4, 1, 17, 0, tzinfo=timezone.utc),
            "grace_deadline_at": datetime(2026, 4, 1, 8, 10, tzinfo=timezone.utc),
            "grace_minutes": 10,
            "effective_from": date(2026, 4, 1),
            "effective_to": None,
            "notes": None,
        }


class SchedulesApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.schedule_service = FakeScheduleService()

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    def test_admin_can_create_schedule_template(self) -> None:
        app.dependency_overrides[get_current_user] = lambda: build_user(
            user_id=1,
            email="admin@kpi.com",
            role=UserRole.ADMIN,
        )
        app.dependency_overrides[get_schedule_service] = lambda: self.schedule_service

        response = self.client.post(
            "/schedules/templates",
            json={
                "name": "Horario oficina",
                "description": "Lunes a viernes",
                "timezone_name": "America/Bogota",
                "grace_minutes": 10,
                "is_active": True,
                "slots": [
                    {
                        "weekday": "MONDAY",
                        "start_time": "08:00:00",
                        "end_time": "17:00:00",
                    }
                ],
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["name"], "Horario oficina")
        self.assertEqual(len(response.json()["slots"]), 1)

    def test_supervisor_cannot_create_schedule_template(self) -> None:
        app.dependency_overrides[get_current_user] = lambda: build_user(
            user_id=10,
            email="supervisor@kpi.com",
            role=UserRole.SUPERVISOR,
        )
        app.dependency_overrides[get_schedule_service] = lambda: self.schedule_service

        response = self.client.post(
            "/schedules/templates",
            json={
                "name": "Horario oficina",
                "description": "Lunes a viernes",
                "timezone_name": "America/Bogota",
                "grace_minutes": 10,
                "is_active": True,
                "slots": [
                    {
                        "weekday": "MONDAY",
                        "start_time": "08:00:00",
                        "end_time": "17:00:00",
                    }
                ],
            },
        )

        self.assertEqual(response.status_code, 403)

    def test_employee_can_get_own_resolved_schedule(self) -> None:
        app.dependency_overrides[get_current_user] = lambda: build_user(
            user_id=2,
            email="employee@kpi.com",
            role=UserRole.EMPLOYEE,
        )
        app.dependency_overrides[get_schedule_service] = lambda: self.schedule_service

        response = self.client.get("/schedules/me/resolved?target_date=2026-04-01")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["user_id"], 2)
        self.assertTrue(response.json()["is_scheduled"])

    def test_supervisor_can_get_user_resolved_schedule(self) -> None:
        app.dependency_overrides[get_current_user] = lambda: build_user(
            user_id=10,
            email="supervisor@kpi.com",
            role=UserRole.SUPERVISOR,
        )
        app.dependency_overrides[get_schedule_service] = lambda: self.schedule_service

        response = self.client.get("/schedules/users/2/resolved?target_date=2026-04-01")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["user_id"], 2)
        self.assertEqual(response.json()["schedule_template_name"], "Horario oficina")

    def test_admin_can_create_schedule_assignment(self) -> None:
        app.dependency_overrides[get_current_user] = lambda: build_user(
            user_id=1,
            email="admin@kpi.com",
            role=UserRole.ADMIN,
        )
        app.dependency_overrides[get_schedule_service] = lambda: self.schedule_service

        response = self.client.post(
            "/schedules/assignments",
            json={
                "user_id": 2,
                "schedule_template_id": 1,
                "effective_from": "2026-04-01",
                "effective_to": None,
                "is_active": True,
                "notes": "Asignacion inicial",
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["user_id"], 2)
        self.assertEqual(response.json()["schedule_template"]["id"], 1)


if __name__ == "__main__":
    unittest.main()
