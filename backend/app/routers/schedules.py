from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query, status

from app.core.deps import get_current_user, get_schedule_service, require_roles
from app.domain.enums import UserRole
from app.models.user import User
from app.schemas.schedule import (
    ScheduleAssignmentCreate,
    ScheduleAssignmentResponse,
    ScheduleResolutionResponse,
    ScheduleTemplateCreate,
    ScheduleTemplateResponse,
    ScheduleTemplateStatusUpdate,
    ScheduleTemplateUpdate,
)
from app.services.schedules import ScheduleService

router = APIRouter(prefix="/schedules", tags=["schedules"])


@router.get("/templates", response_model=list[ScheduleTemplateResponse])
def list_schedule_templates(
    is_active: bool | None = Query(default=None),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.SUPERVISOR)),
    schedule_service: ScheduleService = Depends(get_schedule_service),
) -> list[ScheduleTemplateResponse]:
    return schedule_service.list_templates(is_active=is_active)


@router.get("/templates/{template_id}", response_model=ScheduleTemplateResponse)
def get_schedule_template(
    template_id: int,
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.SUPERVISOR)),
    schedule_service: ScheduleService = Depends(get_schedule_service),
) -> ScheduleTemplateResponse:
    return schedule_service.get_template(template_id=template_id)


@router.post("/templates", response_model=ScheduleTemplateResponse, status_code=status.HTTP_201_CREATED)
def create_schedule_template(
    payload: ScheduleTemplateCreate,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    schedule_service: ScheduleService = Depends(get_schedule_service),
) -> ScheduleTemplateResponse:
    return schedule_service.create_template(
        name=payload.name,
        description=payload.description,
        timezone_name=payload.timezone_name,
        grace_minutes=payload.grace_minutes,
        slots=[slot.model_dump() for slot in payload.slots],
        created_by_user_id=current_user.id,
        is_active=payload.is_active,
    )


@router.patch("/templates/{template_id}", response_model=ScheduleTemplateResponse)
def update_schedule_template(
    template_id: int,
    payload: ScheduleTemplateUpdate,
    _: User = Depends(require_roles(UserRole.ADMIN)),
    schedule_service: ScheduleService = Depends(get_schedule_service),
) -> ScheduleTemplateResponse:
    slots = [slot.model_dump() for slot in payload.slots] if payload.slots is not None else None
    return schedule_service.update_template(
        template_id=template_id,
        name=payload.name,
        description=payload.description,
        timezone_name=payload.timezone_name,
        grace_minutes=payload.grace_minutes,
        slots=slots,
    )


@router.patch("/templates/{template_id}/status", response_model=ScheduleTemplateResponse)
def update_schedule_template_status(
    template_id: int,
    payload: ScheduleTemplateStatusUpdate,
    _: User = Depends(require_roles(UserRole.ADMIN)),
    schedule_service: ScheduleService = Depends(get_schedule_service),
) -> ScheduleTemplateResponse:
    return schedule_service.set_template_status(template_id=template_id, is_active=payload.is_active)


@router.get("/assignments", response_model=list[ScheduleAssignmentResponse])
def list_schedule_assignments(
    user_id: int | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.SUPERVISOR)),
    schedule_service: ScheduleService = Depends(get_schedule_service),
) -> list[ScheduleAssignmentResponse]:
    return schedule_service.list_assignments(user_id=user_id, is_active=is_active)


@router.post("/assignments", response_model=ScheduleAssignmentResponse, status_code=status.HTTP_201_CREATED)
def create_schedule_assignment(
    payload: ScheduleAssignmentCreate,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    schedule_service: ScheduleService = Depends(get_schedule_service),
) -> ScheduleAssignmentResponse:
    return schedule_service.create_assignment(
        user_id=payload.user_id,
        schedule_template_id=payload.schedule_template_id,
        effective_from=payload.effective_from,
        effective_to=payload.effective_to,
        notes=payload.notes,
        assigned_by_user_id=current_user.id,
        is_active=payload.is_active,
    )


@router.get("/me/resolved", response_model=ScheduleResolutionResponse)
def get_my_resolved_schedule(
    target_date: date | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    schedule_service: ScheduleService = Depends(get_schedule_service),
) -> ScheduleResolutionResponse:
    return schedule_service.resolve_schedule(user_id=current_user.id, target_date=target_date)


@router.get("/users/{user_id}/resolved", response_model=ScheduleResolutionResponse)
def get_user_resolved_schedule(
    user_id: int,
    target_date: date | None = Query(default=None),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.SUPERVISOR)),
    schedule_service: ScheduleService = Depends(get_schedule_service),
) -> ScheduleResolutionResponse:
    return schedule_service.resolve_schedule(user_id=user_id, target_date=target_date)
