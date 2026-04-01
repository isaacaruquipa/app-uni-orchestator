"""Database connection and session management.

The database URL is read from the DATABASE_URL environment variable.
If the variable is not set the module falls back to an in-process
SQLite database so that tests and local development can run without
a running PostgreSQL instance.
"""

import os

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session

from backend.db.base import Base

_DATABASE_URL: str = os.environ.get(
    "DATABASE_URL", "sqlite+pysqlite:///:memory:"
)

_engine = create_engine(
    _DATABASE_URL,
    echo=False,
    future=True,
    connect_args={"check_same_thread": False} if "sqlite" in _DATABASE_URL else {},
)

_SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


def get_engine():
    return _engine


def get_session() -> Session:
    return _SessionLocal()


def init_db() -> None:
    """Create all tables defined in the ORM models.

    In production this should be replaced by a proper migration tool
    (e.g. Alembic).  For the purposes of this implementation
    ``Base.metadata.create_all`` is used so that the schema is always
    in sync with the model definitions without requiring a separate
    migration step.
    """
    # Import all model modules so that SQLAlchemy registers them on Base.
    import backend.db.models.auth       # noqa: F401
    import backend.db.models.academic   # noqa: F401
    import backend.db.models.finance    # noqa: F401
    import backend.db.models.marketing  # noqa: F401
    import backend.db.models.content    # noqa: F401
    import backend.db.models.ai         # noqa: F401

    Base.metadata.create_all(bind=_engine)


def reset_db() -> None:
    """Drop and recreate all tables (useful for tests)."""
    import backend.db.models.auth       # noqa: F401
    import backend.db.models.academic   # noqa: F401
    import backend.db.models.finance    # noqa: F401
    import backend.db.models.marketing  # noqa: F401
    import backend.db.models.content    # noqa: F401
    import backend.db.models.ai         # noqa: F401

    Base.metadata.drop_all(bind=_engine)
    Base.metadata.create_all(bind=_engine)
