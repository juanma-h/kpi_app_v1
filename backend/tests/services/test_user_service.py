import unittest
from datetime import datetime, timezone

from bootstrap import configure_test_environment

configure_test_environment()

from app.core.exceptions import ConflictError, ValidationError
from app.domain.enums import UserRole
from app.models.user import User
from app.services.users import UserService


class FakeUserRepository:
    def __init__(self, users: list[User] | None = None):
        self.users = users or []
        self.commits = 0
        self._next_id = max((user.id for user in self.users), default=0) + 1

    def list_all(
        self,
        *,
        is_active: bool | None = None,
        role: str | None = None,
    ) -> list[User]:
        users = list(self.users)
        if is_active is not None:
            users = [user for user in users if user.is_active == is_active]
        if role is not None:
            users = [user for user in users if user.role == role]
        return users

    def get_by_id(self, user_id: int) -> User | None:
        return next((user for user in self.users if user.id == user_id), None)

    def get_by_email(self, email: str) -> User | None:
        return next((user for user in self.users if user.email == email), None)

    def create(
        self,
        *,
        name: str,
        email: str,
        password_hash: str,
        role: str,
        is_active: bool,
    ) -> User:
        user = User(
            id=self._next_id,
            name=name,
            email=email,
            password_hash=password_hash,
            role=role,
            is_active=is_active,
            created_at=datetime.now(timezone.utc),
        )
        self._next_id += 1
        self.users.append(user)
        return user

    def commit(self) -> None:
        self.commits += 1

    def refresh(self, instance: object) -> None:
        return None


def build_user(
    *,
    user_id: int,
    email: str,
    role: UserRole = UserRole.EMPLOYEE,
    is_active: bool = True,
) -> User:
    return User(
        id=user_id,
        name=f"User {user_id}",
        email=email,
        password_hash="hashed",
        role=role.value,
        is_active=is_active,
        created_at=datetime.now(timezone.utc),
    )


class UserServiceTests(unittest.TestCase):
    def test_create_user_normalizes_email_and_name(self) -> None:
        repository = FakeUserRepository()
        service = UserService(user_repository=repository)

        user = service.create_user(
            name="  Ana Perez  ",
            email=" ANA@EXAMPLE.COM ",
            password="Secreta123",
            role=UserRole.SUPERVISOR,
            is_active=True,
        )

        self.assertEqual(user.name, "Ana Perez")
        self.assertEqual(user.email, "ana@example.com")
        self.assertEqual(user.role, UserRole.SUPERVISOR.value)
        self.assertEqual(repository.commits, 1)

    def test_create_user_rejects_duplicate_email(self) -> None:
        repository = FakeUserRepository([build_user(user_id=1, email="ana@example.com")])
        service = UserService(user_repository=repository)

        with self.assertRaisesRegex(ConflictError, "correo"):
            service.create_user(
                name="Ana Perez",
                email="ana@example.com",
                password="Secreta123",
                role=UserRole.EMPLOYEE,
                is_active=True,
            )

    def test_update_user_rejects_self_role_change(self) -> None:
        repository = FakeUserRepository([build_user(user_id=1, email="admin@example.com", role=UserRole.ADMIN)])
        service = UserService(user_repository=repository)

        with self.assertRaisesRegex(ValidationError, "propio rol"):
            service.update_user(
                user_id=1,
                actor_user_id=1,
                role=UserRole.SUPERVISOR,
            )

    def test_set_user_status_rejects_self_deactivation(self) -> None:
        repository = FakeUserRepository([build_user(user_id=1, email="admin@example.com", role=UserRole.ADMIN)])
        service = UserService(user_repository=repository)

        with self.assertRaisesRegex(ValidationError, "desactivar tu propio usuario"):
            service.set_user_status(user_id=1, actor_user_id=1, is_active=False)


if __name__ == "__main__":
    unittest.main()
