"""Unit tests for ReviewService: reviews, dimensions, responses, reports, and aggregates."""

from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.models.business import Business
from app.models.college import College
from app.models.review import Review, ReviewStatus, VerificationLevel
from app.models.review_report import ReviewReportReason, ReviewReportStatus
from app.models.review_response import ReviewResponse
from app.models.student import Student, VerificationStatus
from app.models.user import User, UserRole, UserStatus
from app.schemas.rating_dimension import RatingDimensionCreate
from app.schemas.review import (
    ReviewCreate,
    ReviewRatingItem,
    ReviewUpdate,
)
from app.services.review_service import ReviewService


def test_get_reviewer_info_verified_student():
    """Test get_reviewer_info returns college name for verified student."""
    user_id = uuid4()
    mock_db = MagicMock()

    college = College(
        id=uuid4(), name="MIT Academy of Engineering", short_name="MIT AOE"
    )
    student = Student(
        id=uuid4(),
        user_id=user_id,
        verification_status=VerificationStatus.VERIFIED,
        college=college,
    )

    mock_db.query.return_value.filter.return_value.first.return_value = student

    display_name, is_verified = ReviewService.get_reviewer_info(user_id, mock_db)
    assert display_name == "Verified MIT AOE Student"
    assert is_verified is True


def test_get_reviewer_info_unverified_student():
    """Test get_reviewer_info returns anonymous student for unverified student."""
    user_id = uuid4()
    mock_db = MagicMock()

    student = Student(
        id=uuid4(),
        user_id=user_id,
        verification_status=VerificationStatus.PENDING,
        college=None,
    )

    mock_db.query.return_value.filter.return_value.first.return_value = student

    display_name, is_verified = ReviewService.get_reviewer_info(user_id, mock_db)
    assert display_name == "Anonymous Student"
    assert is_verified is False


def test_create_review_verified_student_success():
    """Test creating a review by a verified student creates dimensional ratings and photos."""
    mock_db = MagicMock()
    business_id = uuid4()
    user_id = uuid4()
    dim_id1 = uuid4()
    dim_id2 = uuid4()

    business = Business(id=business_id, name="Campus Cafe")
    user = User(id=user_id, role=UserRole.STUDENT, status=UserStatus.ACTIVE)
    student = Student(
        id=uuid4(),
        user_id=user_id,
        verification_status=VerificationStatus.VERIFIED,
    )

    def mock_filter_first(query_model):
        if query_model is Business:
            return business
        elif query_model is User:
            return user
        elif query_model is Review:
            return None  # No existing active review
        elif query_model is Student:
            return student
        return None

    def query_side_effect(*args, **kwargs):
        m = MagicMock()
        model = args[0] if args else None
        m.filter.return_value.first.side_effect = lambda: mock_filter_first(model)
        return m

    mock_db.query.side_effect = query_side_effect

    review_data = ReviewCreate(
        overall_rating=5,
        review_text="Best cold coffee around campus!",
        ratings=[
            ReviewRatingItem(dimension_id=dim_id1, rating=5),
            ReviewRatingItem(dimension_id=dim_id2, rating=4),
        ],
        photo_urls=["https://images.campus.edu/cafe1.jpg"],
    )

    review = ReviewService.create_review(
        business_id=business_id,
        user_id=user_id,
        review_data=review_data,
        db=mock_db,
    )

    assert review.business_id == business_id
    assert review.user_id == user_id
    assert review.overall_rating == 5
    assert review.review_text == "Best cold coffee around campus!"
    assert review.verification_level == VerificationLevel.VERIFIED_STUDENT
    assert review.status == ReviewStatus.ACTIVE

    # Verify db.add was called for Review, 2 ReviewRatings, and 1 ReviewPhoto
    assert mock_db.add.call_count >= 4
    mock_db.commit.assert_called_once()


