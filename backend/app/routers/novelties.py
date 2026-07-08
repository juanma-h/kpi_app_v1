from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query, status

from app.core.deps import (
    get_current_user,
    get_novelty_kpi_service,
    get_novelty_service,
    require_roles,
)
from app.domain.enums import NoveltyPriority, NoveltyStatus, UserRole
from app.models.user import User
from app.schemas.novelty import (
    NoveltyAssignmentUpdate,
    NoveltyCreate,
    NoveltyKpiOverviewResponse,
    NoveltyLogCreate,
    NoveltyLogResponse,
    NoveltyResponse,
    NoveltyStatusUpdate,
    NoveltyUpdate,
    OperationalAreaCreate,
    OperationalAreaResponse,
    OperationalAreaStatusUpdate,
    SourceSystemCreate,
    SourceSystemResponse,
    SourceSystemStatusUpdate,
)
from app.services.novelties import NoveltyService
from app.services.novelty_kpis import NoveltyKpiService

router = APIRouter(prefix="/novelties", tags=["novelties"])


@router.get("/areas", response_model=list[OperationalAreaResponse])
def list_operational_areas(
    is_active: bool | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    novelty_service: NoveltyService = Depends(get_novelty_service),
) -> list[OperationalAreaResponse]:
    resolved_is_active = is_active
    if current_user.role not in {UserRole.ADMIN.value, UserRole.SUPERVISOR.value}:
        resolved_is_active = True
    return novelty_service.list_areas(is_active=resolved_is_active)


@router.post("/areas", response_model=OperationalAreaResponse, status_code=status.HTTP_201_CREATED)
def create_operational_area(
    payload: OperationalAreaCreate,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    novelty_service: NoveltyService = Depends(get_novelty_service),
) -> OperationalAreaResponse:
    return novelty_service.create_area(
        code=payload.code,
        name=payload.name,
        description=payload.description,
        is_active=payload.is_active,
        created_by_user_id=current_user.id,
    )


@router.patch("/areas/{area_id}/status", response_model=OperationalAreaResponse)
def update_operational_area_status(
    area_id: int,
    payload: OperationalAreaStatusUpdate,
    _: User = Depends(require_roles(UserRole.ADMIN)),
    novelty_service: NoveltyService = Depends(get_novelty_service),
) -> OperationalAreaResponse:
    return novelty_service.set_area_status(area_id=area_id, is_active=payload.is_active)


@router.get("/source-systems", response_model=list[SourceSystemResponse])
def list_source_systems(
    is_active: bool | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    novelty_service: NoveltyService = Depends(get_novelty_service),
) -> list[SourceSystemResponse]:
    resolved_is_active = is_active
    if current_user.role not in {UserRole.ADMIN.value, UserRole.SUPERVISOR.value}:
        resolved_is_active = True
    return novelty_service.list_source_systems(is_active=resolved_is_active)


@router.post("/source-systems", response_model=SourceSystemResponse, status_code=status.HTTP_201_CREATED)
def create_source_system(
    payload: SourceSystemCreate,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    novelty_service: NoveltyService = Depends(get_novelty_service),
) -> SourceSystemResponse:
    return novelty_service.create_source_system(
        code=payload.code,
        name=payload.name,
        description=payload.description,
        allowlist_domain_id=payload.allowlist_domain_id,
        is_active=payload.is_active,
        created_by_user_id=current_user.id,
    )


@router.patch("/source-systems/{source_system_id}/status", response_model=SourceSystemResponse)
def update_source_system_status(
    source_system_id: int,
    payload: SourceSystemStatusUpdate,
    _: User = Depends(require_roles(UserRole.ADMIN)),
    novelty_service: NoveltyService = Depends(get_novelty_service),
) -> SourceSystemResponse:
    return novelty_service.set_source_system_status(
        source_system_id=source_system_id,
        is_active=payload.is_active,
    )


@router.get("/kpis/me", response_model=NoveltyKpiOverviewResponse)
def get_my_novelty_kpis(
    reported_from: datetime | None = Query(default=None),
    reported_to: datetime | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    novelty_kpi_service: NoveltyKpiService = Depends(get_novelty_kpi_service),
) -> NoveltyKpiOverviewResponse:
    return novelty_kpi_service.get_user_overview(
        user_id=current_user.id,
        reported_from=reported_from,
        reported_to=reported_to,
    )


@router.get("/kpis/overview", response_model=NoveltyKpiOverviewResponse)
def get_global_novelty_kpis(
    reported_from: datetime | None = Query(default=None),
    reported_to: datetime | None = Query(default=None),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.SUPERVISOR)),
    novelty_kpi_service: NoveltyKpiService = Depends(get_novelty_kpi_service),
) -> NoveltyKpiOverviewResponse:
    return novelty_kpi_service.get_global_overview(
        reported_from=reported_from,
        reported_to=reported_to,
    )


@router.get("/kpis/users/{user_id}", response_model=NoveltyKpiOverviewResponse)
def get_user_novelty_kpis(
    user_id: int,
    reported_from: datetime | None = Query(default=None),
    reported_to: datetime | None = Query(default=None),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.SUPERVISOR)),
    novelty_kpi_service: NoveltyKpiService = Depends(get_novelty_kpi_service),
) -> NoveltyKpiOverviewResponse:
    return novelty_kpi_service.get_user_overview(
        user_id=user_id,
        reported_from=reported_from,
        reported_to=reported_to,
    )


