"""Unit tests for Pilot Campus Database Seeding Script.

Verifies:
1. Creation of platform administrator, college, campus, categories, and businesses.
2. Idempotency: Multiple runs do not duplicate or fail on existing records.
"""

from unittest.mock import MagicMock
from uuid import uuid4

from app.core.seed import seed_database
from app.models.user import User


def test_seed_database_execution_flow():
    """Verify seed_database execution queries existing records and adds missing records."""
    db_mock = MagicMock()
    # Mock query to return None initially so entities are created
    db_mock.query.return_value.filter.return_value.first.return_value = None

    stats = seed_database(db_mock)

    assert stats["users"] >= 4  # 1 admin + 3 merchants
    assert stats["colleges"] == 1
    assert stats["campuses"] == 1
    assert stats["categories"] >= 5
    assert stats["dimensions"] >= 10
    assert stats["businesses"] == 3
    assert stats["services"] >= 8

    # Verify db.commit was called
    db_mock.commit.assert_called()


def test_seed_database_idempotent_when_records_exist():
    """Verify seed_database skips creation when entities are already present."""
    db_mock = MagicMock()

    dummy_user = User(id=uuid4(), email="admin@aaspaas.com")
    db_mock.query.return_value.filter.return_value.first.return_value = dummy_user

    stats = seed_database(db_mock)

    # When all entities already exist, 0 new items should be created
    assert stats["users"] == 0
    assert stats["colleges"] == 0
    assert stats["campuses"] == 0
    assert stats["businesses"] == 0
    assert stats["services"] == 0

    db_mock.commit.assert_called()
