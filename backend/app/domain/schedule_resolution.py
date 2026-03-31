from __future__ import annotations

import math
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from app.core.exceptions import InternalStateError
from app.domain.enums import Weekday
from app.models.user_schedule_assignment import UserScheduleAssignment


def resolve_schedule_for_date(
    *,
    user_id: int,
    assignments: list[UserScheduleAssignment],
    target_date: date,
) -> dict:
    matches = [
        assignment
        for assignment in assignments
        if assignment.effective_from <= target_date
        and (assignment.effective_to is None or assignment.effective_to >= target_date)
    ]
    if len(matches) > 1:
        raise InternalStateError("Existe mas de una asignacion activa para la fecha consultada.")

    if not matches:
        return _build_unscheduled_resolution(
            user_id=user_id,
            target_date=target_date,
            reason="No hay una asignacion activa para la fecha consultada.",
        )

    return _build_resolution(
        user_id=user_id,
        assignment=matches[0],
        target_date=target_date,
        actual_start_at=None,
    )


def resolve_schedule_for_shift_start(
    *,
    user_id: int,
    assignments: list[UserScheduleAssignment],
    shift_start_at: datetime,
) -> dict:
    matches: list[tuple[UserScheduleAssignment, date]] = []
    for assignment in assignments:
        timezone = ZoneInfo(assignment.schedule_template.timezone_name)
        local_date = shift_start_at.astimezone(timezone).date()
        if assignment.effective_from <= local_date and (
            assignment.effective_to is None or assignment.effective_to >= local_date
        ):
            matches.append((assignment, local_date))

    if len(matches) > 1:
        raise InternalStateError("Existe mas de una asignacion activa para el turno consultado.")

    if not matches:
        return _build_unscheduled_resolution(
            user_id=user_id,
            target_date=shift_start_at.date(),
            reason="No hay una asignacion activa que cubra la fecha del turno.",
        )

    assignment, local_date = matches[0]
    return _build_resolution(
        user_id=user_id,
        assignment=assignment,
        target_date=local_date,
        actual_start_at=shift_start_at,
    )


def _build_resolution(
    *,
    user_id: int,
    assignment: UserScheduleAssignment,
    target_date: date,
    actual_start_at: datetime | None,
) -> dict:
    template = assignment.schedule_template
    weekday_value = weekday_from_date(target_date)
    slot = next((slot for slot in template.slots if slot.weekday == weekday_value), None)

    if not slot:
        return {
            "user_id": user_id,
            "target_date": target_date,
            "is_scheduled": False,
            "resolution_reason": "La asignacion activa no define horario para el dia consultado.",
            "assignment_id": assignment.id,
            "schedule_template_id": template.id,
            "schedule_template_name": template.name,
            "timezone_name": template.timezone_name,
            "weekday": Weekday(weekday_value),
            "expected_start_time": None,
            "expected_end_time": None,
            "expected_start_at": None,
            "expected_end_at": None,
            "grace_deadline_at": None,
            "grace_minutes": template.grace_minutes,
            "effective_from": assignment.effective_from,
            "effective_to": assignment.effective_to,
            "notes": assignment.notes,
            "actual_start_at": actual_start_at,
            "is_punctual": None,
            "late_by_minutes": None,
            "start_delay_minutes": None,
        }

    timezone = ZoneInfo(template.timezone_name)
    expected_start_at = datetime.combine(target_date, slot.start_time, tzinfo=timezone)
    expected_end_at = datetime.combine(target_date, slot.end_time, tzinfo=timezone)
    if slot.end_time <= slot.start_time:
        expected_end_at += timedelta(days=1)
    grace_deadline_at = expected_start_at + timedelta(minutes=template.grace_minutes)

    if actual_start_at is None:
        is_punctual = None
        late_by_minutes = None
        start_delay_minutes = None
    else:
        is_punctual = actual_start_at <= grace_deadline_at
        late_by_minutes = _ceil_positive_minutes(actual_start_at - grace_deadline_at)
        start_delay_minutes = _ceil_positive_minutes(actual_start_at - expected_start_at)

    return {
        "user_id": user_id,
        "target_date": target_date,
        "is_scheduled": True,
        "resolution_reason": None,
        "assignment_id": assignment.id,
        "schedule_template_id": template.id,
        "schedule_template_name": template.name,
        "timezone_name": template.timezone_name,
        "weekday": Weekday(weekday_value),
        "expected_start_time": slot.start_time,
        "expected_end_time": slot.end_time,
        "expected_start_at": expected_start_at,
        "expected_end_at": expected_end_at,
        "grace_deadline_at": grace_deadline_at,
        "grace_minutes": template.grace_minutes,
        "effective_from": assignment.effective_from,
        "effective_to": assignment.effective_to,
        "notes": assignment.notes,
        "actual_start_at": actual_start_at,
        "is_punctual": is_punctual,
        "late_by_minutes": late_by_minutes,
        "start_delay_minutes": start_delay_minutes,
    }


def _build_unscheduled_resolution(
    *,
    user_id: int,
    target_date: date,
    reason: str,
) -> dict:
    return {
        "user_id": user_id,
        "target_date": target_date,
        "is_scheduled": False,
        "resolution_reason": reason,
        "assignment_id": None,
        "schedule_template_id": None,
        "schedule_template_name": None,
        "timezone_name": None,
        "weekday": Weekday(weekday_from_date(target_date)),
        "expected_start_time": None,
        "expected_end_time": None,
        "expected_start_at": None,
        "expected_end_at": None,
        "grace_deadline_at": None,
        "grace_minutes": None,
        "effective_from": None,
        "effective_to": None,
        "notes": None,
        "actual_start_at": None,
        "is_punctual": None,
        "late_by_minutes": None,
        "start_delay_minutes": None,
    }


def weekday_from_date(target_date: date) -> str:
    return list(Weekday)[target_date.weekday()].value


def _ceil_positive_minutes(delta: timedelta) -> int:
    seconds = delta.total_seconds()
    if seconds <= 0:
        return 0
    return math.ceil(seconds / 60)
