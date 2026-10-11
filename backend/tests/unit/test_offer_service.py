"""Unit tests for OfferService."""

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.models.business import Business
from app.models.offer import Offer, OfferDiscountType, OfferStatus
from app.models.offer_redemption import OfferRedemption, OfferRedemptionStatus
from app.models.student import Student, VerificationStatus
from app.models.user import User, UserRole
from app.schemas.offer import OfferCreate, OfferUpdate
from app.services.offer_service import OfferService


def test_create_offer_owner_success():
    """Test business owner successfully creates an offer."""
    mock_db = MagicMock()
    owner_id = uuid4()
    business_id = uuid4()

    owner = User(id=owner_id, role=UserRole.OWNER)
    business = Business(id=business_id, owner_id=owner_id, name="Campus Cafe")

    mock_db.query.return_value.filter.return_value.first.return_value = business

    now = datetime.now(timezone.utc)
    offer_in = OfferCreate(
        title="20% Student Discount",
        description="Get 20% off on all burgers",
        discount_type=OfferDiscountType.PERCENTAGE,
        discount_value=20.0,
        valid_from=now,
        valid_until=now + timedelta(days=30),
        max_redemptions=50,
    )

    offer = OfferService.create_offer(business_id, offer_in, owner, mock_db)
    assert offer.title == "20% Student Discount"
    assert offer.discount_value == 20.0
    assert offer.max_redemptions == 50
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


def test_create_offer_non_owner_forbidden():
    """Test non-owner user cannot create offer for business."""
    mock_db = MagicMock()
    owner_id = uuid4()
    other_user_id = uuid4()
    business_id = uuid4()

    other_user = User(id=other_user_id, role=UserRole.OWNER)
    business = Business(id=business_id, owner_id=owner_id, name="Campus Cafe")

    mock_db.query.return_value.filter.return_value.first.return_value = business

    now = datetime.now(timezone.utc)
    offer_in = OfferCreate(
        title="Hacked Discount",
        description="Fake discount",
        discount_type=OfferDiscountType.PERCENTAGE,
        discount_value=50.0,
        valid_from=now,
        valid_until=now + timedelta(days=10),
    )

    with pytest.raises(HTTPException) as exc:
        OfferService.create_offer(business_id, offer_in, other_user, mock_db)
    assert exc.value.status_code == 403


def test_create_offer_invalid_dates_rejected():
    """Test offer creation with valid_until <= valid_from raises 400."""
    now = datetime.now(timezone.utc)
    with pytest.raises(ValueError):
        OfferCreate(
            title="Invalid Dates",
            description="Testing dates",
            discount_type=OfferDiscountType.PERCENTAGE,
            discount_value=10.0,
            valid_from=now + timedelta(days=5),
            valid_until=now,  # Invalid: until before from
        )


def test_get_offer_active_public():
    """Test public access to active offer."""
    mock_db = MagicMock()
    offer_id = uuid4()
    business_id = uuid4()

    offer = Offer(
        id=offer_id,
        business_id=business_id,
        title="15% Off",
        status=OfferStatus.ACTIVE,
    )
    mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = (
        offer
    )

    retrieved = OfferService.get_offer(offer_id, mock_db)
    assert retrieved.id == offer_id
    assert retrieved.title == "15% Off"


def test_get_offer_draft_forbidden_for_public():
    """Test public student cannot view draft offer."""
    mock_db = MagicMock()
    offer_id = uuid4()
    business_id = uuid4()
    owner_id = uuid4()

    business = Business(id=business_id, owner_id=owner_id)
    offer = Offer(
        id=offer_id,
        business_id=business_id,
        business=business,
        title="Draft Offer",
        status=OfferStatus.DRAFT,
    )
    mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = (
        offer
    )

    student = User(id=uuid4(), role=UserRole.STUDENT)
    with pytest.raises(HTTPException) as exc:
        OfferService.get_offer(offer_id, mock_db, current_user=student)
    assert exc.value.status_code == 404


