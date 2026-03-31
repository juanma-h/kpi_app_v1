from __future__ import annotations

from datetime import date
from typing import Any, Sequence

from sqlalchemy.orm import Session, selectinload

from app.models.schedule_template import ScheduleTemplate
from app.models.schedule_template_slot import ScheduleTemplateSlot
from app.models.user import User
from app.models.user_schedule_assignment import UserScheduleAssignment
from app.repositories.contracts import ScheduleRepositoryProtocol


class ScheduleRepository(ScheduleRepositoryProtocol):
    def __init__(self, db: Session):
        self.db = db

    def list_templates(self, *, is_active: bool | None = None) -> list[ScheduleTemplate]:
        query = self.db.query(ScheduleTemplate).options(selectinload(ScheduleTemplate.slots))
        if is_active is not None:
            query = query.filter(ScheduleTemplate.is_active == is_active)
        return query.order_by(ScheduleTemplate.name.asc()).all()

    def get_template_by_id(self, template_id: int) -> ScheduleTemplate | None:
        return (
            self.db.query(ScheduleTemplate)
            .options(selectinload(ScheduleTemplate.slots))
            .filter(ScheduleTemplate.id == template_id)
            .first()
        )

    def get_template_by_name(self, name: str) -> ScheduleTemplate | None:
        return (
            self.db.query(ScheduleTemplate)
            .filter(ScheduleTemplate.name == name)
            .first()
        )

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
            name=name,
            description=description,
            timezone_name=timezone_name,
            grace_minutes=grace_minutes,
            is_active=is_active,
            created_by_user_id=created_by_user_id,
        )
        self.db.add(template)
        self.db.flush()
        return template

    def replace_template_slots(
        self,
        *,
        template: ScheduleTemplate,
        slots: Sequence[dict[str, Any]],
    ) -> None:
        template.slots = [
            ScheduleTemplateSlot(
                weekday=slot["weekday"],
                start_time=slot["start_time"],
                end_time=slot["end_time"],
            )
            for slot in slots
        ]

    def list_assignments(
        self,
        *,
        user_id: int | None = None,
        is_active: bool | None = None,
    ) -> list[UserScheduleAssignment]:
        query = self.db.query(UserScheduleAssignment).options(
            selectinload(UserScheduleAssignment.schedule_template).selectinload(ScheduleTemplate.slots)
        )
        if user_id is not None:
            query = query.filter(UserScheduleAssignment.user_id == user_id)
        if is_active is not None:
            query = query.filter(UserScheduleAssignment.is_active == is_active)
        return query.order_by(
            UserScheduleAssignment.effective_from.desc(),
            UserScheduleAssignment.id.desc(),
        ).all()

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
            user_id=user_id,
            schedule_template_id=schedule_template_id,
            effective_from=effective_from,
            effective_to=effective_to,
            is_active=is_active,
            notes=notes,
            assigned_by_user_id=assigned_by_user_id,
        )
        self.db.add(assignment)
        return assignment

    def get_user_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def commit(self) -> None:
        self.db.commit()

    def refresh(self, instance: object) -> None:
        self.db.refresh(instance)
