from fastapi import APIRouter, Depends, status

from app.core.deps import get_allowlist_domain_service, require_roles
from app.domain.enums import UserRole
from app.models.user import User
from app.schemas.allowlist import (
    AllowlistDomainCreate,
    AllowlistDomainResponse,
    AllowlistDomainStatusUpdate,
)
from app.services.allowlist_domains import AllowlistDomainService

router = APIRouter(prefix="/allowlist", tags=["allowlist"])


@router.get("/domains", response_model=list[AllowlistDomainResponse])
def list_domains(
    _: User = Depends(require_roles(UserRole.ADMIN)),
    allowlist_service: AllowlistDomainService = Depends(get_allowlist_domain_service),
) -> list[AllowlistDomainResponse]:
    return list(allowlist_service.list_domains())


@router.post(
    "/domains",
    response_model=AllowlistDomainResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_domain(
    payload: AllowlistDomainCreate,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    allowlist_service: AllowlistDomainService = Depends(get_allowlist_domain_service),
) -> AllowlistDomainResponse:
    return allowlist_service.create_domain(
        raw_domain=payload.domain,
        description=payload.description,
        created_by_user_id=current_user.id,
    )


@router.patch("/domains/{domain_id}/status", response_model=AllowlistDomainResponse)
def update_domain_status(
    domain_id: int,
    payload: AllowlistDomainStatusUpdate,
    _: User = Depends(require_roles(UserRole.ADMIN)),
    allowlist_service: AllowlistDomainService = Depends(get_allowlist_domain_service),
) -> AllowlistDomainResponse:
    return allowlist_service.set_domain_status(
        domain_id=domain_id,
        is_active=payload.is_active,
    )
