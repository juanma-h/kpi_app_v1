from collections.abc import Generator

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import AuthenticationError, PermissionDeniedError
from app.db.session import SessionLocal
from app.domain.enums import UserRole
from app.models.user import User
from app.repositories.activity_events import ActivityEventRepository
from app.repositories.allowlist_domains import AllowlistDomainRepository
from app.repositories.operational_kpis import OperationalKpiRepository
from app.repositories.schedules import ScheduleRepository
from app.repositories.shift_work import ShiftWorkRepository
from app.repositories.users import UserRepository
from app.services.activity_events import ActivityEventService
from app.services.allowlist_domains import AllowlistDomainService
from app.services.auth import AuthService
from app.services.operational_kpis import OperationalKpiService
from app.services.schedules import ScheduleService
from app.services.shifts import ShiftService
from app.services.users import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise AuthenticationError("Token invalido o expirado.")
        user_id = int(user_id_str)
    except (JWTError, ValueError):
        raise AuthenticationError("Token invalido o expirado.")

    user = UserRepository(db).get_by_id(user_id)
    if not user or not user.is_active:
        raise AuthenticationError("Token invalido o expirado.")

    return user


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(user_repository=UserRepository(db))


def get_shift_service(db: Session = Depends(get_db)) -> ShiftService:
    return ShiftService(shift_work_repository=ShiftWorkRepository(db))


def get_allowlist_domain_service(db: Session = Depends(get_db)) -> AllowlistDomainService:
    return AllowlistDomainService(allowlist_repository=AllowlistDomainRepository(db))


def get_activity_event_service(db: Session = Depends(get_db)) -> ActivityEventService:
    return ActivityEventService(
        activity_event_repository=ActivityEventRepository(db),
        shift_work_repository=ShiftWorkRepository(db),
        allowlist_repository=AllowlistDomainRepository(db),
    )


def get_operational_kpi_service(db: Session = Depends(get_db)) -> OperationalKpiService:
    return OperationalKpiService(
        operational_kpi_repository=OperationalKpiRepository(db),
        schedule_repository=ScheduleRepository(db),
    )


def get_schedule_service(db: Session = Depends(get_db)) -> ScheduleService:
    return ScheduleService(schedule_repository=ScheduleRepository(db))


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(user_repository=UserRepository(db))


def require_roles(*roles: UserRole):
    allowed_roles = {role.value for role in roles}

    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise PermissionDeniedError("No tienes permisos para realizar esta accion.")
        return current_user

    return dependency
