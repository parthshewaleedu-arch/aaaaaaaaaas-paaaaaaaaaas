"""Tests for Campus model"""

import pytest
from decimal import Decimal

from app.models.college import College
from app.models.campus import Campus


def test_create_campus(db):
    """Test creating a campus."""
    college = College(
        name="Test University",
        email_domain="test.edu",
    )
    db.add(college)
    db.commit()

    campus = Campus(
        college_id=college.id,
        name="Main Campus",
        address="123 University Ave, City, State",
        latitude=Decimal("40.7128"),
        longitude=Decimal("-74.0060"),
    )
    db.add(campus)
    db.commit()

    assert campus.id is not None
    assert campus.college_id == college.id
    assert campus.name == "Main Campus"
    assert campus.latitude == Decimal("40.7128")
    assert campus.longitude == Decimal("-74.0060")
    assert campus.radius_meters == 3000  # default


def test_campus_custom_radius(db):
    """Test campus with custom radius."""
    college = College(name="College", email_domain="college.edu")
    db.add(college)
    db.commit()

    campus = Campus(
        college_id=college.id,
        name="Campus",
        address="Address",
        latitude=Decimal("40.0"),
        longitude=Decimal("-74.0"),
        radius_meters=5000,
    )
    db.add(campus)
    db.commit()

    assert campus.radius_meters == 5000


def test_campus_college_relationship(db):
    """Test relationship between campus and college."""
    college = College(name="University", email_domain="uni.edu")
    db.add(college)
    db.commit()

    campus1 = Campus(
        college_id=college.id,
        name="North Campus",
        address="North Address",
        latitude=Decimal("40.0"),
        longitude=Decimal("-74.0"),
    )
    campus2 = Campus(
        college_id=college.id,
        name="South Campus",
        address="South Address",
        latitude=Decimal("39.0"),
        longitude=Decimal("-74.0"),
    )
    db.add_all([campus1, campus2])
    db.commit()

    db.refresh(college)
    assert len(college.campuses) == 2
    assert campus1.college == college
    assert campus2.college == college


def test_campus_repr(db):
    """Test campus string representation."""
    college = College(name="College", email_domain="c.edu")
    db.add(college)
    db.commit()

    campus = Campus(
        college_id=college.id,
        name="Test Campus",
        address="Address",
        latitude=Decimal("40.0"),
        longitude=Decimal("-74.0"),
    )
    db.add(campus)
    db.commit()

    repr_str = repr(campus)
    assert "Campus" in repr_str
    assert "Test Campus" in repr_str
