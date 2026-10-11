"""Unit tests for AdminService."""

from datetime import datetime, timezone
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.models.business import (
    Business,
    BusinessStatus,
    BusinessVerificationStatus,
)
from app.models.review import Review, ReviewStatus, VerificationLevel
from app.models.review_report import ReviewReport, ReviewReportStatus
from app.models.user import User, UserRole, UserStatus
from app.services.admin_service import AdminService
from app.services.review_service import ReviewService


def test_record_audit_log_success():
    """Test creating and persisting an audit log."""
    mock_db = MagicMock()
    admin_id = uuid4()
    entity_id = uuid4()

    log = AdminService.record_audit_log(
        db=mock_db,
        admin_id=admin_id,
        action="TEST_ACTION",
        entity_type="business",
        entity_id=entity_id,
        old_data={"status": "PENDING"},
        new_data={"status": "ACTIVE"},
        reason="Manual approval",
        ip_address="127.0.0.1",
        user_agent="Pytest Agent",
    )

    assert log.admin_id == admin_id
    assert log.action == "TEST_ACTION"
    assert log.entity_type == "business"
    assert log.entity_id == entity_id
    assert mock_db.add.called
    assert mock_db.commit.called


def test_get_dashboard_metrics():
    """Test aggregating platform dashboard KPIs."""
    mock_db = MagicMock()
    # Mock query.count() returns
    mock_db.query.return_value.count.return_value = 50
    mock_db.query.return_value.filter.return_value.count.return_value = 10

    metrics = AdminService.get_dashboard_metrics(db=mock_db)

    assert metrics.students is not None
    assert metrics.businesses is not None
    assert metrics.reviews is not None
    assert metrics.reports is not None


def test_list_users():
    """Test listing and filtering users."""
    mock_db = MagicMock()
    u1 = User(
        id=uuid4(),
        email="student@univ.edu",
        phone="9876543210",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
        created_at=datetime.now(timezone.utc),
    )

    query_mock = MagicMock()
    mock_db.query.return_value = query_mock
    query_mock.filter.return_value = query_mock
    query_mock.count.return_value = 1
    query_mock.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [
        u1
    ]

    users, total = AdminService.list_users(
        db=mock_db,
        role=UserRole.STUDENT,
        status_filter=UserStatus.ACTIVE,
    )

    assert total == 1
    assert len(users) == 1
    assert users[0].email == "student@univ.edu"
    assert users[0].role == UserRole.STUDENT


def test_update_user_status_success():
    """Test updating user status and recording audit log."""
    mock_db = MagicMock()
    user_id = uuid4()
    admin_id = uuid4()

    user = User(
        id=user_id,
        email="test@univ.edu",
        phone="9876543210",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
        created_at=datetime.now(timezone.utc),
    )
    mock_db.query.return_value.filter.return_value.first.return_value = user

    res = AdminService.update_user_status(
        db=mock_db,
        user_id=user_id,
        admin_id=admin_id,
        new_status=UserStatus.SUSPENDED,
        reason="Breach of community guidelines",
    )

    assert res.status == UserStatus.SUSPENDED
    assert user.status == UserStatus.SUSPENDED
    assert mock_db.commit.called


def test_update_user_status_not_found():
    """Test updating non-existent user raises 404."""
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc:
        AdminService.update_user_status(
            db=mock_db,
            user_id=uuid4(),
            admin_id=uuid4(),
            new_status=UserStatus.SUSPENDED,
        )
    assert exc.value.status_code == 404


def test_verify_business_approve_success():
    """Test approving business verification sets status to ACTIVE and VERIFIED."""
    mock_db = MagicMock()
    biz_id = uuid4()
    admin_id = uuid4()

    biz = Business(
        id=biz_id,
        name="Campus Bakery",
        owner_id=uuid4(),
        status=BusinessStatus.PENDING,
        verification_status=BusinessVerificationStatus.PENDING,
        created_at=datetime.now(timezone.utc),
    )
    biz.owner = User(id=biz.owner_id, email="owner@bakery.com")
    biz.campus = None

    mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = (
        biz
    )

    res = AdminService.verify_business(
        db=mock_db,
        business_id=biz_id,
        admin_id=admin_id,
        action="APPROVE",
        reason="GST and FSSAI verified",
    )

    assert res.status == BusinessStatus.ACTIVE
    assert res.verification_status == BusinessVerificationStatus.VERIFIED
    assert biz.verified_at is not None
    assert mock_db.commit.called


