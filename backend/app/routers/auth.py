from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.core.deps import get_auth_service, get_current_user
from app.models.user import User
from app.schemas.auth import TokenResponse
from app.schemas.user import UserMe
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    token = auth_service.authenticate(
        email=form_data.username,
        password=form_data.password,
    )
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserMe)
def me(current_user: User = Depends(get_current_user)) -> UserMe:
    return UserMe(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role,
    )
