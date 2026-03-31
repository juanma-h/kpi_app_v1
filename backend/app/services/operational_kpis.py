from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone

from app.core.exceptions import NotFoundError, ValidationError
from app.domain.enums import ActivityEventType, SessionStatus, ShiftStatus
from app.models.activity_event import ActivityEvent
from app.models.session import Session as WorkSession
from app.models.shift import Shift
from app.repositories.contracts import OperationalKpiRepositoryProtocol


class OperationalKpiService:
    def __init__(self, operational_kpi_repository: OperationalKpiRepositoryProtocol):
        self.operational_kpi_repository = operational_kpi_repository

    def get_overview(
        self,
        *,
        started_from: datetime | None = None,
        started_to: datetime | None = None,
        limit: int = 200,
    ) -> dict:
        normalized_from = self._normalize_range_datetime(started_from)
        normalized_to = self._normalize_range_datetime(started_to)
        normalized_limit = self._normalize_limit(limit)
        self._validate_range(normalized_from, normalized_to)

        shifts = list(
            self.operational_kpi_repository.list_shifts(
                started_from=normalized_from,
                started_to=normalized_to,
                limit=normalized_limit,
            )
        )
        shift_ids = [shift.id for shift in shifts]
        return self._build_summary(
            shifts=shifts,
            sessions=list(self.operational_kpi_repository.list_sessions(shift_ids=shift_ids)),
            events=list(self.operational_kpi_repository.list_events(shift_ids=shift_ids)),
        )

    def get_user_overview(
        self,
        *,
        user_id: int,
        started_from: datetime | None = None,
        started_to: datetime | None = None,
        limit: int = 200,
    ) -> dict:
        user = self.operational_kpi_repository.get_user_by_id(user_id)
        if not user:
            raise NotFoundError("El usuario solicitado no existe.")

        normalized_from = self._normalize_range_datetime(started_from)
        normalized_to = self._normalize_range_datetime(started_to)
        normalized_limit = self._normalize_limit(limit)
        self._validate_range(normalized_from, normalized_to)

        shifts = list(
            self.operational_kpi_repository.list_shifts(
                user_id=user_id,
                started_from=normalized_from,
                started_to=normalized_to,
                limit=normalized_limit,
            )
        )
        shift_ids = [shift.id for shift in shifts]
        summary = self._build_summary(
            shifts=shifts,
            sessions=list(
                self.operational_kpi_repository.list_sessions(
                    user_id=user_id,
                    shift_ids=shift_ids,
                )
            ),
            events=list(
                self.operational_kpi_repository.list_events(
                    user_id=user_id,
                    shift_ids=shift_ids,
                )
            ),
        )
        summary["user_id"] = user.id
        summary["user_name"] = user.name
        summary["user_email"] = user.email
        summary["user_role"] = user.role
        return summary

    def get_shift_overview(self, *, shift_id: int) -> dict:
        shift = self.operational_kpi_repository.get_shift_by_id(shift_id)
        if not shift:
            raise NotFoundError("El turno solicitado no existe.")

        user = self.operational_kpi_repository.get_user_by_id(shift.user_id)
        sessions = list(self.operational_kpi_repository.list_sessions(shift_ids=[shift.id]))
        events = list(self.operational_kpi_repository.list_events(shift_ids=[shift.id]))
        summary = self._build_summary(
            shifts=[shift],
            sessions=sessions,
            events=events,
        )
        summary["shift_id"] = shift.id
        summary["shift_status"] = shift.status
        summary["shift_started_at"] = shift.start_at
        summary["shift_ended_at"] = shift.end_at
        summary["user_id"] = shift.user_id
        summary["user_name"] = user.name if user else None
        summary["user_email"] = user.email if user else None
        summary["user_role"] = user.role if user else None
        summary["device_labels"] = sorted(
            {session.device_label for session in sessions if session.device_label}
        )
        return summary

    def _build_summary(
        self,
        *,
        shifts: list[Shift],
        sessions: list[WorkSession],
        events: list[ActivityEvent],
    ) -> dict:
        now = datetime.now(timezone.utc)
        total_shift_seconds = sum(self._duration_seconds(shift.start_at, shift.end_at, now) for shift in shifts)
        total_session_seconds = sum(
            self._duration_seconds(session.start_at, session.end_at, now) for session in sessions
        )
        total_active_seconds = sum(
            event.duration_seconds or 0
            for event in events
            if event.event_type == ActivityEventType.HEARTBEAT.value
        )
        total_idle_seconds = sum(
            event.duration_seconds or 0
            for event in events
            if event.event_type == ActivityEventType.IDLE.value
        )
        total_tracked_seconds = total_active_seconds + total_idle_seconds
        total_untracked_session_seconds = max(total_session_seconds - total_tracked_seconds, 0)

        event_counter = Counter(event.event_type for event in events)
        domain_counter: dict[str, dict[str, int]] = defaultdict(
            lambda: {
                "event_count": 0,
                "page_view_count": 0,
                "heartbeat_count": 0,
                "idle_event_count": 0,
                "active_seconds": 0,
                "idle_seconds": 0,
            }
        )
        for event in events:
            stats = domain_counter[event.source_domain]
            stats["event_count"] += 1
            if event.event_type == ActivityEventType.PAGE_VIEW.value:
                stats["page_view_count"] += 1
            if event.event_type == ActivityEventType.HEARTBEAT.value:
                stats["heartbeat_count"] += 1
                stats["active_seconds"] += event.duration_seconds or 0
            if event.event_type == ActivityEventType.IDLE.value:
                stats["idle_event_count"] += 1
                stats["idle_seconds"] += event.duration_seconds or 0

        first_activity_at = min((event.occurred_at for event in events), default=None)
        last_activity_at = max((event.occurred_at for event in events), default=None)

        return {
            "shift_count": len(shifts),
            "closed_shift_count": sum(1 for shift in shifts if shift.status == ShiftStatus.CLOSED.value),
            "open_shift_count": sum(1 for shift in shifts if shift.status == ShiftStatus.OPEN.value),
            "session_count": len(sessions),
            "open_session_count": sum(1 for session in sessions if session.status == SessionStatus.OPEN.value),
            "total_shift_seconds": total_shift_seconds,
            "total_session_seconds": total_session_seconds,
            "total_active_seconds": total_active_seconds,
            "total_idle_seconds": total_idle_seconds,
            "total_tracked_seconds": total_tracked_seconds,
            "total_untracked_session_seconds": total_untracked_session_seconds,
            "activity_coverage_rate": self._safe_ratio(total_tracked_seconds, total_session_seconds),
            "active_rate": self._safe_ratio(total_active_seconds, total_tracked_seconds),
            "idle_rate": self._safe_ratio(total_idle_seconds, total_tracked_seconds),
            "event_count": len(events),
            "page_view_count": event_counter[ActivityEventType.PAGE_VIEW.value],
            "heartbeat_count": event_counter[ActivityEventType.HEARTBEAT.value],
            "idle_event_count": event_counter[ActivityEventType.IDLE.value],
            "resume_count": event_counter[ActivityEventType.RESUME.value],
            "distinct_domain_count": len(domain_counter),
            "first_activity_at": first_activity_at,
            "last_activity_at": last_activity_at,
            "punctuality_supported": False,
            "punctuality_reason": "La puntualidad requiere un modulo de horarios programados que aun no existe.",
            "domains": [
                {
                    "source_domain": domain,
                    **stats,
                }
                for domain, stats in sorted(
                    domain_counter.items(),
                    key=lambda item: (-item[1]["event_count"], item[0]),
                )
            ],
            "event_types": [
                {
                    "event_type": ActivityEventType.PAGE_VIEW,
                    "count": event_counter[ActivityEventType.PAGE_VIEW.value],
                    "tracked_seconds": 0,
                },
                {
                    "event_type": ActivityEventType.HEARTBEAT,
                    "count": event_counter[ActivityEventType.HEARTBEAT.value],
                    "tracked_seconds": total_active_seconds,
                },
                {
                    "event_type": ActivityEventType.IDLE,
                    "count": event_counter[ActivityEventType.IDLE.value],
                    "tracked_seconds": total_idle_seconds,
                },
                {
                    "event_type": ActivityEventType.RESUME,
                    "count": event_counter[ActivityEventType.RESUME.value],
                    "tracked_seconds": 0,
                },
            ],
        }

    @staticmethod
    def _duration_seconds(start_at: datetime, end_at: datetime | None, now: datetime) -> int:
        effective_end = end_at or now
        seconds = int((effective_end - start_at).total_seconds())
        return max(seconds, 0)

    @staticmethod
    def _safe_ratio(numerator: int, denominator: int) -> float:
        if denominator <= 0:
            return 0.0
        return round(numerator / denominator, 4)

    @staticmethod
    def _normalize_limit(limit: int) -> int:
        if limit < 1 or limit > 200:
            raise ValidationError("El limite solicitado esta fuera del rango permitido.")
        return limit

    @staticmethod
    def _normalize_range_datetime(value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            raise ValidationError("Los filtros de fecha deben incluir zona horaria.")
        return value.astimezone(timezone.utc)

    @staticmethod
    def _validate_range(started_from: datetime | None, started_to: datetime | None) -> None:
        if started_from and started_to and started_from > started_to:
            raise ValidationError("El rango de fechas enviado no es valido.")