def test_update_offer_owner_success():
    """Test business owner successfully updates offer details."""
    mock_db = MagicMock()
    owner_id = uuid4()
    business_id = uuid4()
    offer_id = uuid4()

    business = Business(id=business_id, owner_id=owner_id)
    offer = Offer(
        id=offer_id,
        business_id=business_id,
        business=business,
        title="Old Title",
        discount_value=10.0,
        valid_from=datetime.now(timezone.utc),
        valid_until=datetime.now(timezone.utc) + timedelta(days=10),
    )
    mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = (
        offer
    )

    owner = User(id=owner_id, role=UserRole.OWNER)
    update_in = OfferUpdate(title="New Title", discount_value=25.0)

    updated = OfferService.update_offer(offer_id, update_in, owner, mock_db)
    assert updated.title == "New Title"
    assert updated.discount_value == 25.0
    mock_db.commit.assert_called_once()


def test_cancel_offer_owner_success():
    """Test owner cancelling an offer sets status to CANCELLED."""
    mock_db = MagicMock()
    owner_id = uuid4()
    business_id = uuid4()
    offer_id = uuid4()

    business = Business(id=business_id, owner_id=owner_id)
    offer = Offer(
        id=offer_id,
        business_id=business_id,
        business=business,
        status=OfferStatus.ACTIVE,
    )
    mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = (
        offer
    )

    owner = User(id=owner_id, role=UserRole.OWNER)
    cancelled = OfferService.delete_or_cancel_offer(offer_id, owner, mock_db)
    assert cancelled.status == OfferStatus.CANCELLED
    mock_db.commit.assert_called_once()


def test_redeem_offer_verified_student_success():
    """Test verified student successfully redeems active offer."""
    mock_db = MagicMock()
    student_user_id = uuid4()
    offer_id = uuid4()

    student_user = User(id=student_user_id, role=UserRole.STUDENT)
    student_profile = Student(
        user_id=student_user_id,
        verification_status=VerificationStatus.VERIFIED,
    )

    now = datetime.now(timezone.utc)
    offer = Offer(
        id=offer_id,
        title="50% Off",
        status=OfferStatus.ACTIVE,
        valid_from=now - timedelta(days=1),
        valid_until=now + timedelta(days=5),
        max_redemptions=100,
        redemption_count=10,
    )

    def query_side_effect(*args, **kwargs):
        m = MagicMock()
        model = args[0] if args else None
        if model is Student:
            m.filter.return_value.first.return_value = student_profile
        elif model is Offer:
            m.options.return_value.filter.return_value.first.return_value = offer
        elif model is OfferRedemption:
            # Check for existing pending redemption (None) and unique code check (None)
            m.filter.return_value.first.return_value = None
        return m

    mock_db.query.side_effect = query_side_effect

    redemption = OfferService.redeem_offer(offer_id, student_user, mock_db)
    assert redemption.offer_id == offer_id
    assert redemption.user_id == student_user_id
    assert redemption.verification_code.startswith("OFR-")
    assert redemption.status == OfferRedemptionStatus.PENDING
    assert offer.redemption_count == 11
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


def test_redeem_offer_unverified_student_rejected():
    """Test unverified student is rejected with 403."""
    mock_db = MagicMock()
    student_user_id = uuid4()
    offer_id = uuid4()

    student_user = User(id=student_user_id, role=UserRole.STUDENT)
    student_profile = Student(
        user_id=student_user_id,
        verification_status=VerificationStatus.UNVERIFIED,
    )
    mock_db.query.return_value.filter.return_value.first.return_value = student_profile

    with pytest.raises(HTTPException) as exc:
        OfferService.redeem_offer(offer_id, student_user, mock_db)
    assert exc.value.status_code == 403
    assert "verified" in exc.value.detail.lower()


