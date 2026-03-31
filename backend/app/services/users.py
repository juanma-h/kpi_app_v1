from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.core.security import hash_password
from app.domain.enums import UserRole
from app.models.user import User
from app.repositories.contracts import UserRepositoryProtocol


class UserService:
    def __init__(self, user_repository: UserRepositoryProtocol):
        self.user_repository = user_repository

    def list_users(
        self,
        *,
        is_active: bool | None = None,
        role: UserRole | None = None,
    ) -> list[User]:
        role_value = role.value if role else None
        return list(self.user_repository.list_all(is_active=is_active, role=role_value))

    def get_user(self, *, user_id: int) -> User:
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundError("El usuario solicitado no existe.")
        return user

    def create_user(
        self,
        *,
        name: str,
        email: str,
        password: str,
        role: UserRole,
        is_active: bool = True,
    ) -> User:
        normalized_name = self._normalize_name(name)
        normalized_email = self._normalize_email(email)

        existing = self.user_repository.get_by_email(normalized_email)
        if existing:
            raise ConflictError("Ya existe un usuario con ese correo.")

        user = self.user_repository.create(
            name=normalized_name,
            email=normalized_email,
            password_hash=hash_password(password),
            role=role.value,
            is_active=is_active,
        )
        self.user_repository.commit()
        self.user_repository.refresh(user)
        return user

    def update_user(
        self,
        *,
        user_id: int,
        actor_user_id: int,
        name: str | None = None,
        email: str | None = None,
        password: str | None = None,
        role: UserRole | None = None,
    ) -> User:
        user = self.get_user(user_id=user_id)

        if all(value is None for value in (name, email, password, role)):
            raise ValidationError("No se enviaron cambios para actualizar el usuario.")

        if role is not None and actor_user_id == user_id and role.value != user.role:
            raise ValidationError("No puedes cambiar tu propio rol.")

        if name is not None:
            user.name = self._normalize_name(name)

        if email is not None:
            normalized_email = self._normalize_email(email)
            existing = self.user_repository.get_by_email(normalized_email)
            if existing and existing.id != user.id:
                raise ConflictError("Ya existe un usuario con ese correo.")
            user.email = normalized_email

        if password is not None:
            user.password_hash = hash_password(password)

        if role is not None:
            user.role = role.value

        self.user_repository.commit()
        self.user_repository.refresh(user)
        return user

    def set_user_status(
        self,
        *,
        user_id: int,
        actor_user_id: int,
        is_active: bool,
    ) -> User:
        user = self.get_user(user_id=user_id)

        if actor_user_id == user_id and not is_active:
            raise ValidationError("No puedes desactivar tu propio usuario.")

        user.is_active = is_active
        self.user_repository.commit()
        self.user_repository.refresh(user)
        return user

    @staticmethod
    def _normalize_name(name: str) -> str:
        normalized = name.strip()
        if not normalized:
            raise ValidationError("El nombre es obligatorio.")
        return normalized

    @staticmethod
    def _normalize_email(email: str) -> str:
        normalized = email.strip().lower()
        if not normalized:
            raise ValidationError("El correo es obligatorio.")
        return normalized
