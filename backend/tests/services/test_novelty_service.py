import unittest
from datetime import date, datetime, timezone

from tests.bootstrap import configure_test_environment

configure_test_environment()

from app.core.exceptions import PermissionDeniedError, ValidationError
from app.domain.enums import NoveltyLogType, NoveltyPriority, NoveltyStatus, UserRole
from app.models.allowlist_domain import AllowlistDomain
from app.models.novelty import Novelty
from app.models.novelty_log import NoveltyLog
from app.models.operational_area import OperationalArea
from app.models.session import Session as WorkSession
from app.models.shift import Shift
from app.models.source_system import SourceSystem
from app.models.user import User
from app.services.novelty_kpis import NoveltyKpiService
from app.services.novelties import NoveltyService


def build_user(
    *,
    user_id: int,
    role: UserRole = UserRole.EMPLOYEE,
    is_active: bool = True,
) -> User:
    return User(
        id=user_id,
        name=f"User {user_id}",
        email=f"user{user_id}@kpi.com",
        password_hash="hashed",
        role=role.value,
        is_active=is_active,
        created_at=datetime.now(timezone.utc),
    )


def build_area(*, area_id: int = 1, code: str = "NOVEDADES", is_active: bool = True) -> OperationalArea:
    now = datetime.now(timezone.utc)
    return OperationalArea(
        id=area_id,
        code=code,
        name="Novedades",
        description="Gestion ecommerce",
        is_active=is_active,
        created_by_user_id=1,
        created_at=now,
        updated_at=now,
    )


def build_source_system(
    *,
    source_system_id: int = 1,
    code: str = "VENDELO",
    is_active: bool = True,
    allowlist_active: bool = True,
) -> SourceSystem:
    now = datetime.now(timezone.utc)
    domain = AllowlistDomain(
        id=9,
        domain="vendelo.example.com",
        description="Vendelo",
        is_active=allowlist_active,
        created_by_user_id=1,
        created_at=now,
        updated_at=now,
    )
    source = SourceSystem(
        id=source_system_id,
        code=code,
        name="Vendelo",
        description="Sistema ecommerce",
        allowlist_domain_id=domain.id,
        is_active=is_active,
        created_by_user_id=1,
        created_at=now,
        updated_at=now,
    )
    source.allowlist_domain = domain
    return source


