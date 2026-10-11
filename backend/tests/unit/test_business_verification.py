"""Unit tests for business verification workflow."""

import json
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.models.business import Business, BusinessStatus, BusinessVerificationStatus
from app.services.business_service import BusinessService


def test_submit_for_verification_with_notes_and_docs():
    """Test owner submitting business for verification with notes and documents."""
    mock_db = MagicMock()
    owner_id = uuid4()
    business_id = uuid4()

    business = Business(
        id=business_id,
        owner_id=owner_id,
        name="Campus Xerox",
        status=BusinessStatus.PENDING,
        verification_status=BusinessVerificationStatus.UNVERIFIED,
    )
    mock_db.query.return_value.filter.return_value.first.return_value = business

    notes = "Shop license attached"
    documents = ["https://storage.aaspaas.com/docs/license1.pdf"]

    result = BusinessService.submit_for_verification(
        business_id=business_id,
        owner_id=owner_id,
        db=mock_db,
        notes=notes,
        documents=documents,
    )

    assert result is not None
    assert result.verification_status == BusinessVerificationStatus.PENDING
    assert result.status == BusinessStatus.PENDING
    assert result.verification_notes is not None

    parsed = json.loads(result.verification_notes)
    assert parsed["notes"] == notes
    assert parsed["documents"] == documents
    mock_db.commit.assert_called_once()


def test_submit_for_verification_already_verified_raises():
    """Test cannot submit a business that is already verified."""
    mock_db = MagicMock()
    owner_id = uuid4()
    business_id = uuid4()

    business = Business(
        id=business_id,
        owner_id=owner_id,
        name="Verified Shop",
        verification_status=BusinessVerificationStatus.VERIFIED,
    )
    mock_db.query.return_value.filter.return_value.first.return_value = business

    with pytest.raises(ValueError, match="already verified"):
        BusinessService.submit_for_verification(business_id, owner_id, mock_db)


def test_approve_business_admin():
    """Test admin approving a pending business."""
    mock_db = MagicMock()
    business_id = uuid4()
    admin_id = uuid4()

    business = Business(
        id=business_id,
        name="Sharma Mess",
        status=BusinessStatus.PENDING,
        verification_status=BusinessVerificationStatus.PENDING,
        rejection_reason="Previous missing document",
    )
    mock_db.query.return_value.filter.return_value.first.return_value = business

    result = BusinessService.approve_business(
        business_id=business_id,
        db=mock_db,
        reviewer_id=admin_id,
        reason="Physical verification complete",
    )

    assert result is not None
    assert result.verification_status == BusinessVerificationStatus.VERIFIED
    assert result.status == BusinessStatus.ACTIVE
    assert result.verified_at is not None
    assert result.rejection_reason is None
    mock_db.commit.assert_called_once()


def test_reject_business_admin():
    """Test admin rejecting a business with explanation reason."""
    mock_db = MagicMock()
    business_id = uuid4()
    admin_id = uuid4()

    business = Business(
        id=business_id,
        name="Suspicious Shop",
        status=BusinessStatus.PENDING,
        verification_status=BusinessVerificationStatus.PENDING,
    )
    mock_db.query.return_value.filter.return_value.first.return_value = business

    reason = "Address proof is invalid"
    result = BusinessService.reject_business(
        business_id=business_id,
        db=mock_db,
        reviewer_id=admin_id,
        reason=reason,
    )

    assert result is not None
    assert result.verification_status == BusinessVerificationStatus.UNVERIFIED
    assert result.status == BusinessStatus.REJECTED
    assert result.rejection_reason == reason
    mock_db.commit.assert_called_once()