def test_redeem_offer_limit_reached_rejected():
    """Test redeeming offer that has reached max_redemptions raises 400."""
    mock_db = MagicMock()
    student_user_id = uuid4()
    offer_id = uuid4()

    student_user = User(id=student_user_id, role=UserRole.STUDENT)
    student_profile = Student(
        user_id=student_user_id,
        verification_status=VerificationStatus.VERIFIED,
    )

    now = datetime.now(timezone.utc)
    offer = Offer(
        id=offer_id,
        status=OfferStatus.ACTIVE,
        valid_from=now - timedelta(days=1),
        valid_until=now + timedelta(days=5),
        max_redemptions=5,
        redemption_count=5,  # Limit reached
    )

    def query_side_effect(*args, **kwargs):
        m = MagicMock()
        model = args[0] if args else None
        if model is Student:
            m.filter.return_value.first.return_value = student_profile
        elif model is Offer:
            m.options.return_value.filter.return_value.first.return_value = offer
        return m

    mock_db.query.side_effect = query_side_effect

    with pytest.raises(HTTPException) as exc:
        OfferService.redeem_offer(offer_id, student_user, mock_db)
    assert exc.value.status_code == 400
    assert "maximum" in exc.value.detail.lower()


def test_validate_redemption_merchant_success():
    """Test merchant successfully validates and completes a redemption code."""
    mock_db = MagicMock()
    owner_id = uuid4()
    business_id = uuid4()
    offer_id = uuid4()
    student_id = uuid4()
    redemption_id = uuid4()

    merchant = User(id=owner_id, role=UserRole.OWNER)
    business = Business(id=business_id, owner_id=owner_id, name="Campus Cafe")

    offer = Offer(
        id=offer_id,
        business_id=business_id,
        title="20% Off",
        discount_type=OfferDiscountType.PERCENTAGE,
        discount_value=20.0,
    )

    now = datetime.now(timezone.utc)
    redemption = OfferRedemption(
        id=redemption_id,
        offer_id=offer_id,
        offer=offer,
        user_id=student_id,
        verification_code="OFR-ABC123",
        status=OfferRedemptionStatus.PENDING,
        expires_at=now + timedelta(hours=1),
    )

    def query_side_effect(*args, **kwargs):
        m = MagicMock()
        model = args[0] if args else None
        if model is Business:
            m.filter.return_value.first.return_value = business
        elif model is OfferRedemption:
            m.options.return_value.filter.return_value.first.return_value = redemption
        elif model is Student:
            m.filter.return_value.first.return_value = Student(
                user_id=student_id, department="Computer Science"
            )
        return m

    mock_db.query.side_effect = query_side_effect

    res = OfferService.validate_redemption(
        business_id=business_id,
        verification_code="OFR-ABC123",
        current_user=merchant,
        db=mock_db,
    )

    assert res.success is True
    assert res.status == OfferRedemptionStatus.COMPLETED
    assert res.discount_value == 20.0
    assert redemption.status == OfferRedemptionStatus.COMPLETED
    mock_db.commit.assert_called_once()


def test_validate_redemption_wrong_business_rejected():
    """Test merchant validating code for a different business raises 400."""
    mock_db = MagicMock()
    owner_id = uuid4()
    business_id = uuid4()
    other_business_id = uuid4()
    offer_id = uuid4()

    merchant = User(id=owner_id, role=UserRole.OWNER)
    business = Business(id=business_id, owner_id=owner_id)

    offer = Offer(
        id=offer_id, business_id=other_business_id
    )  # Belongs to other business
    redemption = OfferRedemption(
        offer_id=offer_id,
        offer=offer,
        verification_code="OFR-OTHER1",
        status=OfferRedemptionStatus.PENDING,
    )

    def query_side_effect(*args, **kwargs):
        m = MagicMock()
        model = args[0] if args else None
        if model is Business:
            m.filter.return_value.first.return_value = business
        elif model is OfferRedemption:
            m.options.return_value.filter.return_value.first.return_value = redemption
        return m

    mock_db.query.side_effect = query_side_effect

    with pytest.raises(HTTPException) as exc:
        OfferService.validate_redemption(
            business_id=business_id,
            verification_code="OFR-OTHER1",
            current_user=merchant,
            db=mock_db,
        )
    assert exc.value.status_code == 400
    assert "different business" in exc.value.detail.lower()