class FakeNoveltyRepository:
    def __init__(self):
        self.areas = [build_area()]
        self.source_systems = [build_source_system()]
        self.users = [
            build_user(user_id=1, role=UserRole.ADMIN),
            build_user(user_id=2, role=UserRole.EMPLOYEE),
            build_user(user_id=3, role=UserRole.EMPLOYEE),
        ]
        self.novelties: list[Novelty] = []
        self.logs: list[NoveltyLog] = []
        self.commits = 0
        self._next_novelty_id = 1
        self._next_log_id = 1

    def list_areas(self, *, is_active=None):
        areas = list(self.areas)
        if is_active is not None:
            areas = [area for area in areas if area.is_active == is_active]
        return areas

    def get_area_by_id(self, area_id: int):
        return next((area for area in self.areas if area.id == area_id), None)

    def get_area_by_code(self, code: str):
        return next((area for area in self.areas if area.code == code), None)

    def get_area_by_name(self, name: str):
        return next((area for area in self.areas if area.name == name), None)

    def create_area(self, *, code, name, description, is_active, created_by_user_id):
        now = datetime.now(timezone.utc)
        area = OperationalArea(
            id=len(self.areas) + 1,
            code=code,
            name=name,
            description=description,
            is_active=is_active,
            created_by_user_id=created_by_user_id,
            created_at=now,
            updated_at=now,
        )
        self.areas.append(area)
        return area

    def list_source_systems(self, *, is_active=None):
        systems = list(self.source_systems)
        if is_active is not None:
            systems = [system for system in systems if system.is_active == is_active]
        return systems

    def get_source_system_by_id(self, source_system_id: int):
        return next((item for item in self.source_systems if item.id == source_system_id), None)

    def get_source_system_by_code(self, code: str):
        return next((item for item in self.source_systems if item.code == code), None)

    def get_source_system_by_name(self, name: str):
        return next((item for item in self.source_systems if item.name == name), None)

    def create_source_system(self, *, code, name, description, allowlist_domain_id, is_active, created_by_user_id):
        now = datetime.now(timezone.utc)
        allowlist_domain = self.get_allowlist_domain_by_id(allowlist_domain_id) if allowlist_domain_id else None
        source = SourceSystem(
            id=len(self.source_systems) + 1,
            code=code,
            name=name,
            description=description,
            allowlist_domain_id=allowlist_domain_id,
            is_active=is_active,
            created_by_user_id=created_by_user_id,
            created_at=now,
            updated_at=now,
        )
        source.allowlist_domain = allowlist_domain
        self.source_systems.append(source)
        return source

    def get_allowlist_domain_by_id(self, allowlist_domain_id: int):
        for source_system in self.source_systems:
            if (
                source_system.allowlist_domain is not None
                and source_system.allowlist_domain.id == allowlist_domain_id
            ):
                return source_system.allowlist_domain
        return None

    def list_novelties(
        self,
        *,
        involved_user_id=None,
        area_id=None,
        source_system_id=None,
        assigned_user_id=None,
        reported_by_user_id=None,
        status=None,
        priority=None,
        novelty_type=None,
        reported_from=None,
        reported_to=None,
        limit=200,
    ):
        novelties = list(self.novelties)
        if involved_user_id is not None:
            novelties = [
                novelty
                for novelty in novelties
                if novelty.reported_by_user_id == involved_user_id or novelty.assigned_user_id == involved_user_id
            ]
        if area_id is not None:
            novelties = [novelty for novelty in novelties if novelty.area_id == area_id]
        if source_system_id is not None:
            novelties = [novelty for novelty in novelties if novelty.source_system_id == source_system_id]
        if assigned_user_id is not None:
            novelties = [novelty for novelty in novelties if novelty.assigned_user_id == assigned_user_id]
        if reported_by_user_id is not None:
            novelties = [novelty for novelty in novelties if novelty.reported_by_user_id == reported_by_user_id]
        if status is not None:
            novelties = [novelty for novelty in novelties if novelty.status == status]
        if priority is not None:
            novelties = [novelty for novelty in novelties if novelty.priority == priority]
        if novelty_type is not None:
            novelties = [novelty for novelty in novelties if novelty.novelty_type == novelty_type]
        if reported_from is not None:
            novelties = [novelty for novelty in novelties if novelty.reported_at >= reported_from]
        if reported_to is not None:
            novelties = [novelty for novelty in novelties if novelty.reported_at <= reported_to]
        novelties = sorted(novelties, key=lambda novelty: (novelty.reported_at, novelty.id), reverse=True)
        return novelties if limit is None else novelties[:limit]

    def get_novelty_by_id(self, novelty_id: int):
        return next((novelty for novelty in self.novelties if novelty.id == novelty_id), None)

    def create_novelty(
        self,
        *,
        area_id,
        source_system_id,
        reported_by_user_id,
        assigned_user_id,
        reported_shift_id,
        reported_session_id,
        external_reference,
        order_reference,
        customer_reference,
        title,
        description,
        novelty_type,
        priority,
        status,
        extra_data,
        reported_at,
    ):
        now = datetime.now(timezone.utc)
        novelty = Novelty(
            id=self._next_novelty_id,
            area_id=area_id,
            source_system_id=source_system_id,
            reported_by_user_id=reported_by_user_id,
            assigned_user_id=assigned_user_id,
            reported_shift_id=reported_shift_id,
            reported_session_id=reported_session_id,
            external_reference=external_reference,
            order_reference=order_reference,
            customer_reference=customer_reference,
            title=title,
            description=description,
            novelty_type=novelty_type,
            priority=priority,
            status=status,
            extra_data=extra_data,
            reported_at=reported_at,
            first_action_at=None,
            resolved_at=None,
            closed_at=None,
            created_at=now,
            updated_at=now,
        )
        novelty.area = self.get_area_by_id(area_id)
        novelty.source_system = self.get_source_system_by_id(source_system_id)
        novelty.reported_by = self.get_user_by_id(reported_by_user_id)
        novelty.assigned_user = self.get_user_by_id(assigned_user_id) if assigned_user_id else None
        self._next_novelty_id += 1
        self.novelties.append(novelty)
        return novelty

    def list_logs(self, *, novelty_id: int):
        return [log for log in self.logs if log.novelty_id == novelty_id]

    def list_logs_for_novelties(self, *, novelty_ids: list[int]):
        return [log for log in self.logs if log.novelty_id in novelty_ids]

    def get_log_by_id(self, log_id: int):
        return next((log for log in self.logs if log.id == log_id), None)

    def create_log(
        self,
        *,
        novelty_id,
        author_user_id,
        shift_id,
        session_id,
        work_date,
        log_type,
        content,
        worked_minutes,
        status_after,
        logged_at,
    ):
        log = NoveltyLog(
            id=self._next_log_id,
            novelty_id=novelty_id,
            author_user_id=author_user_id,
            shift_id=shift_id,
            session_id=session_id,
            work_date=work_date,
            log_type=log_type,
            content=content,
            worked_minutes=worked_minutes,
            status_after=status_after,
            logged_at=logged_at,
        )
        log.author = self.get_user_by_id(author_user_id)
        self._next_log_id += 1
        self.logs.append(log)
        return log

    def get_user_by_id(self, user_id: int):
        return next((user for user in self.users if user.id == user_id), None)

    def commit(self):
        self.commits += 1

    def refresh(self, instance):
        return None


