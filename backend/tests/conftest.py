"""Pytest Configuration

Fixtures and configuration for the test suite.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.core.database import Base, get_db
from app.main import app

# Test database URL - use SQLite for testing if PostgreSQL not available
# SQLite doesn't support all PostgreSQL features (PostGIS, enums, etc.)
# so tests requiring those features will be skipped
try:
    # Try to use PostgreSQL if available
    TEST_DATABASE_URL = str(settings.DATABASE_URL).replace(
        "/aaspaas_dev", "/aaspaas_test"
    )
    # Test connection
    test_engine = create_engine(TEST_DATABASE_URL, echo=False)
    with test_engine.connect() as conn:
        conn.execute("SELECT 1")
    USING_POSTGRESQL = True
except Exception:
    # Fall back to SQLite for basic tests
    TEST_DATABASE_URL = "sqlite:///:memory:"
    test_engine = create_engine(
        TEST_DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    USING_POSTGRESQL = False


# Marker to skip tests that require PostgreSQL-specific features
requires_postgresql = pytest.mark.skipif(
    not USING_POSTGRESQL, reason="Test requires PostgreSQL (PostGIS, enums, UUID types)"
)


# Create test session factory
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


@pytest.fixture(scope="session")
def engine():
    """Create test database engine.

    This fixture is scoped to the session, meaning it's created once
    for all tests and cleaned up at the end.

    Only creates tables if using PostgreSQL (SQLite doesn't support all types).
    """
    if USING_POSTGRESQL:
        # Create all tables
        Base.metadata.create_all(bind=test_engine)
    yield test_engine
    if USING_POSTGRESQL:
        # Drop all tables after tests
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def db(engine) -> Session:
    """Create a new database session for each test.

    This fixture is scoped to the function, meaning each test gets
    a fresh database session that is rolled back after the test.

    Yields:
        Database session
    """
    if not USING_POSTGRESQL:
        pytest.skip("Test requires PostgreSQL")

    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db: Session) -> TestClient:
    """Create FastAPI test client with test database.

    This overrides the get_db dependency to use the test database.

    Args:
        db: Test database session

    Returns:
        FastAPI test client
    """

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client_no_db() -> TestClient:
    """Create FastAPI test client without database dependency.

    Use this for tests that don't require a database connection.
    """
    with TestClient(app) as test_client:
        yield test_client


# Fixture for sample data (will be expanded in future phases)
@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@mitaoe.ac.in",
        "password": "SecurePass123!",
        "full_name": "Test User",
        "role": "STUDENT",
    }


@pytest.fixture
def sample_business_data():
    """Sample business data for testing."""
    return {
        "name": "Test Mess",
        "description": "A test mess for students",
        "phone": "+91 98765 43210",
        "address": "Near MIT AOE Gate 2",
        "latitude": 18.7830,
        "longitude": 73.9375,
        "price_level": "₹",
        "student_discount": True,
    }


@pytest.fixture(autouse=True)
def reset_security_state():
    """Ensure in-memory rate limits and blacklists are cleared between tests."""
    from app.core.rate_limiter import clear_rate_limits
    from app.core.token_blacklist import clear_blacklist

    clear_rate_limits()
    clear_blacklist()
    yield
    clear_rate_limits()
    clear_blacklist()
