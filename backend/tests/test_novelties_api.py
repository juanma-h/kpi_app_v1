from datetime import date, datetime, timezone
import unittest

from tests.bootstrap import configure_test_environment

configure_test_environment()

from fastapi.testclient import TestClient

from app.core.deps import get_current_user, get_novelty_kpi_service, get_novelty_service
from app.domain.enums import NoveltyLogType, NoveltyPriority, NoveltyStatus, UserRole
from app.main import app
from app.models.allowlist_domain import AllowlistDomain
from app.models.novelty import Novelty
from app.models.novelty_log import NoveltyLog
from app.models.operational_area import OperationalArea
from app.models.source_system import SourceSystem
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


def build_novelty(*, novelty_id: int, assigned_user_id: int | None = 2, status: NoveltyStatus = NoveltyStatus.OPEN) -> Novelty:
    now = datetime.now(timezone.utc)
    reporter = build_user(user_id=2, email="employee@kpi.com", role=UserRole.EMPLOYEE)
    assignee = build_user(user_id=assigned_user_id, email="assignee@kpi.com", role=UserRole.EMPLOYEE) if assigned_user_id else None
    area = OperationalArea(
        id=1,
        code="NOVEDADES",
        name="Novedades",
        description="Gestion ecommerce",
        is_active=True,
        created_by_user_id=1,
        created_at=now,
        updated_at=now,
    )
    allowlist = AllowlistDomain(
        id=1,
        domain="vendelo.example.com",
        description="Vendelo",
        is_active=True,
        created_by_user_id=1,
        created_at=now,
        updated_at=now,
    )
    source_system = SourceSystem(
        id=1,
        code="VENDELO",
        name="Vendelo",
        description="Sistema ecommerce",
        allowlist_domain_id=1,
        is_active=True,
        created_by_user_id=1,
        created_at=now,
        updated_at=now,
    )
    source_system.allowlist_domain = allowlist

    novelty = Novelty(
        id=novelty_id,
        area_id=1,
        source_system_id=1,
        reported_by_user_id=2,
        assigned_user_id=assigned_user_id,
        reported_shift_id=11,
        reported_session_id=21,
        external_reference="VDL-100",
        order_reference="ORD-100",
        customer_reference="CLI-10",
        title="Pedido con novedad",
        description="Caso operativo del ecommerce.",
        novelty_type="PAGO",
        priority=NoveltyPriority.HIGH.value,
        status=status.value,
        extra_data={"canal": "vendelo"},
        reported_at=now,
        first_action_at=None,
        resolved_at=None,
        closed_at=None,
        created_at=now,
        updated_at=now,
    )
    novelty.area = area
    novelty.source_system = source_system
    novelty.reported_by = reporter
    novelty.assigned_user = assignee
    return novelty


def build_log(*, novelty_id: int) -> NoveltyLog:
    author = build_user(user_id=2, email="employee@kpi.com", role=UserRole.EMPLOYEE)
    log = NoveltyLog(
        id=1,
        novelty_id=novelty_id,
        author_user_id=2,
        shift_id=11,
        session_id=21,
        work_date=date(2026, 4, 11),
        log_type=NoveltyLogType.DAILY_UPDATE.value,
        content="Seguimiento del caso",
        worked_minutes=25,
        status_after=NoveltyStatus.IN_PROGRESS.value,
        logged_at=datetime.now(timezone.utc),
    )
    log.author = author
    return log


