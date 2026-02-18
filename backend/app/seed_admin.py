from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.user import User


def run():
    db: Session = SessionLocal()
    try:
        email = "admin@kpi.com"
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print("Admin ya existe:", existing.email)
            return

        admin = User(
            name="Admin",
            email=email,
            password_hash=hash_password("Admin123*"),
            role="ADMIN",
            is_active=True,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print("Admin creado:", admin.id, admin.email)
    finally:
        db.close()


if __name__ == "__main__":
    run()
