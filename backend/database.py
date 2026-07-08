from sqlalchemy import create_engine

from sqlalchemy.orm import (
    sessionmaker,
    declarative_base
)

from config import (
    DATABASE_URL
)


# =========================================================
# ENGINE
# =========================================================

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=30
)


# =========================================================
# SESSION
# =========================================================

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


# =========================================================
# BASE
# =========================================================

Base = declarative_base()


# =========================================================
# DB DEP
# =========================================================

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
