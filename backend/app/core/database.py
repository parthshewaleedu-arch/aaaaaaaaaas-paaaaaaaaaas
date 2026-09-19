"""Database Configuration

SQLAlchemy setup, session management, and database utilities.
"""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

# Create SQLAlchemy engine
engine = create_engine(
    str(settings.DATABASE_URL),
    echo=settings.DATABASE_ECHO,  # Log SQL queries in development
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=10,  # Connection pool size
    max_overflow=20,  # Max connections beyond pool_size
)

# Create SessionLocal class
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Create Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency to get database session.

    This is used as a FastAPI dependency to provide database sessions
    to route handlers. The session is automatically closed after the request.

    Example:
        @router.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()

    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initialize database.

    This creates all tables defined in models.
    In production, use Alembic migrations instead.
    """
    # Import all models here to ensure they are registered with Base
    # from app.models import user, student, business, etc.
    Base.metadata.create_all(bind=engine)
