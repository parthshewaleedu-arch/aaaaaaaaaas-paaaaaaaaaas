"""Tests for College model"""

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.college import College, CollegeStatus


def test_create_college(db):
    """Test creating a basic college."""
    college = College(
        name="Example University",
        short_name="EU",
        email_domain="example.edu",
    )
    db.add(college)
    db.commit()

    assert college.id is not None
    assert college.name == "Example University"
    assert college.short_name == "EU"
    assert college.email_domain == "example.edu"
    assert college.status == CollegeStatus.ACTIVE
    assert college.created_at is not None


def test_college_email_domain_unique(db):
    """Test that email_domain must be unique."""
    college1 = College(
        name="College 1",
        email_domain="same.edu",
    )
    db.add(college1)
    db.commit()

    college2 = College(
        name="College 2",
        email_domain="same.edu",
    )
    db.add(college2)

    with pytest.raises(IntegrityError):
        db.commit()


def test_college_status(db):
    """Test college status options."""
    statuses = [CollegeStatus.ACTIVE, CollegeStatus.INACTIVE, CollegeStatus.PENDING]

    for status in statuses:
        college = College(
            name=f"College {status.value}",
            email_domain=f"{status.value.lower()}.edu",
            status=status,
        )
        db.add(college)

    db.commit()

    assert db.query(College).count() == len(statuses)


def test_college_repr(db):
    """Test college string representation."""
    college = College(
        name="Test College",
        email_domain="test.edu",
    )
    db.add(college)
    db.commit()

    repr_str = repr(college)
    assert "College" in repr_str
    assert "Test College" in repr_str
