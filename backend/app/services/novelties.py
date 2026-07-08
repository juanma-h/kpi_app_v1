from __future__ import annotations

import re
from datetime import date, datetime, timedelta, timezone

from app.core.exceptions import (
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)
from app.domain.enums import NoveltyLogType, NoveltyPriority, NoveltyStatus, UserRole
from app.models.novelty import Novelty
from app.models.novelty_log import NoveltyLog
from app.models.operational_area import OperationalArea
from app.models.source_system import SourceSystem
from app.models.user import User
from app.repositories.contracts import NoveltyRepositoryProtocol, ShiftWorkRepositoryProtocol


class NoveltyService:
    MAX_FUTURE_DRIFT_MINUTES = 5

    def __init__(
        self,
        *,
        novelty_repository: NoveltyRepositoryProtocol,
        shift_work_repository: ShiftWorkRepositoryProtocol,
    ):
        self.novelty_repository = novelty_repository
        self.shift_work_repository = shift_work_repository

    def list_areas(self, *, is_active: bool | None = None) -> list[OperationalArea]:
        return list(self.novelty_repository.list_areas(is_active=is_active))

    def create_area(
        self,
        *,
        code: str,
        name: str,
        description: str | None,
        is_active: bool,
        created_by_user_id: int | None,
    ) -> OperationalArea:
        normalized_code = self._normalize_code(code)
        normalized_name = self._normalize_name(name, field_name="El nombre del area")
        normalized_description = self._normalize_optional_text(description, max_length=255)

        if self.novelty_repository.get_area_by_code(normalized_code):
            raise ConflictError("Ya existe un area operativa con ese codigo.")
        if self.novelty_repository.get_area_by_name(normalized_name):
            raise ConflictError("Ya existe un area operativa con ese nombre.")

        area = self.novelty_repository.create_area(
            code=normalized_code,
            name=normalized_name,
            description=normalized_description,
            is_active=is_active,
            created_by_user_id=created_by_user_id,
        )
        self.novelty_repository.commit()
        self.novelty_repository.refresh(area)
        return area

    def set_area_status(self, *, area_id: int, is_active: bool) -> OperationalArea:
        area = self.get_area(area_id=area_id)
        area.is_active = is_active
        self.novelty_repository.commit()
        self.novelty_repository.refresh(area)
        return area

    def get_area(self, *, area_id: int) -> OperationalArea:
        area = self.novelty_repository.get_area_by_id(area_id)
        if not area:
            raise NotFoundError("El area operativa solicitada no existe.")
        return area

    def list_source_systems(self, *, is_active: bool | None = None) -> list[SourceSystem]:
        return list(self.novelty_repository.list_source_systems(is_active=is_active))

    def create_source_system(
        self,
        *,
        code: str,
        name: str,
        description: str | None,
        allowlist_domain_id: int | None,
        is_active: bool,
        created_by_user_id: int | None,
    ) -> SourceSystem:
        normalized_code = self._normalize_code(code)
        normalized_name = self._normalize_name(name, field_name="El nombre del sistema fuente")
        normalized_description = self._normalize_optional_text(description, max_length=255)

        if self.novelty_repository.get_source_system_by_code(normalized_code):
            raise ConflictError("Ya existe un sistema fuente con ese codigo.")
        if self.novelty_repository.get_source_system_by_name(normalized_name):
            raise ConflictError("Ya existe un sistema fuente con ese nombre.")

        if allowlist_domain_id is not None:
            domain = self.novelty_repository.get_allowlist_domain_by_id(allowlist_domain_id)
            if not domain:
                raise NotFoundError("El dominio de allowlist solicitado no existe.")
            if not domain.is_active:
                raise ValidationError("Solo puedes vincular dominios activos al sistema fuente.")

        source_system = self.novelty_repository.create_source_system(
            code=normalized_code,
            name=normalized_name,
            description=normalized_description,
            allowlist_domain_id=allowlist_domain_id,
            is_active=is_active,
            created_by_user_id=created_by_user_id,
        )
        self.novelty_repository.commit()
        self.novelty_repository.refresh(source_system)
        return self.get_source_system(source_system_id=source_system.id)

    def set_source_system_status(self, *, source_system_id: int, is_active: bool) -> SourceSystem:
        source_system = self.get_source_system(source_system_id=source_system_id)
        source_system.is_active = is_active
        self.novelty_repository.commit()
        self.novelty_repository.refresh(source_system)
        return self.get_source_system(source_system_id=source_system.id)

    def get_source_system(self, *, source_system_id: int) -> SourceSystem:
        source_system = self.novelty_repository.get_source_system_by_id(source_system_id)
        if not source_system:
            raise NotFoundError("El sistema fuente solicitado no existe.")
        return source_system

    def list_novelties(
        self,
        *,
        area_id: int | None = None,
        source_system_id: int | None = None,
        assigned_user_id: int | None = None,
        reported_by_user_id: int | None = None,
        status: NoveltyStatus | None = None,
        priority: NoveltyPriority | None = None,
        novelty_type: str | None = None,
        reported_from: datetime | None = None,
        reported_to: datetime | None = None,
        limit: int = 200,
    ) -> list[Novelty]:
        normalized_range = self._normalize_reported_range(reported_from, reported_to)
        normalized_limit = self._normalize_limit(limit)
        normalized_type = self._normalize_optional_text(novelty_type, max_length=80)
        return list(
            self.novelty_repository.list_novelties(
                area_id=area_id,
                source_system_id=source_system_id,
                assigned_user_id=assigned_user_id,
                reported_by_user_id=reported_by_user_id,
                status=status.value if status else None,
                priority=priority.value if priority else None,
                novelty_type=normalized_type,
                reported_from=normalized_range[0],
                reported_to=normalized_range[1],
                limit=normalized_limit,
            )
        )

    def list_my_novelties(
        self,
        *,
        current_user: User,
        status: NoveltyStatus | None = None,
        priority: NoveltyPriority | None = None,
        area_id: int | None = None,
        source_system_id: int | None = None,
        novelty_type: str | None = None,
        reported_from: datetime | None = None,
        reported_to: datetime | None = None,
        limit: int = 200,
    ) -> list[Novelty]:
        normalized_range = self._normalize_reported_range(reported_from, reported_to)
        normalized_limit = self._normalize_limit(limit)
        normalized_type = self._normalize_optional_text(novelty_type, max_length=80)
        return list(
            self.novelty_repository.list_novelties(
                involved_user_id=current_user.id,
                area_id=area_id,
                source_system_id=source_system_id,
                status=status.value if status else None,
                priority=priority.value if priority else None,
                novelty_type=normalized_type,
                reported_from=normalized_range[0],
                reported_to=normalized_range[1],
                limit=normalized_limit,
            )
        )

    def get_novelty(self, *, novelty_id: int, actor: User) -> Novelty:
        novelty = self.novelty_repository.get_novelty_by_id(novelty_id)
        if not novelty:
            raise NotFoundError("La novedad solicitada no existe.")
        self._ensure_access(novelty=novelty, actor=actor)
        return novelty

    def create_novelty(
        self,
        *,
        actor: User,
        area_id: int,
        source_system_id: int,
        assigned_user_id: int | None,
        external_reference: str | None,
        order_reference: str | None,
        customer_reference: str | None,
        title: str,
        description: str,
        novelty_type: str,
        priority: NoveltyPriority,
        reported_at: datetime | None,
        extra_data: dict[str, str | int | float | bool | None] | None,
    ) -> Novelty:
        area = self.get_area(area_id=area_id)
        if not area.is_active:
            raise ValidationError("No puedes registrar novedades sobre un area inactiva.")

        source_system = self.get_source_system(source_system_id=source_system_id)
        if not source_system.is_active:
            raise ValidationError("No puedes registrar novedades sobre un sistema fuente inactivo.")

        normalized_assigned_user_id = self._resolve_assigned_user_id(
            actor=actor,
            assigned_user_id=assigned_user_id,
        )
        normalized_reported_at = self._normalize_reported_at(reported_at)
        normalized_title = self._normalize_name(title, field_name="El titulo")
        normalized_description = self._normalize_required_text(description, field_name="La descripcion")
        normalized_type = self._normalize_name(novelty_type, field_name="El tipo de novedad")
        normalized_external_reference = self._normalize_optional_text(external_reference, max_length=120)
        normalized_order_reference = self._normalize_optional_text(order_reference, max_length=120)
        normalized_customer_reference = self._normalize_optional_text(customer_reference, max_length=120)
        normalized_extra_data = dict(extra_data) if extra_data else None

        open_shift = self.shift_work_repository.get_open_shift_for_user(actor.id)
        open_session = (
            self.shift_work_repository.get_open_session_for_shift(open_shift.id) if open_shift else None
        )

        novelty = self.novelty_repository.create_novelty(
            area_id=area.id,
            source_system_id=source_system.id,
            reported_by_user_id=actor.id,
            assigned_user_id=normalized_assigned_user_id,
            reported_shift_id=open_shift.id if open_shift else None,
            reported_session_id=open_session.id if open_session else None,
            external_reference=normalized_external_reference,
            order_reference=normalized_order_reference,
            customer_reference=normalized_customer_reference,
            title=normalized_title,
            description=normalized_description,
            novelty_type=normalized_type,
            priority=priority.value,
            status=NoveltyStatus.OPEN.value,
            extra_data=normalized_extra_data,
            reported_at=normalized_reported_at,
        )
        self.novelty_repository.commit()
        return self._get_persisted_novelty(novelty.id)

    def update_novelty(
        self,
        *,
        novelty_id: int,
        actor: User,
        area_id: int | None = None,
        source_system_id: int | None = None,
        external_reference: str | None = None,
        order_reference: str | None = None,
        customer_reference: str | None = None,
        title: str | None = None,
        description: str | None = None,
        novelty_type: str | None = None,
        priority: NoveltyPriority | None = None,
        extra_data: dict[str, str | int | float | bool | None] | None = None,
    ) -> Novelty:
        self._ensure_manager(actor)
        novelty = self.get_novelty(novelty_id=novelty_id, actor=actor)

        if all(
            value is None
            for value in (
                area_id,
                source_system_id,
                external_reference,
                order_reference,
                customer_reference,
                title,
                description,
                novelty_type,
                priority,
                extra_data,
            )
        ):
            raise ValidationError("No se enviaron cambios para actualizar la novedad.")

        if area_id is not None:
            area = self.get_area(area_id=area_id)
            if not area.is_active:
                raise ValidationError("No puedes mover la novedad a un area inactiva.")
            novelty.area_id = area.id

        if source_system_id is not None:
            source_system = self.get_source_system(source_system_id=source_system_id)
            if not source_system.is_active:
                raise ValidationError("No puedes mover la novedad a un sistema fuente inactivo.")
            novelty.source_system_id = source_system.id

        if external_reference is not None:
            novelty.external_reference = self._normalize_optional_text(external_reference, max_length=120)
        if order_reference is not None:
            novelty.order_reference = self._normalize_optional_text(order_reference, max_length=120)
        if customer_reference is not None:
            novelty.customer_reference = self._normalize_optional_text(customer_reference, max_length=120)
        if title is not None:
            novelty.title = self._normalize_name(title, field_name="El titulo")
        if description is not None:
            novelty.description = self._normalize_required_text(description, field_name="La descripcion")
        if novelty_type is not None:
            novelty.novelty_type = self._normalize_name(novelty_type, field_name="El tipo de novedad")
        if priority is not None:
            novelty.priority = priority.value
        if extra_data is not None:
            novelty.extra_data = dict(extra_data)

        self.novelty_repository.commit()
        return self._get_persisted_novelty(novelty.id)

    def assign_novelty(
        self,
        *,
        novelty_id: int,
        actor: User,
        assigned_user_id: int | None,
        note: str | None,
    ) -> Novelty:
        self._ensure_manager(actor)
        novelty = self.get_novelty(novelty_id=novelty_id, actor=actor)

        normalized_assigned_user_id = None
        assigned_label = "sin asignacion"
        if assigned_user_id is not None:
            assigned_user = self.novelty_repository.get_user_by_id(assigned_user_id)
            if not assigned_user:
                raise NotFoundError("El usuario asignado no existe.")
            if not assigned_user.is_active:
                raise ValidationError("No puedes asignar novedades a usuarios inactivos.")
            normalized_assigned_user_id = assigned_user.id
            assigned_label = assigned_user.name

        novelty.assigned_user_id = normalized_assigned_user_id
        logged_at = datetime.now(timezone.utc)
        content = self._normalize_optional_text(note, max_length=1000) or f"Asignacion actualizada a {assigned_label}."
        self._ensure_first_action(novelty=novelty, action_at=logged_at)
        self.novelty_repository.create_log(
            novelty_id=novelty.id,
            author_user_id=actor.id,
            shift_id=None,
            session_id=None,
            work_date=logged_at.date(),
            log_type=NoveltyLogType.ASSIGNMENT.value,
            content=content,
            worked_minutes=None,
            status_after=novelty.status,
            logged_at=logged_at,
        )
        self.novelty_repository.commit()
        return self._get_persisted_novelty(novelty.id)

    def set_novelty_status(
        self,
        *,
        novelty_id: int,
        actor: User,
        status: NoveltyStatus,
        note: str | None,
    ) -> Novelty:
        novelty = self.get_novelty(novelty_id=novelty_id, actor=actor)
        logged_at = datetime.now(timezone.utc)
        self._apply_status(novelty=novelty, next_status=status, changed_at=logged_at)
        self._ensure_first_action(novelty=novelty, action_at=logged_at)
        content = self._normalize_optional_text(note, max_length=1000) or f"Estado cambiado a {status.value}."
        self.novelty_repository.create_log(
            novelty_id=novelty.id,
            author_user_id=actor.id,
            shift_id=None,
            session_id=None,
            work_date=logged_at.date(),
            log_type=NoveltyLogType.STATUS_CHANGE.value,
            content=content,
            worked_minutes=None,
            status_after=status.value,
            logged_at=logged_at,
        )
        self.novelty_repository.commit()
        return self._get_persisted_novelty(novelty.id)

    def list_logs(self, *, novelty_id: int, actor: User) -> list[NoveltyLog]:
        novelty = self.get_novelty(novelty_id=novelty_id, actor=actor)
        return list(self.novelty_repository.list_logs(novelty_id=novelty.id))

    def create_log(
        self,
        *,
        novelty_id: int,
        actor: User,
        work_date: date | None,
        log_type: NoveltyLogType,
        content: str,
        worked_minutes: int | None,
        status_after: NoveltyStatus | None,
    ) -> NoveltyLog:
        novelty = self.get_novelty(novelty_id=novelty_id, actor=actor)
        logged_at = datetime.now(timezone.utc)
        open_shift = self.shift_work_repository.get_open_shift_for_user(actor.id)
        open_session = (
            self.shift_work_repository.get_open_session_for_shift(open_shift.id) if open_shift else None
        )

        normalized_content = self._normalize_required_text(content, field_name="El contenido de la bitacora")
        normalized_work_date = work_date or logged_at.date()
        if worked_minutes is not None and worked_minutes < 1:
            raise ValidationError("El tiempo trabajado debe ser mayor a cero.")

        if status_after is not None:
            self._apply_status(novelty=novelty, next_status=status_after, changed_at=logged_at)
        self._ensure_first_action(novelty=novelty, action_at=logged_at)

        log = self.novelty_repository.create_log(
            novelty_id=novelty.id,
            author_user_id=actor.id,
            shift_id=open_shift.id if open_shift else None,
            session_id=open_session.id if open_session else None,
            work_date=normalized_work_date,
            log_type=log_type.value,
            content=normalized_content,
            worked_minutes=worked_minutes,
            status_after=status_after.value if status_after else novelty.status,
            logged_at=logged_at,
        )
        self.novelty_repository.commit()
        return self._get_persisted_log(log.id)

    def _resolve_assigned_user_id(self, *, actor: User, assigned_user_id: int | None) -> int | None:
        resolved_user_id = assigned_user_id
        if resolved_user_id is None and actor.role == UserRole.EMPLOYEE.value:
            resolved_user_id = actor.id
        if resolved_user_id is None:
            return None

        assigned_user = self.novelty_repository.get_user_by_id(resolved_user_id)
        if not assigned_user:
            raise NotFoundError("El usuario asignado no existe.")
        if not assigned_user.is_active:
            raise ValidationError("No puedes asignar novedades a usuarios inactivos.")
        return assigned_user.id

    def _ensure_access(self, *, novelty: Novelty, actor: User) -> None:
        if actor.role in {UserRole.ADMIN.value, UserRole.SUPERVISOR.value}:
            return
        if novelty.reported_by_user_id == actor.id:
            return
        if novelty.assigned_user_id == actor.id:
            return
        raise PermissionDeniedError("No tienes permisos para acceder a esta novedad.")

    @staticmethod
    def _ensure_manager(actor: User) -> None:
        if actor.role not in {UserRole.ADMIN.value, UserRole.SUPERVISOR.value}:
            raise PermissionDeniedError("No tienes permisos para administrar esta novedad.")

    @staticmethod
    def _normalize_code(code: str) -> str:
        normalized = code.strip().upper().replace("-", "_").replace(" ", "_")
        if not re.fullmatch(r"[A-Z0-9_]{2,40}", normalized):
            raise ValidationError("El codigo enviado no es valido.")
        return normalized

    @staticmethod
    def _normalize_name(name: str, *, field_name: str) -> str:
        normalized = name.strip()
        if not normalized:
            raise ValidationError(f"{field_name} es obligatorio.")
        return normalized

    @staticmethod
    def _normalize_required_text(value: str, *, field_name: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValidationError(f"{field_name} es obligatoria.")
        return normalized

    @staticmethod
    def _normalize_optional_text(value: str | None, *, max_length: int) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            return None
        if len(normalized) > max_length:
            raise ValidationError("El texto enviado excede la longitud permitida.")
        return normalized

    @classmethod
    def _normalize_reported_at(cls, reported_at: datetime | None) -> datetime:
        if reported_at is None:
            return datetime.now(timezone.utc)
        if reported_at.tzinfo is None:
            raise ValidationError("La fecha reported_at debe incluir zona horaria.")
        normalized = reported_at.astimezone(timezone.utc)
        if normalized > datetime.now(timezone.utc) + timedelta(minutes=cls.MAX_FUTURE_DRIFT_MINUTES):
            raise ValidationError("La novedad no puede registrarse con una fecha futura invalida.")
        return normalized

    def _normalize_reported_range(
        self,
        reported_from: datetime | None,
        reported_to: datetime | None,
    ) -> tuple[datetime | None, datetime | None]:
        normalized_from = self._normalize_range_datetime(reported_from)
        normalized_to = self._normalize_range_datetime(reported_to)
        if normalized_from and normalized_to and normalized_from > normalized_to:
            raise ValidationError("El rango de fechas enviado no es valido.")
        return normalized_from, normalized_to

    @staticmethod
    def _normalize_range_datetime(value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            raise ValidationError("Los filtros de fecha deben incluir zona horaria.")
        return value.astimezone(timezone.utc)

    @staticmethod
    def _normalize_limit(limit: int) -> int:
        if limit < 1 or limit > 500:
            raise ValidationError("El limite solicitado esta fuera del rango permitido.")
        return limit

    @staticmethod
    def _ensure_first_action(*, novelty: Novelty, action_at: datetime) -> None:
        if novelty.first_action_at is None:
            novelty.first_action_at = action_at

    @staticmethod
    def _apply_status(*, novelty: Novelty, next_status: NoveltyStatus, changed_at: datetime) -> None:
        current_status = NoveltyStatus(novelty.status)
        if current_status == NoveltyStatus.CLOSED and next_status != NoveltyStatus.CLOSED:
            raise ValidationError("No se admite reabrir novedades cerradas en esta fase del modulo.")
        if novelty.resolved_at is not None and next_status not in {NoveltyStatus.RESOLVED, NoveltyStatus.CLOSED}:
            raise ValidationError("No se admite devolver una novedad resuelta a un estado abierto en esta fase.")

        novelty.status = next_status.value
        if next_status == NoveltyStatus.RESOLVED:
            novelty.resolved_at = novelty.resolved_at or changed_at
        elif next_status == NoveltyStatus.CLOSED:
            novelty.resolved_at = novelty.resolved_at or changed_at
            novelty.closed_at = changed_at

    def _get_persisted_novelty(self, novelty_id: int) -> Novelty:
        novelty = self.novelty_repository.get_novelty_by_id(novelty_id)
        if not novelty:
            raise NotFoundError("La novedad solicitada no existe.")
        return novelty

    def _get_persisted_log(self, log_id: int) -> NoveltyLog:
        log = self.novelty_repository.get_log_by_id(log_id)
        if not log:
            raise NotFoundError("La bitacora solicitada no existe.")
        return log