def build_kpi_payload(*, user_id: int | None = None) -> dict:
    return {
        "user_id": user_id,
        "user_name": "User 2" if user_id else None,
        "user_email": "employee@kpi.com" if user_id else None,
        "user_role": "EMPLOYEE" if user_id else None,
        "total_novelties": 4,
        "open_count": 1,
        "in_progress_count": 2,
        "blocked_count": 0,
        "resolved_count": 0,
        "closed_count": 1,
        "backlog_count": 3,
        "assigned_count": 3,
        "unassigned_count": 1,
        "log_entry_count": 5,
        "logged_novelty_count": 3,
        "total_logged_minutes": 120,
        "average_logged_minutes_per_novelty": 40.0,
        "average_time_to_first_action_minutes": 35.0,
        "average_resolution_minutes": 180.0,
        "first_reported_at": datetime(2026, 4, 10, 12, 0, tzinfo=timezone.utc).isoformat(),
        "last_reported_at": datetime(2026, 4, 11, 12, 0, tzinfo=timezone.utc).isoformat(),
        "priorities": [{"key": "HIGH", "label": "HIGH", "count": 2}],
        "statuses": [{"key": "IN_PROGRESS", "label": "IN_PROGRESS", "count": 2}],
        "areas": [{"key": "Novedades", "label": "Novedades", "count": 4}],
        "source_systems": [{"key": "Vendelo", "label": "Vendelo", "count": 4}],
        "novelty_types": [{"key": "PAGO", "label": "PAGO", "count": 2}],
    }


class FakeNoveltyService:
    def __init__(self):
        self.novelty = build_novelty(novelty_id=1)
        self.last_area_filter = None
        self.last_source_system_filter = None

    def list_areas(self, *, is_active=None):
        self.last_area_filter = is_active
        return [self.novelty.area]

    def create_area(self, *, code, name, description, is_active, created_by_user_id):
        area = self.novelty.area
        area.code = code
        area.name = name
        area.description = description
        area.is_active = is_active
        area.created_by_user_id = created_by_user_id
        return area

    def set_area_status(self, *, area_id: int, is_active: bool):
        self.novelty.area.is_active = is_active
        return self.novelty.area

    def list_source_systems(self, *, is_active=None):
        self.last_source_system_filter = is_active
        return [self.novelty.source_system]

    def create_source_system(self, *, code, name, description, allowlist_domain_id, is_active, created_by_user_id):
        source_system = self.novelty.source_system
        source_system.code = code
        source_system.name = name
        source_system.description = description
        source_system.allowlist_domain_id = allowlist_domain_id
        source_system.is_active = is_active
        source_system.created_by_user_id = created_by_user_id
        return source_system

    def set_source_system_status(self, *, source_system_id: int, is_active: bool):
        self.novelty.source_system.is_active = is_active
        return self.novelty.source_system

    def list_my_novelties(self, **kwargs):
        return [self.novelty]

    def list_novelties(self, **kwargs):
        return [self.novelty]

    def get_novelty(self, *, novelty_id: int, actor: User):
        return self.novelty

    def create_novelty(self, **kwargs):
        return self.novelty

    def update_novelty(self, **kwargs):
        return self.novelty

    def assign_novelty(self, **kwargs):
        return self.novelty

    def set_novelty_status(self, **kwargs):
        self.novelty.status = NoveltyStatus.IN_PROGRESS.value
        return self.novelty

    def list_logs(self, **kwargs):
        return [build_log(novelty_id=self.novelty.id)]

    def create_log(self, **kwargs):
        return build_log(novelty_id=self.novelty.id)


class FakeNoveltyKpiService:
    def get_user_overview(self, *, user_id: int, reported_from=None, reported_to=None):
        return build_kpi_payload(user_id=user_id)

    def get_global_overview(self, *, reported_from=None, reported_to=None):
        return build_kpi_payload()


class NoveltiesApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.novelty_service = FakeNoveltyService()
        self.novelty_kpi_service = FakeNoveltyKpiService()

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    def test_admin_can_create_operational_area(self) -> None:
        app.dependency_overrides[get_current_user] = lambda: build_user(
            user_id=1,
            email="admin@kpi.com",
            role=UserRole.ADMIN,
        )
        app.dependency_overrides[get_novelty_service] = lambda: self.novelty_service

        response = self.client.post(
            "/novelties/areas",
            json={
                "code": "VENDELO_OPS",
                "name": "Vendelo OPS",
                "description": "Gestion diaria ecommerce",
                "is_active": True,
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["code"], "VENDELO_OPS")

    def test_employee_can_list_active_operational_areas_for_novelty_creation(self) -> None:
        app.dependency_overrides[get_current_user] = lambda: build_user(
            user_id=2,
            email="employee@kpi.com",
            role=UserRole.EMPLOYEE,
        )
        app.dependency_overrides[get_novelty_service] = lambda: self.novelty_service

        response = self.client.get("/novelties/areas?is_active=false")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertTrue(self.novelty_service.last_area_filter)

    def test_employee_can_create_novelty(self) -> None:
        app.dependency_overrides[get_current_user] = lambda: build_user(
            user_id=2,
            email="employee@kpi.com",
            role=UserRole.EMPLOYEE,
        )
        app.dependency_overrides[get_novelty_service] = lambda: self.novelty_service

        response = self.client.post(
            "/novelties",
            json={
                "area_id": 1,
                "source_system_id": 1,
                "assigned_user_id": 2,
                "external_reference": "VDL-100",
                "order_reference": "ORD-100",
                "customer_reference": "CLI-10",
                "title": "Pedido con novedad",
                "description": "Caso operativo del ecommerce que requiere seguimiento diario.",
                "novelty_type": "PAGO",
                "priority": "HIGH",
                "extra_data": {"canal": "vendelo"},
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["title"], "Pedido con novedad")
        self.assertEqual(response.json()["source_system"]["code"], "VENDELO")

    def test_employee_can_list_active_source_systems_for_novelty_creation(self) -> None:
        app.dependency_overrides[get_current_user] = lambda: build_user(
            user_id=2,
            email="employee@kpi.com",
            role=UserRole.EMPLOYEE,
        )
        app.dependency_overrides[get_novelty_service] = lambda: self.novelty_service

        response = self.client.get("/novelties/source-systems?is_active=false")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertTrue(self.novelty_service.last_source_system_filter)

    def test_supervisor_can_list_global_novelties(self) -> None:
        app.dependency_overrides[get_current_user] = lambda: build_user(
            user_id=10,
            email="supervisor@kpi.com",
            role=UserRole.SUPERVISOR,
        )
        app.dependency_overrides[get_novelty_service] = lambda: self.novelty_service

        response = self.client.get("/novelties")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_employee_cannot_list_global_novelties(self) -> None:
        app.dependency_overrides[get_current_user] = lambda: build_user(
            user_id=2,
            email="employee@kpi.com",
            role=UserRole.EMPLOYEE,
        )
        app.dependency_overrides[get_novelty_service] = lambda: self.novelty_service

        response = self.client.get("/novelties")

        self.assertEqual(response.status_code, 403)

    def test_employee_can_add_log_to_own_novelty(self) -> None:
        app.dependency_overrides[get_current_user] = lambda: build_user(
            user_id=2,
            email="employee@kpi.com",
            role=UserRole.EMPLOYEE,
        )
        app.dependency_overrides[get_novelty_service] = lambda: self.novelty_service

        response = self.client.post(
            "/novelties/1/logs",
            json={
                "work_date": "2026-04-11",
                "log_type": "DAILY_UPDATE",
                "content": "Se revisa el caso y se deja seguimiento con el operador.",
                "worked_minutes": 25,
                "status_after": "IN_PROGRESS",
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["log_type"], "DAILY_UPDATE")
        self.assertEqual(response.json()["worked_minutes"], 25)

    def test_employee_can_get_own_novelty_kpis(self) -> None:
        app.dependency_overrides[get_current_user] = lambda: build_user(
            user_id=2,
            email="employee@kpi.com",
            role=UserRole.EMPLOYEE,
        )
        app.dependency_overrides[get_novelty_kpi_service] = lambda: self.novelty_kpi_service

        response = self.client.get("/novelties/kpis/me")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["user_id"], 2)
        self.assertEqual(response.json()["total_novelties"], 4)

    def test_employee_cannot_get_global_novelty_kpis(self) -> None:
        app.dependency_overrides[get_current_user] = lambda: build_user(
            user_id=2,
            email="employee@kpi.com",
            role=UserRole.EMPLOYEE,
        )
        app.dependency_overrides[get_novelty_kpi_service] = lambda: self.novelty_kpi_service

        response = self.client.get("/novelties/kpis/overview")

        self.assertEqual(response.status_code, 403)


if __name__ == "__main__":
    unittest.main()
