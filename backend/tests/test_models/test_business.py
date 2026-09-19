"""Tests for Business model"""

import pytest
from decimal import Decimal

from app.models.user import User, UserRole
from app.models.college import College
from app.models.campus import Campus
from app.models.business import Business, BusinessStatus, BusinessVerificationStatus, PriceLevel


def test_create_business(db):
    """Test creating a basic business."""
    owner = User(email="owner@example.com", password_hash="hash", role=UserRole.OWNER)
    college = College(name="College", email_domain="college.edu")
    db.add_all([owner, college])
    db.commit()

    campus = Campus(
        college_id=college.id,
        name="Campus",
        address="Campus Address",
        latitude=Decimal("40.0"),
        longitude=Decimal("-74.0"),
    )
    db.add(campus)
    db.commit()

    business = Business(
        owner_id=owner.id,
        campus_id=campus.id,
        name="Test Business",
        phone="+919876543210",
        address="123 Business St",
        latitude=Decimal("40.0001"),
        longitude=Decimal("-74.0001"),
    )
    db.add(business)
    db.commit()

    assert business.id is not None
    assert business.name == "Test Business"
    assert business.owner_id == owner.id
    assert business.campus_id == campus.id
    assert business.status == BusinessStatus.PENDING
    assert business.verification_status == BusinessVerificationStatus.UNVERIFIED
    assert business.review_count == 0


def test_business_with_details(db):
    """Test business with full details."""
    owner = User(email="owner@example.com", password_hash="hash", role=UserRole.OWNER)
    college = College(name="College", email_domain="college.edu")
    db.add_all([owner, college])
    db.commit()

    campus = Campus(
        college_id=college.id,
        name="Campus",
        address="Address",
        latitude=Decimal("40.0"),
        longitude=Decimal("-74.0"),
    )
    db.add(campus)
    db.commit()

    business = Business(
        owner_id=owner.id,
        campus_id=campus.id,
        name="Full Business",
        description="A great business near campus",
        phone="+919876543210",
        whatsapp="+919876543210",
        email="business@example.com",
        website_url="https://business.example.com",
        address="123 Business St",
        latitude=Decimal("40.0001"),
        longitude=Decimal("-74.0001"),
        price_level=PriceLevel.LEVEL_2,
        student_discount=True,
        student_discount_description="10% off with valid student ID",
    )
    db.add(business)
    db.commit()

    assert business.description == "A great business near campus"
    assert business.whatsapp == "+919876543210"
    assert business.price_level == PriceLevel.LEVEL_2
    assert business.student_discount is True


def test_business_owner_relationship(db):
    """Test relationship between business and owner."""
    owner = User(email="owner@example.com", password_hash="hash", role=UserRole.OWNER)
    college = College(name="College", email_domain="college.edu")
    db.add_all([owner, college])
    db.commit()

    campus = Campus(
        college_id=college.id,
        name="Campus",
        address="Address",
        latitude=Decimal("40.0"),
        longitude=Decimal("-74.0"),
    )
    db.add(campus)
    db.commit()

    business1 = Business(
        owner_id=owner.id,
        campus_id=campus.id,
        name="Business 1",
        phone="+911111111111",
        address="Address 1",
        latitude=Decimal("40.0"),
        longitude=Decimal("-74.0"),
    )
    business2 = Business(
        owner_id=owner.id,
        campus_id=campus.id,
        name="Business 2",
        phone="+912222222222",
        address="Address 2",
        latitude=Decimal("40.1"),
        longitude=Decimal("-74.1"),
    )
    db.add_all([business1, business2])
    db.commit()

    db.refresh(owner)
    assert len(owner.businesses) == 2


def test_business_status_transitions(db):
    """Test business status changes."""
    owner = User(email="owner@example.com", password_hash="hash", role=UserRole.OWNER)
    college = College(name="College", email_domain="college.edu")
    db.add_all([owner, college])
    db.commit()

    campus = Campus(
        college_id=college.id,
        name="Campus",
        address="Address",
        latitude=Decimal("40.0"),
        longitude=Decimal("-74.0"),
    )
    db.add(campus)
    db.commit()

    business = Business(
        owner_id=owner.id,
        campus_id=campus.id,
        name="Business",
        phone="+919876543210",
        address="Address",
        latitude=Decimal("40.0"),
        longitude=Decimal("-74.0"),
    )
    db.add(business)
    db.commit()

    assert business.status == BusinessStatus.PENDING

    business.status = BusinessStatus.ACTIVE
    business.verification_status = BusinessVerificationStatus.VERIFIED
    db.commit()

    db.refresh(business)
    assert business.status == BusinessStatus.ACTIVE
    assert business.verification_status == BusinessVerificationStatus.VERIFIED


def test_business_rating_update(db):
    """Test updating business rating and review count."""
    owner = User(email="owner@example.com", password_hash="hash", role=UserRole.OWNER)
    college = College(name="College", email_domain="college.edu")
    db.add_all([owner, college])
    db.commit()

    campus = Campus(
        college_id=college.id,
        name="Campus",
        address="Address",
        latitude=Decimal("40.0"),
        longitude=Decimal("-74.0"),
    )
    db.add(campus)
    db.commit()

    business = Business(
        owner_id=owner.id,
        campus_id=campus.id,
        name="Business",
        phone="+919876543210",
        address="Address",
        latitude=Decimal("40.0"),
        longitude=Decimal("-74.0"),
    )
    db.add(business)
    db.commit()

    assert business.average_rating is None
    assert business.review_count == 0

    business.average_rating = Decimal("4.5")
    business.review_count = 10
    db.commit()

    db.refresh(business)
    assert business.average_rating == Decimal("4.50")
    assert business.review_count == 10


def test_business_repr(db):
    """Test business string representation."""
    owner = User(email="owner@example.com", password_hash="hash", role=UserRole.OWNER)
    college = College(name="College", email_domain="college.edu")
    db.add_all([owner, college])
    db.commit()

    campus = Campus(
        college_id=college.id,
        name="Campus",
        address="Address",
        latitude=Decimal("40.0"),
        longitude=Decimal("-74.0"),
    )
    db.add(campus)
    db.commit()

    business = Business(
        owner_id=owner.id,
        campus_id=campus.id,
        name="Test Business",
        phone="+919876543210",
        address="Address",
        latitude=Decimal("40.0"),
        longitude=Decimal("-74.0"),
    )
    db.add(business)
    db.commit()

    repr_str = repr(business)
    assert "Business" in repr_str
    assert "Test Business" in repr_str
