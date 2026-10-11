"""Review Service

Business logic for student reviews, category-specific rating dimensions,
helpful voting, business responses, moderation reporting, and business rating aggregation.
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.business import Business
from app.models.rating_dimension import RatingDimension
from app.models.review import Review, ReviewStatus, VerificationLevel
from app.models.review_photo import ReviewPhoto
from app.models.review_rating import ReviewRating
from app.models.review_report import (
    ReviewReport,
    ReviewReportReason,
    ReviewReportStatus,
)
from app.models.review_response import ReviewResponse
from app.core.sanitizer import sanitize_text
from app.models.student import Student, VerificationStatus
from app.models.user import User, UserRole
from app.schemas.rating_dimension import RatingDimensionCreate
from app.schemas.review import (
    ReviewCreate,
    ReviewDetailResponse,
    ReviewPhotoResponse,
    ReviewRatingResponse,
    ReviewResponseItem,
    ReviewUpdate,
    ReviewUserResponse,
)


class ReviewService:
    """Service for managing the structured multi-dimensional review system."""

    @classmethod
    def get_reviewer_info(cls, user_id: UUID, db: Session) -> tuple[str, bool]:
        """Generate privacy-preserving student display name and verification flag.

        Example:
            Verified MIT AOE Student (is_verified=True)
            Anonymous Student (is_verified=False)
        """
        student = db.query(Student).filter(Student.user_id == user_id).first()
        if (
            student
            and getattr(student, "verification_status", None)
            == VerificationStatus.VERIFIED
        ):
            college_name = "College"
            college = getattr(student, "college", None)
            if college:
                college_name = getattr(college, "short_name", None) or getattr(
                    college, "name", "College"
                )
            return f"Verified {college_name} Student", True
        return "Anonymous Student", False

    @classmethod
    def serialize_review_detail(
        cls, review: Review, db: Session
    ) -> ReviewDetailResponse:
        """Serialize a Review SQLAlchemy model into a full ReviewDetailResponse."""
        display_name, is_verified = cls.get_reviewer_info(review.user_id, db)

        ratings_list = []
        for r in review.ratings or []:
            dim_name = r.dimension.name if r.dimension else "Rating"
            ratings_list.append(
                ReviewRatingResponse(
                    dimension_id=r.dimension_id,
                    dimension=dim_name,
                    rating=r.rating,
                )
            )

        photos_list = [
            ReviewPhotoResponse(id=p.id, image_url=p.image_url, created_at=p.created_at)
            for p in (review.photos or [])
        ]

        response_item = None
        if review.response:
            response_item = ReviewResponseItem(
                id=review.response.id,
                response_text=review.response.response_text,
                created_at=review.response.created_at,
                updated_at=review.response.updated_at,
            )

        return ReviewDetailResponse(
            id=review.id,
            business_id=review.business_id,
            user=ReviewUserResponse(
                id=review.user_id,
                display_name=display_name,
                is_verified_student=is_verified,
            ),
            overall_rating=review.overall_rating,
            review_text=review.review_text,
            verification_level=str(
                review.verification_level.value
                if hasattr(review.verification_level, "value")
                else review.verification_level
            ),
            status=str(
                review.status.value
                if hasattr(review.status, "value")
                else review.status
            ),
            ratings=ratings_list,
            photos=photos_list,
            helpful_count=review.helpful_count or 0,
            has_response=review.response is not None,
            response=response_item,
            created_at=review.created_at,
            updated_at=review.updated_at,
        )

    @classmethod
    def create_review(
        cls,
        business_id: UUID,
        user_id: UUID,
        review_data: ReviewCreate,
        db: Session,
    ) -> Review:
        """Create a new review for a business.

        Enforces student role, single active review constraint, and updates business ratings.

        Args:
            business_id: Target business UUID.
            user_id: Reviewer's user UUID.
            review_data: Review submission data.
            db: Database session.

        Returns:
            Created Review instance.
        """
        # Verify business exists
        business = db.query(Business).filter(Business.id == business_id).first()
        if not business:
            raise ValueError("Business not found")

        # Verify user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")

        # Ensure user has STUDENT role
        if user.role != UserRole.STUDENT and user.role != UserRole.ADMIN:
            raise ValueError("Only students can submit reviews")

        # Check for existing active review
        existing = (
            db.query(Review)
            .filter(
                Review.business_id == business_id,
                Review.user_id == user_id,
                Review.status == ReviewStatus.ACTIVE,
                Review.deleted_at.is_(None),
            )
            .first()
        )
        if existing:
            raise ValueError("You have already reviewed this business")

        # Determine verification level
        student = db.query(Student).filter(Student.user_id == user_id).first()
        if student and student.verification_status == VerificationStatus.VERIFIED:
            verification_level = VerificationLevel.VERIFIED_STUDENT
        else:
            verification_level = VerificationLevel.UNVERIFIED

        now = datetime.now(timezone.utc)
        review = Review(
            id=uuid4(),
            business_id=business_id,
            user_id=user_id,
            overall_rating=review_data.overall_rating,
            review_text=sanitize_text(review_data.review_text.strip())
            if review_data.review_text
            else None,
            verification_level=verification_level,
            status=ReviewStatus.ACTIVE,
            helpful_count=0,
            created_at=now,
            updated_at=now,
        )
        db.add(review)
        db.flush()

        # Add dimensional ratings
        if review_data.ratings:
            for item in review_data.ratings:
                dim_rating = ReviewRating(
                    id=uuid4(),
                    review_id=review.id,
                    dimension_id=item.dimension_id,
                    rating=item.rating,
                )
                db.add(dim_rating)

        # Add photos
        if review_data.photo_urls:
            for url in review_data.photo_urls:
                photo = ReviewPhoto(
                    id=uuid4(),
                    review_id=review.id,
                    image_url=url.strip(),
                    created_at=now,
                )
                db.add(photo)

        db.flush()
        cls.recalculate_business_ratings(business_id, db)
        db.commit()
        db.refresh(review)
        return review

    @classmethod
    def update_review(
        cls,
        review_id: UUID,
        user_id: UUID,
        update_data: ReviewUpdate,
        db: Session,
    ) -> Optional[Review]:
        """Update a student's own review.

        Args:
            review_id: Review UUID.
            user_id: Requesting user UUID.
            update_data: Updated fields.
            db: Database session.

        Returns:
            Updated Review instance or None.
        """
        review = (
            db.query(Review)
            .filter(Review.id == review_id, Review.deleted_at.is_(None))
            .first()
        )
        if not review:
            return None

        if review.user_id != user_id:
            raise PermissionError("You can only edit your own review")

        now = datetime.now(timezone.utc)
        if update_data.overall_rating is not None:
            review.overall_rating = update_data.overall_rating
        if update_data.review_text is not None:
            review.review_text = (
                sanitize_text(update_data.review_text.strip())
                if update_data.review_text
                else None
            )

        # Update dimensional ratings if provided
        if update_data.ratings is not None:
            db.query(ReviewRating).filter(ReviewRating.review_id == review.id).delete(
                synchronize_session=False
            )
            for item in update_data.ratings:
                dim_rating = ReviewRating(
                    id=uuid4(),
                    review_id=review.id,
                    dimension_id=item.dimension_id,
                    rating=item.rating,
                )
                db.add(dim_rating)

        # Update photos if provided
        if update_data.photo_urls is not None:
            db.query(ReviewPhoto).filter(ReviewPhoto.review_id == review.id).delete(
                synchronize_session=False
            )
            for url in update_data.photo_urls:
                photo = ReviewPhoto(
                    id=uuid4(),
                    review_id=review.id,
                    image_url=url.strip(),
                    created_at=now,
                )
                db.add(photo)

        review.updated_at = now
        db.flush()
        cls.recalculate_business_ratings(review.business_id, db)
        db.commit()
        db.refresh(review)
        return review

    @classmethod
    def delete_review(
        cls,
        review_id: UUID,
        user_id: UUID,
        db: Session,
        is_admin: bool = False,
    ) -> bool:
        """Soft-delete a review and recompute business rating aggregates.

        Args:
            review_id: Review UUID.
            user_id: Requesting user UUID.
            db: Database session.
            is_admin: Whether requester has ADMIN role.

        Returns:
            True if deleted, False if not found.
        """
        review = (
            db.query(Review)
            .filter(Review.id == review_id, Review.deleted_at.is_(None))
            .first()
        )
        if not review:
            return False

        if not is_admin and review.user_id != user_id:
            raise PermissionError("You can only delete your own review")

        review.status = ReviewStatus.REMOVED
        review.deleted_at = datetime.now(timezone.utc)
        db.flush()
        cls.recalculate_business_ratings(review.business_id, db)
        db.commit()
        return True

    @classmethod
    def get_review_by_id(cls, review_id: UUID, db: Session) -> Optional[Review]:
        """Get an active review by ID."""
        return (
            db.query(Review)
            .filter(Review.id == review_id, Review.deleted_at.is_(None))
            .first()
        )

    @classmethod
    def list_reviews(
        cls,
        business_id: UUID,
        db: Session,
        min_rating: Optional[int] = None,
        verification_level: Optional[str] = None,
        sort: str = "newest",
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Review], int, dict[str, float]]:
        """List active reviews for a business with filtering, sorting, and dimensional breakdown.

        Args:
            business_id: Business UUID.
            db: Database session.
            min_rating: Filter by minimum overall rating (1-5).
            verification_level: Filter by verification level.
            sort: Sort order ('newest', 'highest_rated', 'lowest_rated', 'most_helpful').
            page: Page number (1-based).
            page_size: Items per page.

        Returns:
            Tuple of (reviews_list, total_count, rating_breakdown_dict).
        """
        query = db.query(Review).filter(
            Review.business_id == business_id,
            Review.status == ReviewStatus.ACTIVE,
            Review.deleted_at.is_(None),
        )

        if min_rating is not None:
            query = query.filter(Review.overall_rating >= min_rating)
        if verification_level:
            query = query.filter(Review.verification_level == verification_level)

        total = query.count()

        # Sorting
        if sort == "highest_rated":
            query = query.order_by(
                Review.overall_rating.desc(), Review.created_at.desc()
            )
        elif sort == "lowest_rated":
            query = query.order_by(
                Review.overall_rating.asc(), Review.created_at.desc()
            )
        elif sort == "most_helpful":
            query = query.order_by(
                Review.helpful_count.desc(), Review.created_at.desc()
            )
        else:  # newest
            query = query.order_by(Review.created_at.desc())

        skip = max(0, (page - 1) * page_size)
        reviews = query.offset(skip).limit(page_size).all()

        # Compute dimensional rating breakdown across all active reviews for this business
        breakdown = cls.calculate_rating_breakdown(business_id, db)

        return reviews, total, breakdown

    @classmethod
    def calculate_rating_breakdown(
        cls, business_id: UUID, db: Session
    ) -> dict[str, float]:
        """Calculate average scores for each evaluation dimension across active reviews."""
        rows = (
            db.query(
                RatingDimension.name,
                func.avg(ReviewRating.rating).label("avg_rating"),
            )
            .join(ReviewRating, ReviewRating.dimension_id == RatingDimension.id)
            .join(Review, Review.id == ReviewRating.review_id)
            .filter(
                Review.business_id == business_id,
                Review.status == ReviewStatus.ACTIVE,
                Review.deleted_at.is_(None),
            )
            .group_by(RatingDimension.name)
            .all()
        )

        breakdown = {}
        for name, avg_score in rows:
            if avg_score is not None:
                breakdown[name] = round(float(avg_score), 1)
        return breakdown

    @classmethod
    def recalculate_business_ratings(cls, business_id: UUID, db: Session) -> None:
        """Recalculate denormalized average_rating and review_count on Business."""
        stats = (
            db.query(
                func.count(Review.id).label("total"),
                func.avg(Review.overall_rating).label("average"),
            )
            .filter(
                Review.business_id == business_id,
                Review.status == ReviewStatus.ACTIVE,
                Review.deleted_at.is_(None),
            )
            .first()
        )

        business = db.query(Business).filter(Business.id == business_id).first()
        if business:
            count = 0
            avg = None
            if stats:
                try:
                    count = stats[0] or 0
                    avg = stats[1]
                except (TypeError, IndexError, KeyError):
                    count = getattr(stats, "total", 0)
                    avg = getattr(stats, "average", None)
            business.review_count = count or 0
            business.average_rating = round(float(avg), 2) if avg is not None else None

    @classmethod
    def respond_to_review(
        cls,
        review_id: UUID,
        owner_id: UUID,
        response_text: str,
        db: Session,
    ) -> ReviewResponse:
        """Create or update a business owner's response to a customer review.

        Args:
            review_id: Target review UUID.
            owner_id: Business owner UUID.
            response_text: Text of owner reply.
            db: Database session.

        Returns:
            Created or updated ReviewResponse.
        """
        review = (
            db.query(Review)
            .filter(Review.id == review_id, Review.deleted_at.is_(None))
            .first()
        )
        if not review:
            raise ValueError("Review not found")

        # Verify owner owns this business
        business = db.query(Business).filter(Business.id == review.business_id).first()
        if not business or business.owner_id != owner_id:
            user = db.query(User).filter(User.id == owner_id).first()
            if not user or user.role != UserRole.ADMIN:
                raise PermissionError(
                    "Only the business owner or admin can reply to this review"
                )

        now = datetime.now(timezone.utc)
        sanitized_response = sanitize_text(response_text.strip())
        existing = (
            db.query(ReviewResponse)
            .filter(ReviewResponse.review_id == review_id)
            .first()
        )
        if existing:
            existing.response_text = sanitized_response
            existing.updated_at = now
            db.commit()
            db.refresh(existing)
            return existing

        response = ReviewResponse(
            id=uuid4(),
            review_id=review_id,
            owner_id=owner_id,
            response_text=sanitized_response,
            created_at=now,
            updated_at=now,
        )
        db.add(response)
        db.commit()
        db.refresh(response)
        return response

    @classmethod
    def report_review(
        cls,
        review_id: UUID,
        reported_by: UUID,
        reason: str,
        description: Optional[str],
        db: Session,
    ) -> ReviewReport:
        """Report a review for policy violation or moderation.

        Args:
            review_id: Review UUID.
            reported_by: Reporter user UUID.
            reason: Report reason string.
            description: Optional details.
            db: Database session.

        Returns:
            Created ReviewReport instance.
        """
        review = db.query(Review).filter(Review.id == review_id).first()
        if not review:
            raise ValueError("Review not found")

        report = ReviewReport(
            id=uuid4(),
            review_id=review_id,
            reported_by=reported_by,
            reason=ReviewReportReason(reason),
            description=sanitize_text(description.strip()) if description else None,
            status=ReviewReportStatus.PENDING,
            created_at=datetime.now(timezone.utc),
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        return report

    @classmethod
    def vote_helpful(cls, review_id: UUID, db: Session) -> Optional[Review]:
        """Increment helpful counter for a review."""
        review = (
            db.query(Review)
            .filter(Review.id == review_id, Review.deleted_at.is_(None))
            .first()
        )
        if not review:
            return None

        review.helpful_count = (review.helpful_count or 0) + 1
        db.commit()
        db.refresh(review)
        return review

    @classmethod
    def get_dimensions_for_business(
        cls, business_id: UUID, db: Session
    ) -> list[RatingDimension]:
        """Fetch applicable rating dimensions based on the business's assigned categories."""
        business = db.query(Business).filter(Business.id == business_id).first()
        if not business:
            return []

        category_ids = [c.id for c in (business.categories or [])]

        query = db.query(RatingDimension)
        if category_ids:
            query = query.filter(
                (RatingDimension.category_id.in_(category_ids))
                | (RatingDimension.category_id.is_(None))
            )
        else:
            query = query.filter(RatingDimension.category_id.is_(None))

        return query.order_by(
            RatingDimension.display_order.asc(), RatingDimension.name.asc()
        ).all()

    @classmethod
    def create_dimension(
        cls, dimension_data: RatingDimensionCreate, db: Session
    ) -> RatingDimension:
        """Create a new category rating dimension."""
        from app.services.category_service import CategoryService

        slug = dimension_data.slug or CategoryService.slugify(dimension_data.name)
        dim = RatingDimension(
            id=uuid4(),
            category_id=dimension_data.category_id,
            name=dimension_data.name.strip(),
            slug=slug,
            description=dimension_data.description.strip()
            if dimension_data.description
            else None,
            display_order=dimension_data.display_order,
        )
        db.add(dim)
        db.commit()
        db.refresh(dim)
        return dim