class FakeShiftWorkRepository:
    def __init__(self):
        self.shift = Shift(
            id=11,
            user_id=2,
            start_at=datetime(2026, 4, 11, 12, 0, tzinfo=timezone.utc),
            end_at=None,
            status="OPEN",
        )
        self.session = WorkSession(
            id=21,
            user_id=2,
            shift_id=11,
            start_at=datetime(2026, 4, 11, 12, 0, tzinfo=timezone.utc),
            end_at=None,
            status="OPEN",
            device_label="PC-ECOM-01",
        )

    def get_open_shift_for_user(self, user_id: int):
        return self.shift if user_id == self.shift.user_id else None

    def get_open_session_for_shift(self, shift_id: int):
        return self.session if shift_id == self.session.shift_id else None


class NoveltyServiceTests(unittest.TestCase):
    def test_create_novelty_defaults_employee_assignment_and_links_open_context(self) -> None:
        repository = FakeNoveltyRepository()
        service = NoveltyService(
            novelty_repository=repository,
            shift_work_repository=FakeShiftWorkRepository(),
        )

        novelty = service.create_novelty(
            actor=repository.get_user_by_id(2),
            area_id=1,
            source_system_id=1,
            assigned_user_id=None,
            external_reference="VDL-001",
            order_reference="ORD-100",
            customer_reference="CLI-55",
            title="Pedido con novedad de pago",
            description="El cliente reporta rechazo en pasarela y requiere validacion manual.",
            novelty_type="PAGO",
            priority=NoveltyPriority.HIGH,
            reported_at=datetime(2026, 4, 11, 13, 0, tzinfo=timezone.utc),
            extra_data={"canal": "vendelo"},
        )

        self.assertEqual(novelty.assigned_user_id, 2)
        self.assertEqual(novelty.reported_shift_id, 11)
        self.assertEqual(novelty.reported_session_id, 21)
        self.assertEqual(novelty.status, NoveltyStatus.OPEN.value)
        self.assertEqual(repository.commits, 1)

    def test_create_source_system_rejects_inactive_allowlist_domain(self) -> None:
        repository = FakeNoveltyRepository()
        repository.source_systems[0].allowlist_domain.is_active = False
        service = NoveltyService(
            novelty_repository=repository,
            shift_work_repository=FakeShiftWorkRepository(),
        )

        with self.assertRaisesRegex(ValidationError, "dominios activos"):
            service.create_source_system(
                code="VENDELO_BOT",
                name="Vendelo Bot",
                description=None,
                allowlist_domain_id=9,
                is_active=True,
                created_by_user_id=1,
            )

    def test_create_log_sets_first_action_and_status(self) -> None:
        repository = FakeNoveltyRepository()
        service = NoveltyService(
            novelty_repository=repository,
            shift_work_repository=FakeShiftWorkRepository(),
        )
        novelty = service.create_novelty(
            actor=repository.get_user_by_id(2),
            area_id=1,
            source_system_id=1,
            assigned_user_id=2,
            external_reference=None,
            order_reference=None,
            customer_reference=None,
            title="Pedido con retraso de despacho",
            description="Se requiere validacion con transportadora y seguimiento diario.",
            novelty_type="DESPACHO",
            priority=NoveltyPriority.MEDIUM,
            reported_at=datetime(2026, 4, 11, 13, 0, tzinfo=timezone.utc),
            extra_data=None,
        )

        log = service.create_log(
            novelty_id=novelty.id,
            actor=repository.get_user_by_id(2),
            work_date=date(2026, 4, 11),
            log_type=NoveltyLogType.DAILY_UPDATE,
            content="Se contacta transportadora y se deja seguimiento para cierre.",
            worked_minutes=35,
            status_after=NoveltyStatus.IN_PROGRESS,
        )

        persisted = repository.get_novelty_by_id(novelty.id)
        self.assertEqual(log.status_after, NoveltyStatus.IN_PROGRESS.value)
        self.assertEqual(persisted.status, NoveltyStatus.IN_PROGRESS.value)
        self.assertIsNotNone(persisted.first_action_at)
        self.assertEqual(log.worked_minutes, 35)

    def test_set_status_rejects_reopening_closed_novelty(self) -> None:
        repository = FakeNoveltyRepository()
        service = NoveltyService(
            novelty_repository=repository,
            shift_work_repository=FakeShiftWorkRepository(),
        )
        novelty = service.create_novelty(
            actor=repository.get_user_by_id(2),
            area_id=1,
            source_system_id=1,
            assigned_user_id=2,
            external_reference=None,
            order_reference=None,
            customer_reference=None,
            title="Pedido duplicado en gestion",
            description="El caso queda resuelto y luego se intenta reabrir fuera del flujo definido.",
            novelty_type="OPERACION",
            priority=NoveltyPriority.MEDIUM,
            reported_at=datetime(2026, 4, 11, 13, 0, tzinfo=timezone.utc),
            extra_data=None,
        )
        service.set_novelty_status(
            novelty_id=novelty.id,
            actor=repository.get_user_by_id(2),
            status=NoveltyStatus.CLOSED,
            note=None,
        )

        with self.assertRaisesRegex(ValidationError, "reabrir"):
            service.set_novelty_status(
                novelty_id=novelty.id,
                actor=repository.get_user_by_id(2),
                status=NoveltyStatus.IN_PROGRESS,
                note=None,
            )

    def test_employee_cannot_admin_update_someone_else_novelty(self) -> None:
        repository = FakeNoveltyRepository()
        service = NoveltyService(
            novelty_repository=repository,
            shift_work_repository=FakeShiftWorkRepository(),
        )
        novelty = service.create_novelty(
            actor=repository.get_user_by_id(2),
            area_id=1,
            source_system_id=1,
            assigned_user_id=2,
            external_reference=None,
            order_reference=None,
            customer_reference=None,
            title="Validacion de fraude",
            description="Caso operativo de fraude con seguimiento del analista asignado.",
            novelty_type="FRAUDE",
            priority=NoveltyPriority.CRITICAL,
            reported_at=datetime(2026, 4, 11, 13, 0, tzinfo=timezone.utc),
            extra_data=None,
        )

        with self.assertRaises(PermissionDeniedError):
            service.update_novelty(
                novelty_id=novelty.id,
                actor=repository.get_user_by_id(3),
                title="Nuevo titulo",
            )