def test_verify_business_reject_success():
    """Test rejecting business verification sets rejection reason."""
    mock_db = MagicMock()
    biz_id = uuid4()
    admin_id = uuid4()

    biz = Business(
        id=biz_id,
        name="Dubious Merchant",
        owner_id=uuid4(),
        status=BusinessStatus.PENDING,
        verification_status=BusinessVerificationStatus.PENDING,
        created_at=datetime.now(timezone.utc),
    )
    biz.owner = User(id=biz.owner_id, email="owner@dubious.com")
    biz.campus = None

    mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = (
        biz
    )

    res = AdminService.verify_business(
        db=mock_db,
        business_id=biz_id,
        admin_id=admin_id,
        action="REJECT",
        reason="Documents blurry and unverifiable",
    )

    assert res.verification_status == BusinessVerificationStatus.UNVERIFIED
    assert res.rejection_reason == "Documents blurry and unverifiable"
    assert mock_db.commit.called


def test_update_business_status():
    """Test changing business status (e.g. suspend)."""
    mock_db = MagicMock()
    biz_id = uuid4()
    admin_id = uuid4()

    biz = Business(
        id=biz_id,
        name="Active Store",
        owner_id=uuid4(),
        status=BusinessStatus.ACTIVE,
        verification_status=BusinessVerificationStatus.VERIFIED,
        created_at=datetime.now(timezone.utc),
    )
    biz.owner = None
    biz.campus = None

    mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = (
        biz
    )

    res = AdminService.update_business_status(
        db=mock_db,
        business_id=biz_id,
        admin_id=admin_id,
        new_status=BusinessStatus.SUSPENDED,
        reason="Pending fraud investigation",
    )

    assert res.status == BusinessStatus.SUSPENDED
    assert biz.status == BusinessStatus.SUSPENDED
    assert mock_db.commit.called


def test_moderate_review_remove(monkeypatch):
    """Test removing a review soft-deletes it, resolves reports, and recalculates business rating."""
    mock_db = MagicMock()
    rev_id = uuid4()
    biz_id = uuid4()
    admin_id = uuid4()

    rev = Review(
        id=rev_id,
        business_id=biz_id,
        user_id=uuid4(),
        overall_rating=1.0,
        review_text="Offensive review",
        status=ReviewStatus.ACTIVE,
        verification_level=VerificationLevel.VERIFIED_STUDENT,
        created_at=datetime.now(timezone.utc),
    )
    rev.business = Business(id=biz_id, name="Campus Gym")
    rev.user = User(id=rev.user_id, email="troll@univ.edu")

    report = ReviewReport(
        id=uuid4(),
        review_id=rev_id,
        reported_by=uuid4(),
        status=ReviewReportStatus.PENDING,
    )

    mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = (
        rev
    )
    mock_db.query.return_value.filter.return_value.all.return_value = [report]
    mock_db.query.return_value.filter.return_value.count.return_value = 1

    monkeypatch.setattr(
        ReviewService, "recalculate_business_ratings", lambda b_id, db: None
    )

    mod_res = AdminService.moderate_review(
        db=mock_db,
        review_id=rev_id,
        admin_id=admin_id,
        action="REMOVE",
        reason="Abusive content violates community standard",
    )

    assert mod_res.status == "REMOVED"
    assert mod_res.user_email == "troll@univ.edu"
    assert rev.status == ReviewStatus.REMOVED
    assert rev.deleted_at is not None
    assert report.status == ReviewReportStatus.RESOLVED
    assert mock_db.commit.called


def test_moderate_review_keep(monkeypatch):
    """Test keeping a review marks pending reports as dismissed."""
    mock_db = MagicMock()
    rev_id = uuid4()
    biz_id = uuid4()
    admin_id = uuid4()

    rev = Review(
        id=rev_id,
        business_id=biz_id,
        user_id=uuid4(),
        overall_rating=4.0,
        review_text="Legitimate critique of service",
        status=ReviewStatus.PENDING_MODERATION,
        verification_level=VerificationLevel.VERIFIED_STUDENT,
        created_at=datetime.now(timezone.utc),
    )
    rev.business = Business(id=biz_id, name="Campus Diner")
    rev.user = User(id=rev.user_id, email="reviewer@univ.edu")

    report = ReviewReport(
        id=uuid4(),
        review_id=rev_id,
        reported_by=uuid4(),
        status=ReviewReportStatus.PENDING,
    )

    mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = (
        rev
    )
    mock_db.query.return_value.filter.return_value.all.return_value = [report]
    mock_db.query.return_value.filter.return_value.count.return_value = 1

    monkeypatch.setattr(
        ReviewService, "recalculate_business_ratings", lambda b_id, db: None
    )

    mod_res = AdminService.moderate_review(
        db=mock_db,
        review_id=rev_id,
        admin_id=admin_id,
        action="KEEP",
        reason="Critique is valid and fair",
    )

    assert mod_res.status == "ACTIVE"
    assert mod_res.user_email == "reviewer@univ.edu"
    assert rev.status == ReviewStatus.ACTIVE
    assert report.status == ReviewReportStatus.DISMISSED
    assert mock_db.commit.called
