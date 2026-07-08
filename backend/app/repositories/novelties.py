from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload

from app.models.allowlist_domain import AllowlistDomain
from app.models.novelty import Novelty
from app.models.novelty_log import NoveltyLog
from app.models.operational_area import OperationalArea
from app.models.source_system import SourceSystem
from app.models.user import User
from app.repositories.contracts import NoveltyRepositoryProtocol


class NoveltyRepository(NoveltyRepositoryProtocol):
    def __init__(self, db: Session):
        self.db = db

    def list_areas(self, *, is_active: bool | None = None) -> list[OperationalArea]:
        query = self.db.query(OperationalArea)
        if is_active is not None:
            query = query.filter(OperationalArea.is_active == is_active)
        return query.order_by(OperationalArea.name.asc()).all()

    def get_area_by_id(self, area_id: int) -> OperationalArea | None:
        return self.db.get(OperationalArea, area_id)

    def get_area_by_code(self, code: str) -> OperationalArea | None:
        return self.db.query(OperationalArea).filter(OperationalArea.code == code).first()

    def get_area_by_name(self, name: str) -> OperationalArea | None:
        return self.db.query(OperationalArea).filter(OperationalArea.name == name).first()

    def create_area(
        self,
        *,
        code: str,
        name: str,
        description: str | None,
        is_active: bool,
        created_by_user_id: int | None,
    ) -> OperationalArea:
        area = OperationalArea(
            code=code,
            name=name,
            description=description,
            is_active=is_active,
            created_by_user_id=created_by_user_id,
        )
        self.db.add(area)
        return area

    def list_source_systems(self, *, is_active: bool | None = None) -> list[SourceSystem]:
        query = self.db.query(SourceSystem).options(selectinload(SourceSystem.allowlist_domain))
        if is_active is not None:
            query = query.filter(SourceSystem.is_active == is_active)
        return query.order_by(SourceSystem.name.asc()).all()

    def get_source_system_by_id(self, source_system_id: int) -> SourceSystem | None:
        return (
            self.db.query(SourceSystem)
            .options(selectinload(SourceSystem.allowlist_domain))
            .filter(SourceSystem.id == source_system_id)
            .first()
        )

    def get_source_system_by_code(self, code: str) -> SourceSystem | None:
        return self.db.query(SourceSystem).filter(SourceSystem.code == code).first()

    def get_source_system_by_name(self, name: str) -> SourceSystem | None:
        return self.db.query(SourceSystem).filter(SourceSystem.name == name).first()

    def create_source_system(
        self,
        *,
        code: str,
        name: str,
        description: str | None,
        allowlist_domain_id: int | None,
        is_active: bool,
        created_by_user_id: int | None,
    ) -> SourceSystem:
        source_system = SourceSystem(
            code=code,
            name=name,
            description=description,
            allowlist_domain_id=allowlist_domain_id,
            is_active=is_active,
            created_by_user_id=created_by_user_id,
        )
        self.db.add(source_system)
        return source_system

    def get_allowlist_domain_by_id(self, allowlist_domain_id: int) -> AllowlistDomain | None:
        return self.db.get(AllowlistDomain, allowlist_domain_id)

    def list_novelties(
        self,
        *,
        involved_user_id: int | None = None,
        area_id: int | None = None,
        source_system_id: int | None = None,
        assigned_user_id: int | None = None,
        reported_by_user_id: int | None = None,
        status: str | None = None,
        priority: str | None = None,
        novelty_type: str | None = None,
        reported_from: datetime | None = None,
        reported_to: datetime | None = None,
        limit: int | None = 200,
    ) -> list[Novelty]:
        query = self.db.query(Novelty).options(
            selectinload(Novelty.area),
            selectinload(Novelty.source_system).selectinload(SourceSystem.allowlist_domain),
            selectinload(Novelty.reported_by),
            selectinload(Novelty.assigned_user),
        )
        if involved_user_id is not None:
            query = query.filter(
                or_(
                    Novelty.reported_by_user_id == involved_user_id,
                    Novelty.assigned_user_id == involved_user_id,
                )
            )
        if area_id is not None:
            query = query.filter(Novelty.area_id == area_id)
        if source_system_id is not None:
            query = query.filter(Novelty.source_system_id == source_system_id)
        if assigned_user_id is not None:
            query = query.filter(Novelty.assigned_user_id == assigned_user_id)
        if reported_by_user_id is not None:
            query = query.filter(Novelty.reported_by_user_id == reported_by_user_id)
        if status is not None:
            query = query.filter(Novelty.status == status)
        if priority is not None:
            query = query.filter(Novelty.priority == priority)
        if novelty_type is not None:
            query = query.filter(Novelty.novelty_type == novelty_type)
        if reported_from is not None:
            query = query.filter(Novelty.reported_at >= reported_from)
        if reported_to is not None:
            query = query.filter(Novelty.reported_at <= reported_to)

        query = query.order_by(Novelty.reported_at.desc(), Novelty.id.desc())
        if limit is not None:
            query = query.limit(limit)
        return query.all()

    def get_novelty_by_id(self, novelty_id: int) -> Novelty | None:
        return (
            self.db.query(Novelty)
            .options(
                selectinload(Novelty.area),
                selectinload(Novelty.source_system).selectinload(SourceSystem.allowlist_domain),
                selectinload(Novelty.reported_by),
                selectinload(Novelty.assigned_user),
            )
            .filter(Novelty.id == novelty_id)
            .first()
        )

    def create_novelty(
        self,
        *,
        area_id: int,
        source_system_id: int,
        reported_by_user_id: int,
        assigned_user_id: int | None,
        reported_shift_id: int | None,
        reported_session_id: int | None,
        external_reference: str | None,
        order_reference: str | None,
        customer_reference: str | None,
        title: str,
        description: str,
        novelty_type: str,
        priority: str,
        status: str,
        extra_data: dict | None,
        reported_at: datetime,
    ) -> Novelty:
        novelty = Novelty(
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
        )
        self.db.add(novelty)
        self.db.flush()
        return novelty

    def list_logs(self, *, novelty_id: int) -> list[NoveltyLog]:
        return (
            self.db.query(NoveltyLog)
            .options(selectinload(NoveltyLog.author))
            .filter(NoveltyLog.novelty_id == novelty_id)
            .order_by(NoveltyLog.work_date.desc(), NoveltyLog.logged_at.desc(), NoveltyLog.id.desc())
            .all()
        )

    def list_logs_for_novelties(self, *, novelty_ids: list[int]) -> list[NoveltyLog]:
        if not novelty_ids:
            return []
        return (
            self.db.query(NoveltyLog)
            .options(selectinload(NoveltyLog.author))
            .filter(NoveltyLog.novelty_id.in_(novelty_ids))
            .order_by(NoveltyLog.work_date.desc(), NoveltyLog.logged_at.desc(), NoveltyLog.id.desc())
            .all()
        )

    def get_log_by_id(self, log_id: int) -> NoveltyLog | None:
        return (
            self.db.query(NoveltyLog)
            .options(selectinload(NoveltyLog.author))
            .filter(NoveltyLog.id == log_id)
            .first()
        )

    def create_log(
        self,
        *,
        novelty_id: int,
        author_user_id: int,
        shift_id: int | None,
        session_id: int | None,
        work_date: date,
        log_type: str,
        content: str,
        worked_minutes: int | None,
        status_after: str | None,
        logged_at: datetime,
    ) -> NoveltyLog:
        log = NoveltyLog(
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
        self.db.add(log)
        self.db.flush()
        return log

    def get_user_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def commit(self) -> None:
        self.db.commit()

    def refresh(self, instance: object) -> None:
        self.db.refresh(instance)