class NoveltyKpiServiceTests(unittest.TestCase):
    def test_get_overview_aggregates_statuses_and_logged_minutes(self) -> None:
        repository = FakeNoveltyRepository()
        now = datetime(2026, 4, 11, 13, 0, tzinfo=timezone.utc)
        novelty_one = repository.create_novelty(
            area_id=1,
            source_system_id=1,
            reported_by_user_id=2,
            assigned_user_id=2,
            reported_shift_id=11,
            reported_session_id=21,
            external_reference="VDL-1",
            order_reference="ORD-1",
            customer_reference=None,
            title="Caso 1",
            description="Caso 1",
            novelty_type="PAGO",
            priority=NoveltyPriority.HIGH.value,
            status=NoveltyStatus.IN_PROGRESS.value,
            extra_data=None,
            reported_at=now,
        )
        novelty_one.first_action_at = now.replace(hour=14)
        novelty_two = repository.create_novelty(
            area_id=1,
            source_system_id=1,
            reported_by_user_id=2,
            assigned_user_id=None,
            reported_shift_id=None,
            reported_session_id=None,
            external_reference="VDL-2",
            order_reference="ORD-2",
            customer_reference=None,
            title="Caso 2",
            description="Caso 2",
            novelty_type="DESPACHO",
            priority=NoveltyPriority.MEDIUM.value,
            status=NoveltyStatus.CLOSED.value,
            extra_data=None,
            reported_at=now.replace(day=10),
        )
        novelty_two.first_action_at = now.replace(day=10, hour=14)
        novelty_two.resolved_at = now.replace(day=10, hour=16)
        repository.create_log(
            novelty_id=novelty_one.id,
            author_user_id=2,
            shift_id=11,
            session_id=21,
            work_date=date(2026, 4, 11),
            log_type=NoveltyLogType.DAILY_UPDATE.value,
            content="Seguimiento uno",
            worked_minutes=30,
            status_after=NoveltyStatus.IN_PROGRESS.value,
            logged_at=now.replace(hour=14),
        )
        repository.create_log(
            novelty_id=novelty_two.id,
            author_user_id=2,
            shift_id=11,
            session_id=21,
            work_date=date(2026, 4, 10),
            log_type=NoveltyLogType.RESOLUTION.value,
            content="Cierre final",
            worked_minutes=45,
            status_after=NoveltyStatus.CLOSED.value,
            logged_at=now.replace(day=10, hour=16),
        )

        service = NoveltyKpiService(novelty_repository=repository)

        overview = service.get_global_overview()

        self.assertEqual(overview["total_novelties"], 2)
        self.assertEqual(overview["in_progress_count"], 1)
        self.assertEqual(overview["closed_count"], 1)
        self.assertEqual(overview["unassigned_count"], 1)
        self.assertEqual(overview["log_entry_count"], 2)
        self.assertEqual(overview["logged_novelty_count"], 2)
        self.assertEqual(overview["total_logged_minutes"], 75)
        self.assertAlmostEqual(overview["average_logged_minutes_per_novelty"], 37.5)
        self.assertAlmostEqual(overview["average_time_to_first_action_minutes"], 60.0)
        self.assertAlmostEqual(overview["average_resolution_minutes"], 180.0)


if __name__ == "__main__":
    unittest.main()
