import os


def configure_test_environment() -> None:
    os.environ.setdefault("APP_NAME", "KPI App API Test")
    os.environ.setdefault("DATABASE_URL", "sqlite:///./test_backend.db")
    os.environ.setdefault("JWT_SECRET", "test-secret")
    os.environ.setdefault("JWT_ALG", "HS256")
    os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MIN", "60")
