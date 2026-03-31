from datetime import datetime, timezone
import unittest

from bootstrap import configure_test_environment

configure_test_environment()

from fastapi.testclient import TestClient

from app.core.deps import get_current_user, get_operational_kpi_service
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


def build_overview(*, user_id: int | None = None) -> dict:
    now = datetime.now(timezone.utc)
    return {
        "user_id": user_id,
        "user_name": "User 2" if user_id else None,
        "user_email": "user2@kpi.com" if user_id else None,
        "user_role": "EMPLOYEE" if user_id else None,
        "shift_count": 1,
        "closed_shift_count": 1,
        "open_shift_count": 0,
        "session_count": 1,
        "open_session_count": 0,
        "total_shift_seconds": 600,
        "total_session_seconds": 600,
        "total_active_seconds": 300,
        "total_idle_seconds": 60,
        "total_tracked_seconds": 360,
        "total_untracked_session_seconds": 240,
        "activity_coverage_rate": 0.6,
        "active_rate": 0.8333,
        "idle_rate": 0.1667,
        "event_count": 5,
        "page_view_count": 1,
        "heartbeat_count": 2,
        "idle_event_count": 1,
        "resume_count": 1,
        "distinct_domain_count": 1,
        "first_activity_at": now.isoformat(),
        "last_activity_at": now.isoformat(),
        "punctuality_supported": True,
        "punctuality_reason": None,
        "scheduled_shift_count": 1,
        "punctuality_evaluated_shift_count": 1,
        "punctual_shift_count": 1,
        "late_shift_count": 0,
        "unscheduled_shift_count": 0,
        "punctuality_rate": 1.0,
        "average_late_by_minutes": 0.0,
        "max_late_by_minutes": 0,
        "average_start_delay_minutes": 0.0,
        "max_start_delay_minutes": 0,
        "domains": [
            {
                "source_domain": "portal.example.com",
                "event_count": 5,
                "page_view_count": 1,
                "heartbeat_count": 2,
                "idle_event_count": 1,
                "active_seconds": 300,
                "idle_seconds": 60,
            }
        ],
        "event_types": [
            {"event_type": "PAGE_VIEW", "count": 1, "tracked_seconds": 0},
            {"event_type": "HEARTBEAT", "count": 2, "tracked_seconds": 300},
            {"event_type": "IDLE", "count": 1, "tracked_seconds": 60},
            {"event_type": "RESUME", "count": 1, "tracked_seconds": 0},
        ],
    }


class FakeOperationalKpiService:
    def get_overview(self, *, started_from=None, started_to=None, limit=200):
        return build_overview()

    def get_user_overview(self, *, user_id: int, started_from=None, started_to=None, limit=200):
        return build_overview(user_id=user_id)

    def get_shift_overview(self, *, shift_id: int):
        overview = build_overview(user_id=2)
        overview.update(
            {
                "shift_id": shift_id,
                "shift_status": "CLOSED",
                "shift_started_at": datetime.now(timezone.utc).isoformat(),
                "shift_ended_at": datetime.now(timezone.utc).isoformat(),
                "device_labels": ["PC-01"],
                "is_scheduled": True,
                "is_punctual": True,
                "late_by_minutes": 0,
                "start_delay_minutes": 0,
                "scheduled_start_at": datetime.now(timezone.utc).isoformat(),
                "scheduled_end_at": datetime.now(timezone.utc).isoformat(),
                "grace_deadline_at": datetime.now(timezone.utc).isoformat(),
                "schedule_template_id": 1,
                "schedule_template_name": "Horario oficina",
                "schedule_timezone_name": "America/Bogota",
            }
        )
        return overview


class KpisApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.kpi_service = FakeOperationalKpiService()

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    def test_employee_can_get_own_kpi_overview(self) -> None:
        app.dependency_overrides[get_current_user] = lambda: build_user(
            user_id=2,
            email="employee@kpi.com",
            role=UserRole.EMPLOYEE,
        )
        app.dependency_overrides[get_operational_kpi_service] = lambda: self.kpi_service

        response = self.client.get("/kpis/me/overview")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["user_id"], 2)
        self.assertEqual(response.json()["total_active_seconds"], 300)

    def test_employee_cannot_get_global_kpi_overview(self) -> None:
        app.dependency_overrides[get_current_user] = lambda: build_user(
            user_id=2,
            email="employee@kpi.com",
            role=UserRole.EMPLOYEE,
        )
        app.dependency_overrides[get_operational_kpi_service] = lambda: self.kpi_service

        response = self.client.get("/kpis/overview")

        self.assertEqual(response.status_code, 403)

    def test_supervisor_can_get_global_kpi_overview(self) -> None:
        app.dependency_overrides[get_current_user] = lambda: build_user(
            user_id=10,
            email="supervisor@kpi.com",
            role=UserRole.SUPERVISOR,
        )
        app.dependency_overrides[get_operational_kpi_service] = lambda: self.kpi_service

        response = self.client.get("/kpis/overview")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["shift_count"], 1)
        self.assertIsNone(response.json()["user_id"])

    def test_supervisor_can_get_shift_kpi_overview(self) -> None:
        app.dependency_overrides[get_current_user] = lambda: build_user(
            user_id=10,
            email="supervisor@kpi.com",
            role=UserRole.SUPERVISOR,
        )
        app.dependency_overrides[get_operational_kpi_service] = lambda: self.kpi_service

        response = self.client.get("/kpis/shifts/11")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["shift_id"], 11)
        self.assertEqual(response.json()["device_labels"], ["PC-01"])
        self.assertTrue(response.json()["is_punctual"])


if __name__ == "__main__":
    unittest.main()
