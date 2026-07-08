from fastapi import APIRouter, Depends, Query, status

from app.core.deps import get_current_user, get_user_service, require_roles
from app.domain.enums import UserRole
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserStatusUpdate, UserUpdate
from app.services.users import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserResponse])
def list_users(
    is_active: bool | None = Query(default=None),
    role: UserRole | None = Query(default=None),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.SUPERVISOR)),
    user_service: UserService = Depends(get_user_service),
) -> list[UserResponse]:
    return user_service.list_users(is_active=is_active, role=role)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.SUPERVISOR)),
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    return user_service.get_user(user_id=user_id)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    _: User = Depends(require_roles(UserRole.ADMIN)),
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    return user_service.create_user(
        name=payload.name,
        email=payload.email,
        password=payload.password,
        role=payload.role,
        is_active=payload.is_active,
    )


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    payload: UserUpdate,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    return user_service.update_user(
        user_id=user_id,
        actor_user_id=current_user.id,
        name=payload.name,
        email=payload.email,
        password=payload.password,
        role=payload.role,
    )


@router.patch("/{user_id}/status", response_model=UserResponse)
def update_user_status(
    user_id: int,
    payload: UserStatusUpdate,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    return user_service.set_user_status(
        user_id=user_id,
        actor_user_id=current_user.id,
        is_active=payload.is_active,
    )
