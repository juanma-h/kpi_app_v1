from app.core.exceptions import AuthenticationError
from app.core.security import create_access_token, verify_password
from app.repositories.contracts import UserRepositoryProtocol


class AuthService:
    def __init__(self, user_repository: UserRepositoryProtocol):
        self.user_repository = user_repository

    def authenticate(self, *, email: str, password: str) -> str:
        user = self.user_repository.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise AuthenticationError("Credenciales invalidas.")

        if not user.is_active:
            raise AuthenticationError("El usuario esta inactivo.")

        return create_access_token(
            subject=str(user.id),
            extra_claims={"role": user.role},
        )
