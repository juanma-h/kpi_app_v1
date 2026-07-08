from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query, status

from app.core.deps import get_activity_event_service, get_current_user, require_roles
from app.domain.enums import ActivityEventType, UserRole
from app.models.user import User
from app.schemas.activity import ActivityEventCreate, ActivityEventResponse
from app.services.activity_events import ActivityEventService

router = APIRouter(prefix="/activity", tags=["activity"])


@router.post("/events", response_model=ActivityEventResponse, status_code=status.HTTP_201_CREATED)
def register_activity_event(
    payload: ActivityEventCreate,
    current_user: User = Depends(get_current_user),
    activity_service: ActivityEventService = Depends(get_activity_event_service),
) -> ActivityEventResponse:
    return activity_service.register_event(
        user_id=current_user.id,
        event_type=payload.event_type,
        source_url=payload.source_url,
        page_title=payload.page_title,
        occurred_at=payload.occurred_at,
        duration_seconds=payload.duration_seconds,
        event_data=payload.event_data,
    )


@router.get("/events/me", response_model=list[ActivityEventResponse])
def list_my_activity_events(
    event_type: ActivityEventType | None = Query(default=None),
    allowlist_domain_id: int | None = Query(default=None),
    occurred_from: datetime | None = Query(default=None),
    occurred_to: datetime | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    activity_service: ActivityEventService = Depends(get_activity_event_service),
) -> list[ActivityEventResponse]:
    return activity_service.list_events(
        user_id=current_user.id,
        allowlist_domain_id=allowlist_domain_id,
        event_type=event_type,
        occurred_from=occurred_from,
        occurred_to=occurred_to,
        limit=limit,
    )


@router.get("/events", response_model=list[ActivityEventResponse])
def list_activity_events(
    user_id: int | None = Query(default=None),
    shift_id: int | None = Query(default=None),
    session_id: int | None = Query(default=None),
    allowlist_domain_id: int | None = Query(default=None),
    event_type: ActivityEventType | None = Query(default=None),
    occurred_from: datetime | None = Query(default=None),
    occurred_to: datetime | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=200),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.SUPERVISOR)),
    activity_service: ActivityEventService = Depends(get_activity_event_service),
) -> list[ActivityEventResponse]:
    return activity_service.list_events(
        user_id=user_id,
        shift_id=shift_id,
        session_id=session_id,
        allowlist_domain_id=allowlist_domain_id,
        event_type=event_type,
        occurred_from=occurred_from,
        occurred_to=occurred_to,
        limit=limit,
    )
