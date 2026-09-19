"""Pytest Configuration

Fixtures and configuration for the test suite.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.core.database import Base, get_db
from app.main import app

# Test database URL (use separate test database)
TEST_DATABASE_URL = str(settings.DATABASE_URL).replace(
    "/aaspaas_dev", "/aaspaas_test"
)

# Create test engine
test_engine = create_engine(
    TEST_DATABASE_URL,
    echo=False,
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
    """
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    yield test_engine
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
