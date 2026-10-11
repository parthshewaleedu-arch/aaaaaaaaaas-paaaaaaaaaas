"""Test Database Configuration

Tests for database setup and session management.
"""

from sqlalchemy.orm import Session

from app.core.database import Base, get_db


def test_database_session_created(db: Session):
    """Test that database session is created correctly."""
    assert db is not None
    assert isinstance(db, Session)


def test_get_db_dependency():
    """Test get_db dependency creates and closes session."""
    # Get generator
    gen = get_db()

    # Get session
    db = next(gen)
    assert db is not None
    assert isinstance(db, Session)

    # Close session (this happens automatically in FastAPI)
    try:
        next(gen)
    except StopIteration:
        pass  # Expected behavior


def test_base_metadata_exists():
    """Test that Base has metadata for models."""
    assert Base.metadata is not None

    # Initially no tables (models not imported yet)
    # This will change when we add models in Phase 2
    assert isinstance(Base.metadata.tables, dict)