@router.get("/me", response_model=list[NoveltyResponse])
def list_my_novelties(
    status: NoveltyStatus | None = Query(default=None),
    priority: NoveltyPriority | None = Query(default=None),
    area_id: int | None = Query(default=None),
    source_system_id: int | None = Query(default=None),
    novelty_type: str | None = Query(default=None),
    reported_from: datetime | None = Query(default=None),
    reported_to: datetime | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    novelty_service: NoveltyService = Depends(get_novelty_service),
) -> list[NoveltyResponse]:
    return novelty_service.list_my_novelties(
        current_user=current_user,
        status=status,
        priority=priority,
        area_id=area_id,
        source_system_id=source_system_id,
        novelty_type=novelty_type,
        reported_from=reported_from,
        reported_to=reported_to,
        limit=limit,
    )


@router.get("", response_model=list[NoveltyResponse])
def list_novelties(
    area_id: int | None = Query(default=None),
    source_system_id: int | None = Query(default=None),
    assigned_user_id: int | None = Query(default=None),
    reported_by_user_id: int | None = Query(default=None),
    status: NoveltyStatus | None = Query(default=None),
    priority: NoveltyPriority | None = Query(default=None),
    novelty_type: str | None = Query(default=None),
    reported_from: datetime | None = Query(default=None),
    reported_to: datetime | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.SUPERVISOR)),
    novelty_service: NoveltyService = Depends(get_novelty_service),
) -> list[NoveltyResponse]:
    return novelty_service.list_novelties(
        area_id=area_id,
        source_system_id=source_system_id,
        assigned_user_id=assigned_user_id,
        reported_by_user_id=reported_by_user_id,
        status=status,
        priority=priority,
        novelty_type=novelty_type,
        reported_from=reported_from,
        reported_to=reported_to,
        limit=limit,
    )


@router.post("", response_model=NoveltyResponse, status_code=status.HTTP_201_CREATED)
def create_novelty(
    payload: NoveltyCreate,
    current_user: User = Depends(get_current_user),
    novelty_service: NoveltyService = Depends(get_novelty_service),
) -> NoveltyResponse:
    return novelty_service.create_novelty(
        actor=current_user,
        area_id=payload.area_id,
        source_system_id=payload.source_system_id,
        assigned_user_id=payload.assigned_user_id,
        external_reference=payload.external_reference,
        order_reference=payload.order_reference,
        customer_reference=payload.customer_reference,
        title=payload.title,
        description=payload.description,
        novelty_type=payload.novelty_type,
        priority=payload.priority,
        reported_at=payload.reported_at,
        extra_data=payload.extra_data,
    )


@router.get("/{novelty_id}", response_model=NoveltyResponse)
def get_novelty(
    novelty_id: int,
    current_user: User = Depends(get_current_user),
    novelty_service: NoveltyService = Depends(get_novelty_service),
) -> NoveltyResponse:
    return novelty_service.get_novelty(novelty_id=novelty_id, actor=current_user)


@router.patch("/{novelty_id}", response_model=NoveltyResponse)
def update_novelty(
    novelty_id: int,
    payload: NoveltyUpdate,
    current_user: User = Depends(get_current_user),
    novelty_service: NoveltyService = Depends(get_novelty_service),
) -> NoveltyResponse:
    return novelty_service.update_novelty(
        novelty_id=novelty_id,
        actor=current_user,
        **payload.model_dump(exclude_unset=True),
    )


@router.patch("/{novelty_id}/assignment", response_model=NoveltyResponse)
def update_novelty_assignment(
    novelty_id: int,
    payload: NoveltyAssignmentUpdate,
    current_user: User = Depends(get_current_user),
    novelty_service: NoveltyService = Depends(get_novelty_service),
) -> NoveltyResponse:
    return novelty_service.assign_novelty(
        novelty_id=novelty_id,
        actor=current_user,
        assigned_user_id=payload.assigned_user_id,
        note=payload.note,
    )


@router.patch("/{novelty_id}/status", response_model=NoveltyResponse)
def update_novelty_status(
    novelty_id: int,
    payload: NoveltyStatusUpdate,
    current_user: User = Depends(get_current_user),
    novelty_service: NoveltyService = Depends(get_novelty_service),
) -> NoveltyResponse:
    return novelty_service.set_novelty_status(
        novelty_id=novelty_id,
        actor=current_user,
        status=payload.status,
        note=payload.note,
    )


@router.get("/{novelty_id}/logs", response_model=list[NoveltyLogResponse])
def list_novelty_logs(
    novelty_id: int,
    current_user: User = Depends(get_current_user),
    novelty_service: NoveltyService = Depends(get_novelty_service),
) -> list[NoveltyLogResponse]:
    return novelty_service.list_logs(novelty_id=novelty_id, actor=current_user)


@router.post("/{novelty_id}/logs", response_model=NoveltyLogResponse, status_code=status.HTTP_201_CREATED)
def create_novelty_log(
    novelty_id: int,
    payload: NoveltyLogCreate,
    current_user: User = Depends(get_current_user),
    novelty_service: NoveltyService = Depends(get_novelty_service),
) -> NoveltyLogResponse:
    return novelty_service.create_log(
        novelty_id=novelty_id,
        actor=current_user,
        work_date=payload.work_date,
        log_type=payload.log_type,
        content=payload.content,
        worked_minutes=payload.worked_minutes,
        status_after=payload.status_after,
    )
