from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base   # ✅ FIXED

from app.config.settings import get_settings

settings = get_settings()


def parse_echo(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        low = value.lower()
        if low in ("true", "1", "yes"):
            return True
        if low in ("false", "0", "no"):
            return False
        if low == "debug":
            return "debug"
    return False


engine = create_engine(
    settings.database_url,
    echo=parse_echo(settings.db_echo),
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
