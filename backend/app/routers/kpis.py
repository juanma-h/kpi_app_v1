from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query

from app.core.deps import get_current_user, get_operational_kpi_service, require_roles
from app.domain.enums import UserRole
from app.models.user import User
from app.schemas.kpi import OperationalKpiOverviewResponse, ShiftKpiResponse
from app.services.operational_kpis import OperationalKpiService

router = APIRouter(prefix="/kpis", tags=["kpis"])


@router.get("/me/overview", response_model=OperationalKpiOverviewResponse)
def get_my_kpi_overview(
    started_from: datetime | None = Query(default=None),
    started_to: datetime | None = Query(default=None),
    limit: int = Query(default=200, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    kpi_service: OperationalKpiService = Depends(get_operational_kpi_service),
) -> OperationalKpiOverviewResponse:
    return kpi_service.get_user_overview(
        user_id=current_user.id,
        started_from=started_from,
        started_to=started_to,
        limit=limit,
    )


@router.get("/overview", response_model=OperationalKpiOverviewResponse)
def get_operational_kpi_overview(
    started_from: datetime | None = Query(default=None),
    started_to: datetime | None = Query(default=None),
    limit: int = Query(default=200, ge=1, le=200),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.SUPERVISOR)),
    kpi_service: OperationalKpiService = Depends(get_operational_kpi_service),
) -> OperationalKpiOverviewResponse:
    return kpi_service.get_overview(
        started_from=started_from,
        started_to=started_to,
        limit=limit,
    )


@router.get("/users/{user_id}/overview", response_model=OperationalKpiOverviewResponse)
def get_user_kpi_overview(
    user_id: int,
    started_from: datetime | None = Query(default=None),
    started_to: datetime | None = Query(default=None),
    limit: int = Query(default=200, ge=1, le=200),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.SUPERVISOR)),
    kpi_service: OperationalKpiService = Depends(get_operational_kpi_service),
) -> OperationalKpiOverviewResponse:
    return kpi_service.get_user_overview(
        user_id=user_id,
        started_from=started_from,
        started_to=started_to,
        limit=limit,
    )


@router.get("/shifts/{shift_id}", response_model=ShiftKpiResponse)
def get_shift_kpi_overview(
    shift_id: int,
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.SUPERVISOR)),
    kpi_service: OperationalKpiService = Depends(get_operational_kpi_service),
) -> ShiftKpiResponse:
    return kpi_service.get_shift_overview(shift_id=shift_id)
