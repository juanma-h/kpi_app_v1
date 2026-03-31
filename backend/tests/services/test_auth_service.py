import unittest

from bootstrap import configure_test_environment

configure_test_environment()

from app.core.exceptions import AuthenticationError
from app.core.security import hash_password
from app.domain.enums import UserRole
from app.models.user import User
from app.services.auth import AuthService


class FakeUserRepository:
    def __init__(self, users: list[User]):
        self.users_by_email = {user.email: user for user in users}
        self.users_by_id = {user.id: user for user in users}

    def get_by_id(self, user_id: int) -> User | None:
        return self.users_by_id.get(user_id)

    def get_by_email(self, email: str) -> User | None:
        return self.users_by_email.get(email)


def build_user(*, is_active: bool = True) -> User:
    return User(
        id=1,
        name="Admin",
        email="admin@kpi.com",
        password_hash=hash_password("Admin123*"),
        role=UserRole.ADMIN.value,
        is_active=is_active,
    )


class AuthServiceTests(unittest.TestCase):
    def test_authenticate_returns_jwt_token(self) -> None:
        service = AuthService(user_repository=FakeUserRepository([build_user()]))

        token = service.authenticate(email="admin@kpi.com", password="Admin123*")

        self.assertTrue(token)
        self.assertEqual(token.count("."), 2)

    def test_authenticate_rejects_inactive_user(self) -> None:
        service = AuthService(user_repository=FakeUserRepository([build_user(is_active=False)]))

        with self.assertRaisesRegex(AuthenticationError, "inactivo"):
            service.authenticate(email="admin@kpi.com", password="Admin123*")


if __name__ == "__main__":
    unittest.main()
