"""Tests for the college verification service."""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.college import College, CollegeStatus
from app.models.student import Student, VerificationStatus
from app.models.user import User, UserRole, UserStatus
from app.services.college_verification_service import CollegeVerificationService


def test_request_verification(db: Session):
    """Test requesting college email verification."""
    # Create a college
    college = College(
        name="Test College",
        email_domain="testcollege.ac.in",
        status=CollegeStatus.ACTIVE,
    )
    db.add(college)
    db.commit()
    db.refresh(college)

    # Create a user
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

    # Create a student
    student = Student(
        user_id=user.id,
        college_id=college.id,
        full_name="Test Student",
        verification_status=VerificationStatus.UNVERIFIED,
    )
    db.add(student)
    db.commit()
    db.refresh(student)

    # Request verification
    success = CollegeVerificationService.request_verification(str(student.id), db)
    assert success is True

    # Check that token and expiration are set
    db.refresh(student)
    assert student.email_verification_token is not None
    assert student.email_verification_expires_at is not None
    # Token should be a string
    assert isinstance(student.email_verification_token, str)
    # Expiration should be in the future (within 24 hours)
    assert student.email_verification_expires_at > datetime.utcnow()
    assert student.email_verification_expires_at < datetime.utcnow() + timedelta(
        hours=25
    )


def test_verify_token_success(db: Session):
    """Test verifying a correct token."""
    # Setup: create college, user, student
    college = College(
        name="Test College",
        email_domain="testcollege.ac.in",
        status=CollegeStatus.ACTIVE,
    )
    db.add(college)
    db.commit()
    db.refresh(college)

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

    student = Student(
        user_id=user.id,
        college_id=college.id,
        full_name="Test Student",
        verification_status=VerificationStatus.UNVERIFIED,
    )
    db.add(student)
    db.commit()
    db.refresh(student)

    # Request verification to generate a token
    CollegeVerificationService.request_verification(str(student.id), db)
    db.refresh(student)
    token = student.email_verification_token
    assert token is not None

    # Verify with the correct token
    success = CollegeVerificationService.verify_token(str(student.id), token, db)
    assert success is True

    # Check that student is now verified and token cleared
    db.refresh(student)
    assert student.verification_status == VerificationStatus.VERIFIED
    assert student.verified_at is not None
    assert student.email_verification_token is None
    assert student.email_verification_expires_at is None


def test_verify_token_invalid(db: Session):
    """Test verifying with an invalid token."""
    # Setup: create college, user, student
    college = College(
        name="Test College",
        email_domain="testcollege.ac.in",
        status=CollegeStatus.ACTIVE,
    )
    db.add(college)
    db.commit()
    db.refresh(college)

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

    student = Student(
        user_id=user.id,
        college_id=college.id,
        full_name="Test Student",
        verification_status=VerificationStatus.UNVERIFIED,
    )
    db.add(student)
    db.commit()
    db.refresh(student)

    # Request verification to generate a token
    CollegeVerificationService.request_verification(str(student.id), db)
    db.refresh(student)
    # Use a wrong token
    wrong_token = "wrong_token"

    # Verify with the wrong token
    success = CollegeVerificationService.verify_token(str(student.id), wrong_token, db)
    assert success is False

    # Token should still be present (not cleared)
    db.refresh(student)
    assert student.email_verification_token is not None
    assert student.verification_status == VerificationStatus.UNVERIFIED


def test_verify_token_expired(db: Session):
    """Test verifying with an expired token."""
    # Setup: create college, user, student
    college = College(
        name="Test College",
        email_domain="testcollege.ac.in",
        status=CollegeStatus.ACTIVE,
    )
    db.add(college)
    db.commit()
    db.refresh(college)

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

    student = Student(
        user_id=user.id,
        college_id=college.id,
        full_name="Test Student",
        verification_status=VerificationStatus.UNVERIFIED,
    )
    db.add(student)
    db.commit()
    db.refresh(student)

    # Manually set an expired token
    expired_time = datetime.utcnow() - timedelta(hours=1)
    student.email_verification_token = "expired_token"
    student.email_verification_expires_at = expired_time
    db.commit()

    # Verify with the expired token
    success = CollegeVerificationService.verify_token(
        str(student.id), "expired_token", db
    )
    assert success is False

    # Token should still be present (not cleared) because it's invalid
    db.refresh(student)
    assert student.email_verification_token == "expired_token"
    assert student.verification_status == VerificationStatus.UNVERIFIED


def test_resend_verification(db: Session):
    """Test resending the verification email."""
    # Setup: create college, user, student
    college = College(
        name="Test College",
        email_domain="testcollege.ac.in",
        status=CollegeStatus.ACTIVE,
    )
    db.add(college)
    db.commit()
    db.refresh(college)

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

    student = Student(
        user_id=user.id,
        college_id=college.id,
        full_name="Test Student",
        verification_status=VerificationStatus.UNVERIFIED,
    )
    db.add(student)
    db.commit()
    db.refresh(student)

    # Request verification to set initial token
    CollegeVerificationService.request_verification(str(student.id), db)
    db.refresh(student)
    old_token = student.email_verification_token
    old_expires = student.email_verification_expires_at

    # Resend verification
    success = CollegeVerificationService.resend_verification(str(student.id), db)
    assert success is True

    # Check that token and expiration have been updated
    db.refresh(student)
    assert student.email_verification_token is not None
    assert student.email_verification_expires_at is not None
    assert student.email_verification_token != old_token
    # Expiration should be updated (later than the old one)
    assert student.email_verification_expires_at > old_expires
