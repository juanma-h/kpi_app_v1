from datetime import datetime, timezone
import unittest

from bootstrap import configure_test_environment

configure_test_environment()

from fastapi.testclient import TestClient

from app.core.deps import get_current_user, get_user_service
from app.domain.enums import UserRole
from app.main import app
from app.models.user import User


def build_user(
    *,
    user_id: int,
    email: str,
    role: UserRole,
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


class FakeUserService:
    def __init__(self):
        self.users = [
            build_user(user_id=1, email="admin@kpi.com", role=UserRole.ADMIN),
            build_user(user_id=2, email="employee@kpi.com", role=UserRole.EMPLOYEE),
        ]
        self.created_payload: dict | None = None

    def list_users(self, *, is_active: bool | None = None, role: UserRole | None = None):
        users = list(self.users)
        if is_active is not None:
            users = [user for user in users if user.is_active == is_active]
        if role is not None:
            users = [user for user in users if user.role == role.value]
        return users

    def get_user(self, *, user_id: int):
        return next(user for user in self.users if user.id == user_id)

    def create_user(self, *, name: str, email: str, password: str, role: UserRole, is_active: bool):
        self.created_payload = {
            "name": name,
            "email": email,
            "password": password,
            "role": role,
            "is_active": is_active,
        }
        user = build_user(user_id=3, email=email, role=role, is_active=is_active)
        user.name = name
        self.users.append(user)
        return user

    def update_user(self, *, user_id: int, actor_user_id: int, name=None, email=None, password=None, role=None):
        user = self.get_user(user_id=user_id)
        if name is not None:
            user.name = name
        if email is not None:
            user.email = email
        if role is not None:
            user.role = role.value
        return user

    def set_user_status(self, *, user_id: int, actor_user_id: int, is_active: bool):
        user = self.get_user(user_id=user_id)
        user.is_active = is_active
        return user


class UsersApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.user_service = FakeUserService()

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    def test_supervisor_can_list_users(self) -> None:
        app.dependency_overrides[get_current_user] = lambda: build_user(
            user_id=10,
            email="supervisor@kpi.com",
            role=UserRole.SUPERVISOR,
        )
        app.dependency_overrides[get_user_service] = lambda: self.user_service

        response = self.client.get("/users")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)

    def test_supervisor_cannot_create_users(self) -> None:
        app.dependency_overrides[get_current_user] = lambda: build_user(
            user_id=10,
            email="supervisor@kpi.com",
            role=UserRole.SUPERVISOR,
        )
        app.dependency_overrides[get_user_service] = lambda: self.user_service

        response = self.client.post(
            "/users",
            json={
                "name": "Nuevo Usuario",
                "email": "nuevo@kpi.com",
                "password": "Secreta123",
                "role": "EMPLOYEE",
                "is_active": True,
            },
        )

        self.assertEqual(response.status_code, 403)

    def test_admin_can_create_users(self) -> None:
        app.dependency_overrides[get_current_user] = lambda: build_user(
            user_id=1,
            email="admin@kpi.com",
            role=UserRole.ADMIN,
        )
        app.dependency_overrides[get_user_service] = lambda: self.user_service

        response = self.client.post(
            "/users",
            json={
                "name": "Nuevo Usuario",
                "email": "nuevo@kpi.com",
                "password": "Secreta123",
                "role": "EMPLOYEE",
                "is_active": True,
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["email"], "nuevo@kpi.com")
        self.assertEqual(self.user_service.created_payload["role"], UserRole.EMPLOYEE)


if __name__ == "__main__":
    unittest.main()
