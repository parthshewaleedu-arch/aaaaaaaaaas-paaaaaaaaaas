"""Tests for the student service."""

import pytest
from sqlalchemy.orm import Session
from uuid import uuid4

from app.models.college import College, CollegeStatus
from app.models.campus import Campus
from app.models.student import VerificationStatus
from app.models.user import User, UserRole, UserStatus
from app.schemas.student import StudentCreate, StudentUpdate
from app.services.student_service import StudentService


def create_test_data(db: Session):
    """Create test college, campus, user, and student."""
    college = College(
        name="Test College",
        short_name="TC",
        email_domain="testcollege.ac.in",
        status=CollegeStatus.ACTIVE,
    )
    db.add(college)
    db.commit()
    db.refresh(college)

    campus = Campus(
        college_id=college.id,
        name="Test Campus",
        address="Test Address",
        latitude=18.7830,
        longitude=73.9375,
        radius_meters=3000,
    )
    db.add(campus)
    db.commit()
    db.refresh(campus)

    user = User(
        email="student@testcollege.ac.in",
        password_hash="hashed_password",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
        is_email_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return college, campus, user


def test_create_student(db: Session):
    """Test creating a student profile."""
    college, campus, user = create_test_data(db)

    student_data = StudentCreate(
        user_id=user.id,
        college_id=college.id,
        campus_id=campus.id,
        full_name="Test Student",
        student_id="STU001",
        department="Computer Science",
        year=3,
    )

    student = StudentService.create_student(student_data, db)

    assert student is not None
    assert student.user_id == user.id
    assert student.college_id == college.id
    assert student.campus_id == campus.id
    assert student.full_name == "Test Student"
    assert student.student_id == "STU001"
    assert student.department == "Computer Science"
    assert student.year == 3
    assert student.verification_status == VerificationStatus.UNVERIFIED


def test_create_student_without_campus(db: Session):
    """Test creating a student profile without campus."""
    college, _, user = create_test_data(db)

    student_data = StudentCreate(
        user_id=user.id,
        college_id=college.id,
        full_name="Test Student",
    )

    student = StudentService.create_student(student_data, db)

    assert student is not None
    assert student.campus_id is None


def test_create_student_duplicate_user(db: Session):
    """Test creating a student profile for a user that already has one."""
    college, campus, user = create_test_data(db)

    student_data = StudentCreate(
        user_id=user.id,
        college_id=college.id,
        campus_id=campus.id,
        full_name="Test Student",
    )

    StudentService.create_student(student_data, db)

    # Try to create another profile for the same user
    student_data2 = StudentCreate(
        user_id=user.id,
        college_id=college.id,
        full_name="Test Student 2",
    )

    with pytest.raises(ValueError, match="Student profile already exists"):
        StudentService.create_student(student_data2, db)


def test_create_student_invalid_user(db: Session):
    """Test creating a student profile with invalid user."""
    college, _, _ = create_test_data(db)

    student_data = StudentCreate(
        user_id=uuid4(),  # Non-existent user
        college_id=college.id,
        full_name="Test Student",
    )

    with pytest.raises(ValueError, match="User not found"):
        StudentService.create_student(student_data, db)


def test_create_student_wrong_role(db: Session):
    """Test creating a student profile for a non-student user."""
    college, _, _ = create_test_data(db)

    # Create an owner user
    owner = User(
        email="owner@testcollege.ac.in",
        password_hash="hashed_password",
        role=UserRole.OWNER,
        status=UserStatus.ACTIVE,
    )
    db.add(owner)
    db.commit()
    db.refresh(owner)

    student_data = StudentCreate(
        user_id=owner.id,
        college_id=college.id,
        full_name="Test Student",
    )

    with pytest.raises(ValueError, match="User must have STUDENT role"):
        StudentService.create_student(student_data, db)


def test_get_student_by_id(db: Session):
    """Test getting student by ID."""
    college, campus, user = create_test_data(db)

    student_data = StudentCreate(
        user_id=user.id,
        college_id=college.id,
        campus_id=campus.id,
        full_name="Test Student",
    )

    created_student = StudentService.create_student(student_data, db)
    retrieved_student = StudentService.get_student_by_id(created_student.id, db)

    assert retrieved_student is not None
    assert retrieved_student.id == created_student.id
    assert retrieved_student.full_name == "Test Student"


def test_get_student_by_user_id(db: Session):
    """Test getting student by user ID."""
    college, campus, user = create_test_data(db)

    student_data = StudentCreate(
        user_id=user.id,
        college_id=college.id,
        campus_id=campus.id,
        full_name="Test Student",
    )

    StudentService.create_student(student_data, db)
    retrieved_student = StudentService.get_student_by_user_id(user.id, db)

    assert retrieved_student is not None
    assert retrieved_student.user_id == user.id


def test_get_student_profile(db: Session):
    """Test getting student profile with related data."""
    college, campus, user = create_test_data(db)

    student_data = StudentCreate(
        user_id=user.id,
        college_id=college.id,
        campus_id=campus.id,
        full_name="Test Student",
        student_id="STU001",
        department="Computer Science",
        year=3,
    )

    created_student = StudentService.create_student(student_data, db)
    profile = StudentService.get_student_profile(created_student.id, db)

    assert profile is not None
    assert profile.id == created_student.id
    assert profile.email == user.email
    assert profile.full_name == "Test Student"
    assert profile.student_id == "STU001"
    assert profile.department == "Computer Science"
    assert profile.year == 3
    assert profile.college_name == college.name
    assert profile.campus_name == campus.name
    assert profile.verification_status == "UNVERIFIED"
    assert profile.is_email_verified is True


def test_update_student(db: Session):
    """Test updating student profile."""
    college, campus, user = create_test_data(db)

    student_data = StudentCreate(
        user_id=user.id,
        college_id=college.id,
        campus_id=campus.id,
        full_name="Test Student",
    )

    created_student = StudentService.create_student(student_data, db)

    update_data = StudentUpdate(
        full_name="Updated Name",
        student_id="STU002",
        department="Electronics",
        year=4,
    )

    updated_student = StudentService.update_student(created_student.id, update_data, db)

    assert updated_student is not None
    assert updated_student.full_name == "Updated Name"
    assert updated_student.student_id == "STU002"
    assert updated_student.department == "Electronics"
    assert updated_student.year == 4


def test_update_student_campus(db: Session):
    """Test updating student campus."""
    college, campus, user = create_test_data(db)

    # Create second campus
    campus2 = Campus(
        college_id=college.id,
        name="Second Campus",
        address="Second Address",
        latitude=18.7900,
        longitude=73.9400,
        radius_meters=3000,
    )
    db.add(campus2)
    db.commit()
    db.refresh(campus2)

    student_data = StudentCreate(
        user_id=user.id,
        college_id=college.id,
        campus_id=campus.id,
        full_name="Test Student",
    )

    created_student = StudentService.create_student(student_data, db)

    update_data = StudentUpdate(campus_id=campus2.id)
    updated_student = StudentService.update_student(created_student.id, update_data, db)

    assert updated_student is not None
    assert updated_student.campus_id == campus2.id


def test_update_student_invalid_campus(db: Session):
    """Test updating student with invalid campus (different college)."""
    college, campus, user = create_test_data(db)

    # Create another college and campus
    college2 = College(
        name="Another College",
        email_domain="another.ac.in",
        status=CollegeStatus.ACTIVE,
    )
    db.add(college2)
    db.commit()
    db.refresh(college2)

    campus2 = Campus(
        college_id=college2.id,
        name="Another Campus",
        address="Another Address",
        latitude=18.7900,
        longitude=73.9400,
        radius_meters=3000,
    )
    db.add(campus2)
    db.commit()
    db.refresh(campus2)

    student_data = StudentCreate(
        user_id=user.id,
        college_id=college.id,
        campus_id=campus.id,
        full_name="Test Student",
    )

    created_student = StudentService.create_student(student_data, db)

    update_data = StudentUpdate(campus_id=campus2.id)

    with pytest.raises(
        ValueError, match="Campus does not belong to the student's college"
    ):
        StudentService.update_student(created_student.id, update_data, db)


def test_list_students(db: Session):
    """Test listing students with filters."""
    college, campus, user = create_test_data(db)

    # Create multiple students
    for i in range(3):
        student_user = User(
            email=f"student{i}@testcollege.ac.in",
            password_hash="hashed_password",
            role=UserRole.STUDENT,
            status=UserStatus.ACTIVE,
            is_email_verified=True,
        )
        db.add(student_user)
        db.commit()
        db.refresh(student_user)

        student_data = StudentCreate(
            user_id=student_user.id,
            college_id=college.id,
            campus_id=campus.id,
            full_name=f"Student {i}",
        )
        StudentService.create_student(student_data, db)

    # List all students
    students = StudentService.list_students(db, college_id=college.id)
    assert len(students) == 3

    # List with pagination
    students = StudentService.list_students(db, college_id=college.id, skip=1, limit=1)
    assert len(students) == 1


def test_count_students(db: Session):
    """Test counting students."""
    college, campus, user = create_test_data(db)

    # Create multiple students
    for i in range(3):
        student_user = User(
            email=f"student{i}@testcollege.ac.in",
            password_hash="hashed_password",
            role=UserRole.STUDENT,
            status=UserStatus.ACTIVE,
            is_email_verified=True,
        )
        db.add(student_user)
        db.commit()
        db.refresh(student_user)

        student_data = StudentCreate(
            user_id=student_user.id,
            college_id=college.id,
            campus_id=campus.id,
            full_name=f"Student {i}",
        )
        StudentService.create_student(student_data, db)

    count = StudentService.count_students(db, college_id=college.id)
    assert count == 3
