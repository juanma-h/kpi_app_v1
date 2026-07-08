from __future__ import annotations

from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

from app.core.exceptions import ConflictError, ValidationError
from app.domain.enums import ActivityEventType
from app.models.activity_event import ActivityEvent
from app.models.allowlist_domain import AllowlistDomain
from app.repositories.contracts import (
    ActivityEventRepositoryProtocol,
    AllowlistDomainRepositoryProtocol,
    ShiftWorkRepositoryProtocol,
)


class ActivityEventService:
    MAX_EVENT_AGE_HOURS = 24
    MAX_FUTURE_DRIFT_MINUTES = 5
    MAX_DURATION_SECONDS = 3600

    def __init__(
        self,
        *,
        activity_event_repository: ActivityEventRepositoryProtocol,
        shift_work_repository: ShiftWorkRepositoryProtocol,
        allowlist_repository: AllowlistDomainRepositoryProtocol,
    ):
        self.activity_event_repository = activity_event_repository
        self.shift_work_repository = shift_work_repository
        self.allowlist_repository = allowlist_repository

    def list_events(
        self,
        *,
        user_id: int | None = None,
        shift_id: int | None = None,
        session_id: int | None = None,
        allowlist_domain_id: int | None = None,
        event_type: ActivityEventType | None = None,
        occurred_from: datetime | None = None,
        occurred_to: datetime | None = None,
        limit: int = 100,
    ) -> list[ActivityEvent]:
        normalized_limit = self._normalize_limit(limit)
        normalized_from = self._normalize_range_datetime(occurred_from)
        normalized_to = self._normalize_range_datetime(occurred_to)

        if normalized_from and normalized_to and normalized_from > normalized_to:
            raise ValidationError("El rango de fechas enviado no es valido.")

        return list(
            self.activity_event_repository.list_all(
                user_id=user_id,
                shift_id=shift_id,
                session_id=session_id,
                allowlist_domain_id=allowlist_domain_id,
                event_type=event_type.value if event_type else None,
                occurred_from=normalized_from,
                occurred_to=normalized_to,
                limit=normalized_limit,
            )
        )

    def register_event(
        self,
        *,
        user_id: int,
        event_type: ActivityEventType,
        source_url: str,
        page_title: str | None,
        occurred_at: datetime | None,
        duration_seconds: int | None,
        event_data: dict[str, str | int | float | bool | None] | None,
    ) -> ActivityEvent:
        shift = self.shift_work_repository.get_open_shift_for_user(user_id)
        if not shift:
            raise ConflictError("Debes iniciar un turno activo antes de registrar actividad.")

        session = self.shift_work_repository.get_open_session_for_shift(shift.id)
        if not session:
            raise ConflictError("Debes tener una sesion activa antes de registrar actividad.")

        normalized_url, source_domain = self._normalize_source_url(source_url)
        allowlist_domain = self._resolve_allowlist_domain(source_domain)
        normalized_occurred_at = self._normalize_occurred_at(occurred_at)
        normalized_page_title = self._normalize_page_title(page_title)
        normalized_duration = self._normalize_duration(event_type=event_type, duration_seconds=duration_seconds)
        normalized_event_data = dict(event_data) if event_data else None

        event = self.activity_event_repository.create(
            user_id=user_id,
            shift_id=shift.id,
            session_id=session.id,
            allowlist_domain_id=allowlist_domain.id,
            event_type=event_type.value,
            source_url=normalized_url,
            source_domain=source_domain,
            page_title=normalized_page_title,
            occurred_at=normalized_occurred_at,
            duration_seconds=normalized_duration,
            event_data=normalized_event_data,
        )
        self.activity_event_repository.commit()
        self.activity_event_repository.refresh(event)
        return event

    def _resolve_allowlist_domain(self, source_domain: str) -> AllowlistDomain:
        active_domains = [
            entry
            for entry in self.allowlist_repository.list_all()
            if entry.is_active
        ]
        for entry in sorted(active_domains, key=lambda item: len(item.domain), reverse=True):
            if source_domain == entry.domain or source_domain.endswith(f".{entry.domain}"):
                return entry

        raise ValidationError("El dominio de origen no esta permitido en la allowlist.")

    @staticmethod
    def _normalize_source_url(source_url: str) -> tuple[str, str]:
        normalized_url = source_url.strip()
        parsed = urlparse(normalized_url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValidationError("La URL enviada no es valida para captura de actividad.")
        return normalized_url, parsed.hostname.lower().rstrip(".")

    @staticmethod
    def _normalize_page_title(page_title: str | None) -> str | None:
        if page_title is None:
            return None
        normalized = page_title.strip()
        return normalized or None

    @classmethod
    def _normalize_occurred_at(cls, occurred_at: datetime | None) -> datetime:
        if occurred_at is None:
            return datetime.now(timezone.utc)
        if occurred_at.tzinfo is None:
            raise ValidationError("El campo occurred_at debe incluir zona horaria.")

        normalized = occurred_at.astimezone(timezone.utc)
        now = datetime.now(timezone.utc)
        if normalized > now + timedelta(minutes=cls.MAX_FUTURE_DRIFT_MINUTES):
            raise ValidationError("El evento no puede registrarse con una fecha futura invalida.")
        if normalized < now - timedelta(hours=cls.MAX_EVENT_AGE_HOURS):
            raise ValidationError("El evento es demasiado antiguo para registrarse.")
        return normalized

    @classmethod
    def _normalize_duration(
        cls,
        *,
        event_type: ActivityEventType,
        duration_seconds: int | None,
    ) -> int | None:
        duration_required = {ActivityEventType.HEARTBEAT, ActivityEventType.IDLE}
        if event_type in duration_required and duration_seconds is None:
            raise ValidationError("El tipo de evento enviado requiere duration_seconds.")
        if event_type not in duration_required and duration_seconds is not None:
            raise ValidationError("El tipo de evento enviado no admite duration_seconds.")
        if duration_seconds is None:
            return None
        if duration_seconds < 1 or duration_seconds > cls.MAX_DURATION_SECONDS:
            raise ValidationError("El duration_seconds enviado esta fuera de rango.")
        return duration_seconds

    @staticmethod
    def _normalize_range_datetime(value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            raise ValidationError("Los filtros de fecha deben incluir zona horaria.")
        return value.astimezone(timezone.utc)

    @staticmethod
    def _normalize_limit(limit: int) -> int:
        if limit < 1 or limit > 200:
            raise ValidationError("El limite solicitado esta fuera del rango permitido.")
        return limit