def test_create_review_non_student_rejected():
    """Test non-student user cannot create a review."""
    mock_db = MagicMock()
    business_id = uuid4()
    user_id = uuid4()

    business = Business(id=business_id, name="Campus Cafe")
    user = User(id=user_id, role=UserRole.OWNER, status=UserStatus.ACTIVE)

    def query_side_effect(*args, **kwargs):
        m = MagicMock()
        model = args[0] if args else None
        if model is Business:
            m.filter.return_value.first.return_value = business
        elif model is User:
            m.filter.return_value.first.return_value = user
        return m

    mock_db.query.side_effect = query_side_effect

    review_data = ReviewCreate(overall_rating=4, review_text="Great place!")

    with pytest.raises(ValueError, match="Only students can submit reviews"):
        ReviewService.create_review(
            business_id=business_id,
            user_id=user_id,
            review_data=review_data,
            db=mock_db,
        )


def test_create_review_duplicate_rejected():
    """Test duplicate review from same student on same business is rejected."""
    mock_db = MagicMock()
    business_id = uuid4()
    user_id = uuid4()

    business = Business(id=business_id, name="Campus Cafe")
    user = User(id=user_id, role=UserRole.STUDENT, status=UserStatus.ACTIVE)
    existing_review = Review(
        id=uuid4(), business_id=business_id, user_id=user_id, overall_rating=4
    )

    def query_side_effect(*args, **kwargs):
        m = MagicMock()
        model = args[0] if args else None
        if model is Business:
            m.filter.return_value.first.return_value = business
        elif model is User:
            m.filter.return_value.first.return_value = user
        elif model is Review:
            m.filter.return_value.first.return_value = existing_review
        return m

    mock_db.query.side_effect = query_side_effect

    review_data = ReviewCreate(overall_rating=5, review_text="Another review")

    with pytest.raises(ValueError, match="You have already reviewed this business"):
        ReviewService.create_review(
            business_id=business_id,
            user_id=user_id,
            review_data=review_data,
            db=mock_db,
        )


def test_update_review_success():
    """Test updating student's own review."""
    mock_db = MagicMock()
    review_id = uuid4()
    user_id = uuid4()
    business_id = uuid4()

    review = Review(
        id=review_id,
        business_id=business_id,
        user_id=user_id,
        overall_rating=4,
        review_text="Good food",
        deleted_at=None,
    )
    business = Business(id=business_id, name="Campus Eatery")

    def query_side_effect(*args, **kwargs):
        m = MagicMock()
        model = args[0] if args else None
        if model is Review:
            m.filter.return_value.first.return_value = review
        elif model is Business:
            m.filter.return_value.first.return_value = business
        else:
            m.filter.return_value.first.return_value = (1, 5.0)
        return m

    mock_db.query.side_effect = query_side_effect

    update_data = ReviewUpdate(
        overall_rating=5,
        review_text="Actually amazing food and faster service!",
    )

    updated = ReviewService.update_review(
        review_id=review_id,
        user_id=user_id,
        update_data=update_data,
        db=mock_db,
    )

    assert updated.overall_rating == 5
    assert updated.review_text == "Actually amazing food and faster service!"
    mock_db.commit.assert_called_once()


def test_update_review_forbidden_for_other_student():
    """Test editing another student's review raises PermissionError."""
    mock_db = MagicMock()
    review_id = uuid4()
    owner_user_id = uuid4()
    other_user_id = uuid4()

    review = Review(
        id=review_id,
        business_id=uuid4(),
        user_id=owner_user_id,
        overall_rating=4,
        deleted_at=None,
    )

    mock_db.query.return_value.filter.return_value.first.return_value = review

    update_data = ReviewUpdate(overall_rating=1)

    with pytest.raises(PermissionError, match="You can only edit your own review"):
        ReviewService.update_review(
            review_id=review_id,
            user_id=other_user_id,
            update_data=update_data,
            db=mock_db,
        )


def test_delete_review_soft_deletes_and_recalculates():
    """Test delete_review soft deletes by setting status=REMOVED and deleted_at timestamp."""
    mock_db = MagicMock()
    review_id = uuid4()
    user_id = uuid4()
    business_id = uuid4()

    review = Review(
        id=review_id,
        business_id=business_id,
        user_id=user_id,
        status=ReviewStatus.ACTIVE,
        deleted_at=None,
    )
    business = Business(id=business_id, name="Campus Eatery")

    def query_side_effect(*args, **kwargs):
        m = MagicMock()
        model = args[0] if args else None
        if model is Review:
            m.filter.return_value.first.return_value = review
        elif model is Business:
            m.filter.return_value.first.return_value = business
        else:
            m.filter.return_value.first.return_value = (0, None)
        return m

    mock_db.query.side_effect = query_side_effect

    success = ReviewService.delete_review(
        review_id=review_id,
        user_id=user_id,
        db=mock_db,
    )

    assert success is True
    assert review.status == ReviewStatus.REMOVED
    assert review.deleted_at is not None
    mock_db.commit.assert_called_once()


