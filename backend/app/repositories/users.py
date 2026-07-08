from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.contracts import UserRepositoryProtocol


class UserRepository(UserRepositoryProtocol):
    def __init__(self, db: Session):
        self.db = db

    def list_all(
        self,
        *,
        is_active: bool | None = None,
        role: str | None = None,
    ) -> list[User]:
        query = self.db.query(User)
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        if role is not None:
            query = query.filter(User.role == role)
        return query.order_by(User.name.asc(), User.email.asc()).all()

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

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
            name=name,
            email=email,
            password_hash=password_hash,
            role=role,
            is_active=is_active,
        )
        self.db.add(user)
        return user

    def commit(self) -> None:
        self.db.commit()

    def refresh(self, instance: object) -> None:
        self.db.refresh(instance)
