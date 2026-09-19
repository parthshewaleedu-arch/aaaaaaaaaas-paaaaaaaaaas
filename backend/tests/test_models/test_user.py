"""Tests for User model"""

import pytest
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from app.models.user import User, UserRole, UserStatus


def test_create_user(db):
    """Test creating a basic user."""
    user = User(
        email="test@example.com",
        password_hash="hashed_password_here",
        role=UserRole.STUDENT,
    )
    db.add(user)
    db.commit()

    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.role == UserRole.STUDENT
    assert user.status == UserStatus.ACTIVE
    assert user.is_email_verified is False
    assert user.is_phone_verified is False
    assert user.created_at is not None
    assert user.updated_at is not None


def test_user_email_unique(db):
    """Test that email must be unique."""
    user1 = User(
        email="duplicate@example.com",
        password_hash="hash1",
        role=UserRole.STUDENT,
    )
    db.add(user1)
    db.commit()

    user2 = User(
        email="duplicate@example.com",
        password_hash="hash2",
        role=UserRole.OWNER,
    )
    db.add(user2)

    with pytest.raises(IntegrityError):
        db.commit()


def test_user_phone_unique(db):
    """Test that phone must be unique when set."""
    user1 = User(
        email="user1@example.com",
        phone="+919876543210",
        password_hash="hash1",
        role=UserRole.STUDENT,
    )
    db.add(user1)
    db.commit()

    user2 = User(
        email="user2@example.com",
        phone="+919876543210",
        password_hash="hash2",
        role=UserRole.OWNER,
    )
    db.add(user2)

    with pytest.raises(IntegrityError):
        db.commit()


def test_user_roles(db):
    """Test different user roles."""
    roles = [UserRole.STUDENT, UserRole.OWNER, UserRole.ADMIN, UserRole.COLLEGE_ADMIN]

    for role in roles:
        user = User(
            email=f"{role.value.lower()}@example.com",
            password_hash="hash",
            role=role,
        )
        db.add(user)

    db.commit()

    assert db.query(User).count() == len(roles)


def test_user_status_changes(db):
    """Test user status transitions."""
    user = User(
        email="status@example.com",
        password_hash="hash",
        role=UserRole.STUDENT,
    )
    db.add(user)
    db.commit()

    assert user.status == UserStatus.ACTIVE

    user.status = UserStatus.SUSPENDED
    db.commit()

    db.refresh(user)
    assert user.status == UserStatus.SUSPENDED


def test_user_soft_delete(db):
    """Test soft deletion with deleted_at timestamp."""
    user = User(
        email="delete@example.com",
        password_hash="hash",
        role=UserRole.STUDENT,
    )
    db.add(user)
    db.commit()

    assert user.deleted_at is None

    user.deleted_at = datetime.utcnow()
    user.status = UserStatus.DELETED
    db.commit()

    db.refresh(user)
    assert user.deleted_at is not None
    assert user.status == UserStatus.DELETED


def test_user_repr(db):
    """Test user string representation."""
    user = User(
        email="repr@example.com",
        password_hash="hash",
        role=UserRole.STUDENT,
    )
    db.add(user)
    db.commit()

    repr_str = repr(user)
    assert "User" in repr_str
    assert "repr@example.com" in repr_str
    assert "STUDENT" in repr_str
