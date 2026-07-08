from __future__ import annotations

from datetime import date, datetime, time
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.domain.enums import Weekday
from app.domain.schedule_resolution import resolve_schedule_for_date
from app.models.schedule_template import ScheduleTemplate
from app.models.user_schedule_assignment import UserScheduleAssignment
from app.repositories.contracts import ScheduleRepositoryProtocol


class ScheduleService:
    def __init__(self, schedule_repository: ScheduleRepositoryProtocol):
        self.schedule_repository = schedule_repository

    def list_templates(self, *, is_active: bool | None = None) -> list[ScheduleTemplate]:
        return list(self.schedule_repository.list_templates(is_active=is_active))

    def get_template(self, *, template_id: int) -> ScheduleTemplate:
        template = self.schedule_repository.get_template_by_id(template_id)
        if not template:
            raise NotFoundError("La plantilla de horario solicitada no existe.")
        return template

    def create_template(
        self,
        *,
        name: str,
        description: str | None,
        timezone_name: str,
        grace_minutes: int,
        slots: list[dict],
        created_by_user_id: int | None,
        is_active: bool = True,
    ) -> ScheduleTemplate:
        normalized_name = self._normalize_name(name)
        normalized_timezone = self._normalize_timezone(timezone_name)
        normalized_description = self._normalize_description(description)
        normalized_grace = self._normalize_grace_minutes(grace_minutes)
        normalized_slots = self._normalize_slots(slots)

        existing = self.schedule_repository.get_template_by_name(normalized_name)
        if existing:
            raise ConflictError("Ya existe una plantilla de horario con ese nombre.")

        template = self.schedule_repository.create_template(
            name=normalized_name,
            description=normalized_description,
            timezone_name=normalized_timezone,
            grace_minutes=normalized_grace,
            is_active=is_active,
            created_by_user_id=created_by_user_id,
        )
        self.schedule_repository.replace_template_slots(template=template, slots=normalized_slots)
        self.schedule_repository.commit()
        self.schedule_repository.refresh(template)
        return self.get_template(template_id=template.id)

    def update_template(
        self,
        *,
        template_id: int,
        name: str | None = None,
        description: str | None = None,
        timezone_name: str | None = None,
        grace_minutes: int | None = None,
        slots: list[dict] | None = None,
    ) -> ScheduleTemplate:
        template = self.get_template(template_id=template_id)
        if all(value is None for value in (name, description, timezone_name, grace_minutes, slots)):
            raise ValidationError("No se enviaron cambios para actualizar la plantilla de horario.")

        if name is not None:
            normalized_name = self._normalize_name(name)
            existing = self.schedule_repository.get_template_by_name(normalized_name)
            if existing and existing.id != template.id:
                raise ConflictError("Ya existe una plantilla de horario con ese nombre.")
            template.name = normalized_name

        if description is not None:
            template.description = self._normalize_description(description)

        if timezone_name is not None:
            template.timezone_name = self._normalize_timezone(timezone_name)

        if grace_minutes is not None:
            template.grace_minutes = self._normalize_grace_minutes(grace_minutes)

        if slots is not None:
            self.schedule_repository.replace_template_slots(
                template=template,
                slots=self._normalize_slots(slots),
            )

        self.schedule_repository.commit()
        self.schedule_repository.refresh(template)
        return self.get_template(template_id=template.id)

    def set_template_status(self, *, template_id: int, is_active: bool) -> ScheduleTemplate:
        template = self.get_template(template_id=template_id)
        template.is_active = is_active
        self.schedule_repository.commit()
        self.schedule_repository.refresh(template)
        return self.get_template(template_id=template.id)

    def list_assignments(
        self,
        *,
        user_id: int | None = None,
        is_active: bool | None = None,
    ) -> list[UserScheduleAssignment]:
        return list(self.schedule_repository.list_assignments(user_id=user_id, is_active=is_active))

    def create_assignment(
        self,
        *,
        user_id: int,
        schedule_template_id: int,
        effective_from: date,
        effective_to: date | None,
        notes: str | None,
        assigned_by_user_id: int | None,
        is_active: bool = True,
    ) -> UserScheduleAssignment:
        user = self.schedule_repository.get_user_by_id(user_id)
        if not user:
            raise NotFoundError("El usuario solicitado no existe.")

        template = self.get_template(template_id=schedule_template_id)
        if not template.is_active and is_active:
            raise ValidationError("No puedes asignar una plantilla de horario inactiva.")

        if effective_to is not None and effective_to < effective_from:
            raise ValidationError("La fecha final de la asignacion no puede ser menor que la inicial.")

        normalized_notes = self._normalize_description(notes)

        for assignment in self.schedule_repository.list_assignments(user_id=user_id, is_active=True):
            if self._ranges_overlap(
                effective_from,
                effective_to,
                assignment.effective_from,
                assignment.effective_to,
            ):
                raise ConflictError("Ya existe una asignacion activa que se cruza con el rango indicado.")

        assignment = self.schedule_repository.create_assignment(
            user_id=user_id,
            schedule_template_id=schedule_template_id,
            effective_from=effective_from,
            effective_to=effective_to,
            is_active=is_active,
            notes=normalized_notes,
            assigned_by_user_id=assigned_by_user_id,
        )
        self.schedule_repository.commit()
        self.schedule_repository.refresh(assignment)
        return assignment

    def resolve_schedule(self, *, user_id: int, target_date: date | None = None) -> dict:
        user = self.schedule_repository.get_user_by_id(user_id)
        if not user:
            raise NotFoundError("El usuario solicitado no existe.")

        resolved_date = target_date or datetime.utcnow().date()
        active_assignments = list(self.schedule_repository.list_assignments(user_id=user_id, is_active=True))
        return resolve_schedule_for_date(
            user_id=user.id,
            assignments=active_assignments,
            target_date=resolved_date,
        )

    @staticmethod
    def _normalize_name(name: str) -> str:
        normalized = name.strip()
        if not normalized:
            raise ValidationError("El nombre de la plantilla es obligatorio.")
        return normalized

    @staticmethod
    def _normalize_description(description: str | None) -> str | None:
        if description is None:
            return None
        normalized = description.strip()
        return normalized or None

    @staticmethod
    def _normalize_timezone(timezone_name: str) -> str:
        normalized = timezone_name.strip()
        if not normalized:
            raise ValidationError("La zona horaria es obligatoria.")
        try:
            ZoneInfo(normalized)
        except ZoneInfoNotFoundError:
            raise ValidationError("La zona horaria enviada no es valida.")
        return normalized

    @staticmethod
    def _normalize_grace_minutes(grace_minutes: int) -> int:
        if grace_minutes < 0 or grace_minutes > 180:
            raise ValidationError("El margen de tolerancia debe estar entre 0 y 180 minutos.")
        return grace_minutes

    def _normalize_slots(self, slots: list[dict]) -> list[dict]:
        if not slots:
            raise ValidationError("La plantilla debe definir al menos un horario por dia.")

        normalized_slots: list[dict] = []
        seen_weekdays: set[str] = set()
        for slot in slots:
            weekday = slot["weekday"]
            weekday_value = weekday.value if isinstance(weekday, Weekday) else str(weekday).upper()
            if weekday_value not in Weekday._value2member_map_:
                raise ValidationError("El dia de la semana enviado no es valido.")
            if weekday_value in seen_weekdays:
                raise ValidationError("No puedes repetir el mismo dia dentro de una plantilla.")

            start_time = slot["start_time"]
            end_time = slot["end_time"]
            if not isinstance(start_time, time) or not isinstance(end_time, time):
                raise ValidationError("Los horarios enviados no son validos.")
            if start_time == end_time:
                raise ValidationError("La hora de inicio y fin no pueden ser iguales.")

            seen_weekdays.add(weekday_value)
            normalized_slots.append(
                {
                    "weekday": weekday_value,
                    "start_time": start_time,
                    "end_time": end_time,
                }
            )

        return sorted(normalized_slots, key=lambda slot: list(Weekday).index(Weekday(slot["weekday"])))

    @staticmethod
    def _ranges_overlap(
        start_a: date,
        end_a: date | None,
        start_b: date,
        end_b: date | None,
    ) -> bool:
        final_a = end_a or date.max
        final_b = end_b or date.max
        return start_a <= final_b and start_b <= final_a
