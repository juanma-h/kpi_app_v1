from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone

from app.core.exceptions import NotFoundError, ValidationError
from app.models.novelty import Novelty
from app.models.novelty_log import NoveltyLog
from app.repositories.contracts import NoveltyRepositoryProtocol


class NoveltyKpiService:
    def __init__(self, *, novelty_repository: NoveltyRepositoryProtocol):
        self.novelty_repository = novelty_repository

    def get_global_overview(
        self,
        *,
        reported_from: datetime | None = None,
        reported_to: datetime | None = None,
    ) -> dict:
        return self._build_overview(
            reported_from=reported_from,
            reported_to=reported_to,
        )

    def get_user_overview(
        self,
        *,
        user_id: int,
        reported_from: datetime | None = None,
        reported_to: datetime | None = None,
    ) -> dict:
        user = self.novelty_repository.get_user_by_id(user_id)
        if not user:
            raise NotFoundError("El usuario solicitado no existe.")

        overview = self._build_overview(
            involved_user_id=user.id,
            reported_from=reported_from,
            reported_to=reported_to,
        )
        overview["user_id"] = user.id
        overview["user_name"] = user.name
        overview["user_email"] = user.email
        overview["user_role"] = user.role
        return overview

    def _build_overview(
        self,
        *,
        involved_user_id: int | None = None,
        reported_from: datetime | None = None,
        reported_to: datetime | None = None,
    ) -> dict:
        normalized_from, normalized_to = self._normalize_range(reported_from, reported_to)
        novelties = list(
            self.novelty_repository.list_novelties(
                involved_user_id=involved_user_id,
                reported_from=normalized_from,
                reported_to=normalized_to,
                limit=None,
            )
        )
        logs = list(
            self.novelty_repository.list_logs_for_novelties(
                novelty_ids=[novelty.id for novelty in novelties],
            )
        )
        logs_by_novelty = self._group_logs_by_novelty(logs)

        status_counts = Counter(novelty.status for novelty in novelties)
        priority_counts = Counter(novelty.priority for novelty in novelties)
        area_counts = Counter(novelty.area.name for novelty in novelties)
        source_counts = Counter(novelty.source_system.name for novelty in novelties)
        type_counts = Counter(novelty.novelty_type for novelty in novelties)

        first_action_minutes = [
            round((novelty.first_action_at - novelty.reported_at).total_seconds() / 60, 2)
            for novelty in novelties
            if novelty.first_action_at is not None
        ]
        resolution_minutes = [
            round((novelty.resolved_at - novelty.reported_at).total_seconds() / 60, 2)
            for novelty in novelties
            if novelty.resolved_at is not None
        ]
        total_logged_minutes = sum(log.worked_minutes or 0 for log in logs)
        logged_novelty_count = sum(1 for novelty in novelties if logs_by_novelty.get(novelty.id))

        return {
            "total_novelties": len(novelties),
            "open_count": status_counts.get("OPEN", 0),
            "in_progress_count": status_counts.get("IN_PROGRESS", 0),
            "blocked_count": status_counts.get("BLOCKED", 0),
            "resolved_count": status_counts.get("RESOLVED", 0),
            "closed_count": status_counts.get("CLOSED", 0),
            "backlog_count": sum(
                status_counts.get(status, 0)
                for status in ("OPEN", "IN_PROGRESS", "BLOCKED")
            ),
            "assigned_count": sum(1 for novelty in novelties if novelty.assigned_user_id is not None),
            "unassigned_count": sum(1 for novelty in novelties if novelty.assigned_user_id is None),
            "log_entry_count": len(logs),
            "logged_novelty_count": logged_novelty_count,
            "total_logged_minutes": total_logged_minutes,
            "average_logged_minutes_per_novelty": round(
                total_logged_minutes / logged_novelty_count,
                2,
            ) if logged_novelty_count else 0.0,
            "average_time_to_first_action_minutes": round(
                sum(first_action_minutes) / len(first_action_minutes),
                2,
            ) if first_action_minutes else 0.0,
            "average_resolution_minutes": round(
                sum(resolution_minutes) / len(resolution_minutes),
                2,
            ) if resolution_minutes else 0.0,
            "first_reported_at": novelties[-1].reported_at if novelties else None,
            "last_reported_at": novelties[0].reported_at if novelties else None,
            "priorities": self._build_breakdown(priority_counts),
            "statuses": self._build_breakdown(status_counts),
            "areas": self._build_breakdown(area_counts),
            "source_systems": self._build_breakdown(source_counts),
            "novelty_types": self._build_breakdown(type_counts),
        }

    @staticmethod
    def _group_logs_by_novelty(logs: list[NoveltyLog]) -> dict[int, list[NoveltyLog]]:
        grouped: dict[int, list[NoveltyLog]] = {}
        for log in logs:
            grouped.setdefault(log.novelty_id, []).append(log)
        return grouped

    @staticmethod
    def _build_breakdown(counter: Counter[str]) -> list[dict]:
        return [
            {"key": key, "label": key, "count": count}
            for key, count in sorted(counter.items(), key=lambda item: (-item[1], item[0]))
        ]

    @staticmethod
    def _normalize_range(
        reported_from: datetime | None,
        reported_to: datetime | None,
    ) -> tuple[datetime | None, datetime | None]:
        if reported_from is not None and reported_from.tzinfo is None:
            raise ValidationError("Los filtros de fecha deben incluir zona horaria.")
        if reported_to is not None and reported_to.tzinfo is None:
            raise ValidationError("Los filtros de fecha deben incluir zona horaria.")

        normalized_from = reported_from.astimezone(timezone.utc) if reported_from else None
        normalized_to = reported_to.astimezone(timezone.utc) if reported_to else None
        if normalized_from and normalized_to and normalized_from > normalized_to:
            raise ValidationError("El rango de fechas enviado no es valido.")
        return normalized_from, normalized_to
