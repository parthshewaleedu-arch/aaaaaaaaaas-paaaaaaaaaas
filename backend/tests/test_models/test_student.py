"""Tests for Student model"""

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.user import User, UserRole
from app.models.college import College
from app.models.campus import Campus
from app.models.student import Student, VerificationStatus
from decimal import Decimal


def test_create_student(db):
    """Test creating a student profile."""
    user = User(
        email="student@test.edu",
        password_hash="hash",
        role=UserRole.STUDENT,
    )
    college = College(name="Test College", email_domain="test.edu")
    db.add_all([user, college])
    db.commit()

    student = Student(
        user_id=user.id,
        college_id=college.id,
        full_name="John Doe",
    )
    db.add(student)
    db.commit()

    assert student.id is not None
    assert student.user_id == user.id
    assert student.college_id == college.id
    assert student.full_name == "John Doe"
    assert student.verification_status == VerificationStatus.UNVERIFIED


def test_student_with_academic_info(db):
    """Test student with optional academic information."""
    user = User(email="student@test.edu", password_hash="hash", role=UserRole.STUDENT)
    college = College(name="College", email_domain="test.edu")
    db.add_all([user, college])
    db.commit()

    student = Student(
        user_id=user.id,
        college_id=college.id,
        full_name="Jane Smith",
        student_id="CS2023001",
        department="Computer Science",
        year=3,
    )
    db.add(student)
    db.commit()

    assert student.student_id == "CS2023001"
    assert student.department == "Computer Science"
    assert student.year == 3


def test_student_campus_relationship(db):
    """Test student with campus assignment."""
    user = User(email="student@test.edu", password_hash="hash", role=UserRole.STUDENT)
    college = College(name="College", email_domain="test.edu")
    db.add_all([user, college])
    db.commit()

    campus = Campus(
        college_id=college.id,
        name="Main Campus",
        address="Address",
        latitude=Decimal("40.0"),
        longitude=Decimal("-74.0"),
    )
    db.add(campus)
    db.commit()

    student = Student(
        user_id=user.id,
        college_id=college.id,
        campus_id=campus.id,
        full_name="Student Name",
    )
    db.add(student)
    db.commit()

    assert student.campus_id == campus.id
    assert student.campus == campus


def test_student_user_one_to_one(db):
    """Test one-to-one relationship between user and student."""
    user = User(email="student@test.edu", password_hash="hash", role=UserRole.STUDENT)
    college = College(name="College", email_domain="test.edu")
    db.add_all([user, college])
    db.commit()

    student = Student(
        user_id=user.id,
        college_id=college.id,
        full_name="Student",
    )
    db.add(student)
    db.commit()

    db.refresh(user)
    assert user.student == student
    assert student.user == user


def test_student_user_unique(db):
    """Test that user_id must be unique (one student per user)."""
    user = User(email="student@test.edu", password_hash="hash", role=UserRole.STUDENT)
    college = College(name="College", email_domain="test.edu")
    db.add_all([user, college])
    db.commit()

    student1 = Student(
        user_id=user.id,
        college_id=college.id,
        full_name="Student 1",
    )
    db.add(student1)
    db.commit()

    student2 = Student(
        user_id=user.id,
        college_id=college.id,
        full_name="Student 2",
    )
    db.add(student2)

    with pytest.raises(IntegrityError):
        db.commit()


def test_student_verification_status(db):
    """Test student verification status transitions."""
    user = User(email="student@test.edu", password_hash="hash", role=UserRole.STUDENT)
    college = College(name="College", email_domain="test.edu")
    db.add_all([user, college])
    db.commit()

    student = Student(
        user_id=user.id,
        college_id=college.id,
        full_name="Student",
    )
    db.add(student)
    db.commit()

    assert student.verification_status == VerificationStatus.UNVERIFIED

    student.verification_status = VerificationStatus.VERIFIED
    db.commit()

    db.refresh(student)
    assert student.verification_status == VerificationStatus.VERIFIED


def test_student_repr(db):
    """Test student string representation."""
    user = User(email="student@test.edu", password_hash="hash", role=UserRole.STUDENT)
    college = College(name="College", email_domain="test.edu")
    db.add_all([user, college])
    db.commit()

    student = Student(
        user_id=user.id,
        college_id=college.id,
        full_name="Test Student",
    )
    db.add(student)
    db.commit()

    repr_str = repr(student)
    assert "Student" in repr_str
    assert "Test Student" in repr_str
