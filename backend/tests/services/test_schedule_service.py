import unittest
from datetime import date, datetime, time, timezone

from tests.bootstrap import configure_test_environment

configure_test_environment()

from app.core.exceptions import ConflictError, ValidationError
from app.domain.enums import Weekday
from app.models.schedule_template import ScheduleTemplate
from app.models.schedule_template_slot import ScheduleTemplateSlot
from app.models.user import User
from app.models.user_schedule_assignment import UserScheduleAssignment
from app.services.schedules import ScheduleService


def build_user(*, user_id: int) -> User:
    return User(
        id=user_id,
        name=f"User {user_id}",
        email=f"user{user_id}@kpi.com",
        password_hash="hashed",
        role="EMPLOYEE",
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )


class FakeScheduleRepository:
    def __init__(self):
        self.users = [build_user(user_id=1), build_user(user_id=2)]
        self.templates: list[ScheduleTemplate] = []
        self.assignments: list[UserScheduleAssignment] = []
        self.commits = 0
        self._template_id = 1
        self._slot_id = 1
        self._assignment_id = 1

    def list_templates(self, *, is_active: bool | None = None) -> list[ScheduleTemplate]:
        templates = list(self.templates)
        if is_active is not None:
            templates = [template for template in templates if template.is_active == is_active]
        return templates

    def get_template_by_id(self, template_id: int) -> ScheduleTemplate | None:
        return next((template for template in self.templates if template.id == template_id), None)

    def get_template_by_name(self, name: str) -> ScheduleTemplate | None:
        return next((template for template in self.templates if template.name == name), None)

    def create_template(
        self,
        *,
        name: str,
        description: str | None,
        timezone_name: str,
        grace_minutes: int,
        is_active: bool,
        created_by_user_id: int | None,
    ) -> ScheduleTemplate:
        template = ScheduleTemplate(
            id=self._template_id,
            name=name,
            description=description,
            timezone_name=timezone_name,
            grace_minutes=grace_minutes,
            is_active=is_active,
            created_by_user_id=created_by_user_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self._template_id += 1
        template.slots = []
        self.templates.append(template)
        return template

    def replace_template_slots(self, *, template: ScheduleTemplate, slots: list[dict]) -> None:
        template.slots = []
        for slot in slots:
            template.slots.append(
                ScheduleTemplateSlot(
                    id=self._slot_id,
                    schedule_template_id=template.id,
                    weekday=slot["weekday"],
                    start_time=slot["start_time"],
                    end_time=slot["end_time"],
                )
            )
            self._slot_id += 1

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
    ) -> UserScheduleAssignment:
        assignment = UserScheduleAssignment(
            id=self._assignment_id,
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
        self._assignment_id += 1
        assignment.schedule_template = self.get_template_by_id(schedule_template_id)
        self.assignments.append(assignment)
        return assignment

    def get_user_by_id(self, user_id: int) -> User | None:
        return next((user for user in self.users if user.id == user_id), None)

    def commit(self) -> None:
        self.commits += 1

    def refresh(self, instance: object) -> None:
        return None


class ScheduleServiceTests(unittest.TestCase):
    def test_create_template_rejects_duplicate_weekday(self) -> None:
        service = ScheduleService(schedule_repository=FakeScheduleRepository())

        with self.assertRaisesRegex(ValidationError, "mismo dia"):
            service.create_template(
                name="Horario oficina",
                description=None,
                timezone_name="America/Bogota",
                grace_minutes=10,
                slots=[
                    {"weekday": Weekday.MONDAY, "start_time": time(8, 0), "end_time": time(17, 0)},
                    {"weekday": Weekday.MONDAY, "start_time": time(9, 0), "end_time": time(18, 0)},
                ],
                created_by_user_id=1,
            )

    def test_create_assignment_rejects_overlapping_ranges(self) -> None:
        repository = FakeScheduleRepository()
        service = ScheduleService(schedule_repository=repository)
        template = service.create_template(
            name="Horario oficina",
            description=None,
            timezone_name="America/Bogota",
            grace_minutes=10,
            slots=[
                {"weekday": Weekday.MONDAY, "start_time": time(8, 0), "end_time": time(17, 0)},
            ],
            created_by_user_id=1,
        )
        service.create_assignment(
            user_id=2,
            schedule_template_id=template.id,
            effective_from=date(2026, 4, 1),
            effective_to=date(2026, 4, 30),
            notes=None,
            assigned_by_user_id=1,
        )

        with self.assertRaisesRegex(ConflictError, "cruza"):
            service.create_assignment(
                user_id=2,
                schedule_template_id=template.id,
                effective_from=date(2026, 4, 15),
                effective_to=date(2026, 5, 15),
                notes=None,
                assigned_by_user_id=1,
            )

    def test_resolve_schedule_supports_overnight_shift(self) -> None:
        repository = FakeScheduleRepository()
        service = ScheduleService(schedule_repository=repository)
        template = service.create_template(
            name="Horario nocturno",
            description="Turno de madrugada",
            timezone_name="America/Bogota",
            grace_minutes=15,
            slots=[
                {"weekday": Weekday.FRIDAY, "start_time": time(22, 0), "end_time": time(6, 0)},
            ],
            created_by_user_id=1,
        )
        service.create_assignment(
            user_id=2,
            schedule_template_id=template.id,
            effective_from=date(2026, 4, 1),
            effective_to=None,
            notes="Guardia nocturna",
            assigned_by_user_id=1,
        )

        resolution = service.resolve_schedule(user_id=2, target_date=date(2026, 4, 3))

        self.assertTrue(resolution["is_scheduled"])
        self.assertEqual(resolution["weekday"], Weekday.FRIDAY)
        self.assertEqual(resolution["expected_start_time"], time(22, 0))
        self.assertEqual(resolution["expected_end_time"], time(6, 0))
        self.assertEqual(resolution["expected_end_at"].date(), date(2026, 4, 4))
        self.assertEqual(resolution["grace_minutes"], 15)

    def test_resolve_schedule_returns_unscheduled_when_day_has_no_slot(self) -> None:
        repository = FakeScheduleRepository()
        service = ScheduleService(schedule_repository=repository)
        template = service.create_template(
            name="Horario lunes",
            description=None,
            timezone_name="America/Bogota",
            grace_minutes=10,
            slots=[
                {"weekday": Weekday.MONDAY, "start_time": time(8, 0), "end_time": time(17, 0)},
            ],
            created_by_user_id=1,
        )
        service.create_assignment(
            user_id=2,
            schedule_template_id=template.id,
            effective_from=date(2026, 4, 1),
            effective_to=None,
            notes=None,
            assigned_by_user_id=1,
        )

        resolution = service.resolve_schedule(user_id=2, target_date=date(2026, 4, 2))

        self.assertFalse(resolution["is_scheduled"])
        self.assertIn("no define horario", resolution["resolution_reason"])


if __name__ == "__main__":
    unittest.main()