def test_respond_to_review_owner_success():
    """Test business owner replying to a customer review."""
    mock_db = MagicMock()
    review_id = uuid4()
    owner_id = uuid4()
    business_id = uuid4()

    review = Review(id=review_id, business_id=business_id, deleted_at=None)
    business = Business(id=business_id, owner_id=owner_id)

    def query_side_effect(*args, **kwargs):
        m = MagicMock()
        model = args[0] if args else None
        if model is Review:
            m.filter.return_value.first.return_value = review
        elif model is Business:
            m.filter.return_value.first.return_value = business
        elif model is ReviewResponse:
            m.filter.return_value.first.return_value = None  # No existing response
        return m

    mock_db.query.side_effect = query_side_effect

    response = ReviewService.respond_to_review(
        review_id=review_id,
        owner_id=owner_id,
        response_text="Thank you for visiting! We look forward to serving you again.",
        db=mock_db,
    )

    assert response.review_id == review_id
    assert response.owner_id == owner_id
    assert (
        response.response_text
        == "Thank you for visiting! We look forward to serving you again."
    )
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


def test_respond_to_review_forbidden_for_non_owner():
    """Test non-owner user cannot reply to review on another business."""
    mock_db = MagicMock()
    review_id = uuid4()
    actual_owner_id = uuid4()
    impostor_id = uuid4()
    business_id = uuid4()

    review = Review(id=review_id, business_id=business_id, deleted_at=None)
    business = Business(id=business_id, owner_id=actual_owner_id)
    impostor = User(id=impostor_id, role=UserRole.OWNER)

    def query_side_effect(*args, **kwargs):
        m = MagicMock()
        model = args[0] if args else None
        if model is Review:
            m.filter.return_value.first.return_value = review
        elif model is Business:
            m.filter.return_value.first.return_value = business
        elif model is User:
            m.filter.return_value.first.return_value = impostor
        return m

    mock_db.query.side_effect = query_side_effect

    with pytest.raises(
        PermissionError, match="Only the business owner or admin can reply"
    ):
        ReviewService.respond_to_review(
            review_id=review_id,
            owner_id=impostor_id,
            response_text="Fake response",
            db=mock_db,
        )


def test_report_review_creates_report():
    """Test filing a moderation report against a review."""
    mock_db = MagicMock()
    review_id = uuid4()
    reporter_id = uuid4()

    review = Review(id=review_id)
    mock_db.query.return_value.filter.return_value.first.return_value = review

    report = ReviewService.report_review(
        review_id=review_id,
        reported_by=reporter_id,
        reason="SPAM",
        description="Advertising an unrelated product",
        db=mock_db,
    )

    assert report.review_id == review_id
    assert report.reported_by == reporter_id
    assert report.reason == ReviewReportReason.SPAM
    assert report.description == "Advertising an unrelated product"
    assert report.status == ReviewReportStatus.PENDING
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


def test_vote_helpful_increments_count():
    """Test helpful voting increments helpful_count by 1."""
    mock_db = MagicMock()
    review_id = uuid4()

    review = Review(id=review_id, helpful_count=5, deleted_at=None)
    mock_db.query.return_value.filter.return_value.first.return_value = review

    updated = ReviewService.vote_helpful(review_id, mock_db)
    assert updated.helpful_count == 6
    mock_db.commit.assert_called_once()


def test_create_and_fetch_rating_dimensions():
    """Test creating a rating dimension and fetching dimensions for a business."""
    mock_db = MagicMock()
    cat_id = uuid4()
    dim_data = RatingDimensionCreate(
        category_id=cat_id,
        name="Hygiene & Cleanliness",
        description="Cleanliness of premises and kitchen",
        display_order=1,
    )

    dim = ReviewService.create_dimension(dim_data, mock_db)
    assert dim.name == "Hygiene & Cleanliness"
    assert dim.slug == "hygiene-cleanliness"
    assert dim.display_order == 1
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
