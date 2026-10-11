"""Owner Analytics Service.

Aggregates KPI metrics, engagement signals, and business performance analytics
for merchants and platform administrators.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.business import Business
from app.models.business_interaction import BusinessInteraction, InteractionType
from app.models.business_photo import BusinessPhoto, BusinessPhotoStatus
from app.models.favorite import Favorite
from app.models.notification import Notification
from app.models.offer import Offer, OfferStatus
from app.models.offer_redemption import OfferRedemption
from app.models.review import Review, ReviewStatus
from app.models.service import Service
from app.schemas.owner_analytics import (
    BusinessAnalyticsResponse,
    BusinessInteractionResponse,
    BusinessSummaryCard,
    OwnerDashboardResponse,
    RatingBreakdown,
    RecentRedemptionItem,
    RecentReviewItem,
)


class OwnerAnalyticsService:
    """Service handling merchant analytics aggregation and interaction logging."""

    @classmethod
    def record_interaction(
        cls,
        db: Session,
        business_id: UUID,
        interaction_type: str,
        user_id: Optional[UUID] = None,
    ) -> BusinessInteractionResponse:
        """Record customer engagement interaction on a business listing."""
        business = (
            db.query(Business)
            .filter(Business.id == business_id, Business.deleted_at.is_(None))
            .first()
        )
        if not business:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Business {business_id} not found",
            )

        interaction = BusinessInteraction(
            id=uuid4(),
            business_id=business_id,
            user_id=user_id,
            interaction_type=interaction_type,
            created_at=datetime.now(timezone.utc),
        )
        db.add(interaction)
        try:
            db.commit()
            db.refresh(interaction)
        except Exception:
            try:
                db.flush()
            except Exception:
                pass

        return BusinessInteractionResponse(
            id=interaction.id,
            business_id=interaction.business_id,
            interaction_type=interaction.interaction_type,
            created_at=interaction.created_at,
        )

    @classmethod
    def get_business_analytics(
        cls,
        db: Session,
        business_id: UUID,
        days: int = 30,
    ) -> BusinessAnalyticsResponse:
        """Aggregate comprehensive engagement and performance analytics for a single business."""
        business = (
            db.query(Business)
            .filter(Business.id == business_id, Business.deleted_at.is_(None))
            .first()
        )
        if not business:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Business {business_id} not found",
            )

        # 1. Interaction counts within time window
        since_time = datetime.now(timezone.utc) - timedelta(days=days)
        interactions_query = db.query(BusinessInteraction).filter(
            BusinessInteraction.business_id == business_id,
            BusinessInteraction.created_at >= since_time,
        )

        profile_views = interactions_query.filter(
            BusinessInteraction.interaction_type == InteractionType.PROFILE_VIEW.value
        ).count()
        direction_requests = interactions_query.filter(
            BusinessInteraction.interaction_type
            == InteractionType.DIRECTION_CLICK.value
        ).count()
        calls = interactions_query.filter(
            BusinessInteraction.interaction_type == InteractionType.CALL_CLICK.value
        ).count()
        offer_views = interactions_query.filter(
            BusinessInteraction.interaction_type == InteractionType.OFFER_VIEW.value
        ).count()

        # 2. Favorites count
        favorites_count = (
            db.query(Favorite).filter(Favorite.business_id == business_id).count()
        )

        # 3. Offers and redemptions
        active_offers_count = (
            db.query(Offer)
            .filter(
                Offer.business_id == business_id,
                Offer.status == OfferStatus.ACTIVE,
            )
            .count()
        )

        redemptions_query = (
            db.query(OfferRedemption)
            .join(Offer, OfferRedemption.offer_id == Offer.id)
            .filter(Offer.business_id == business_id)
        )
        offer_redemptions = redemptions_query.count()

        recent_redemptions_rows = (
            redemptions_query.order_by(desc(OfferRedemption.redeemed_at)).limit(5).all()
        )
        recent_redemptions = [
            RecentRedemptionItem(
                id=r.id,
                offer_id=r.offer_id,
                offer_title=r.offer.title if r.offer else "Promotional Offer",
                redeemed_at=r.redeemed_at,
                status=str(r.status.value if hasattr(r.status, "value") else r.status),
            )
            for r in recent_redemptions_rows
        ]

        # 4. Reviews and rating metrics
        reviews_query = db.query(Review).filter(
            Review.business_id == business_id,
            Review.status == ReviewStatus.ACTIVE,
        )
        reviews_rows = reviews_query.all()
        total_reviews = len(reviews_rows)

        rating_breakdown = RatingBreakdown()
        unanswered_count = 0
        total_rating_score = 0.0

        for rev in reviews_rows:
            rating = rev.overall_rating
            total_rating_score += rating
            if rating == 1:
                rating_breakdown.one_star += 1
            elif rating == 2:
                rating_breakdown.two_star += 1
            elif rating == 3:
                rating_breakdown.three_star += 1
            elif rating == 4:
                rating_breakdown.four_star += 1
            elif rating == 5:
                rating_breakdown.five_star += 1

            if not rev.response:
                unanswered_count += 1

        if total_reviews > 0:
            avg_rating = round(total_rating_score / total_reviews, 2)
        elif business.average_rating is not None:
            avg_rating = float(business.average_rating)
        else:
            avg_rating = None

        recent_reviews_rows = (
            reviews_query.order_by(desc(Review.created_at)).limit(5).all()
        )
        recent_reviews = [
            RecentReviewItem(
                id=rev.id,
                overall_rating=rev.overall_rating,
                comment=rev.review_text,
                created_at=rev.created_at,
                has_response=bool(rev.response),
                verification_level=str(
                    rev.verification_level.value
                    if hasattr(rev.verification_level, "value")
                    else rev.verification_level
                ),
            )
            for rev in recent_reviews_rows
        ]

        # 5. Services and Photos
        active_services_count = (
            db.query(Service)
            .filter(
                Service.business_id == business_id,
                Service.is_active.is_(True),
            )
            .count()
        )
        photos_count = (
            db.query(BusinessPhoto)
            .filter(
                BusinessPhoto.business_id == business_id,
                BusinessPhoto.status == BusinessPhotoStatus.ACTIVE,
            )
            .count()
        )

        return BusinessAnalyticsResponse(
            business_id=business.id,
            business_name=business.name,
            period_days=days,
            profile_views=profile_views,
            direction_requests=direction_requests,
            calls=calls,
            offer_views=offer_views,
            offer_redemptions=offer_redemptions,
            favorites_count=favorites_count,
            total_reviews=total_reviews,
            average_rating=avg_rating,
            rating_breakdown=rating_breakdown,
            unanswered_reviews_count=unanswered_count,
            active_offers_count=active_offers_count,
            active_services_count=active_services_count,
            photos_count=photos_count,
            recent_reviews=recent_reviews,
            recent_redemptions=recent_redemptions,
        )

    @classmethod
    def get_owner_dashboard(
        cls,
        db: Session,
        owner_id: UUID,
    ) -> OwnerDashboardResponse:
        """Calculate consolidated metrics and per-listing summary cards for an owner."""
        businesses = (
            db.query(Business)
            .filter(Business.owner_id == owner_id, Business.deleted_at.is_(None))
            .all()
        )

        total_profile_views = 0
        total_direction_requests = 0
        total_calls = 0
        total_reviews = 0
        total_redemptions = 0
        weighted_rating_sum = 0.0
        total_rated_reviews = 0

        business_cards = []

        for biz in businesses:
            p_views = (
                db.query(BusinessInteraction)
                .filter(
                    BusinessInteraction.business_id == biz.id,
                    BusinessInteraction.interaction_type
                    == InteractionType.PROFILE_VIEW.value,
                )
                .count()
            )
            d_reqs = (
                db.query(BusinessInteraction)
                .filter(
                    BusinessInteraction.business_id == biz.id,
                    BusinessInteraction.interaction_type
                    == InteractionType.DIRECTION_CLICK.value,
                )
                .count()
            )
            c_clicks = (
                db.query(BusinessInteraction)
                .filter(
                    BusinessInteraction.business_id == biz.id,
                    BusinessInteraction.interaction_type
                    == InteractionType.CALL_CLICK.value,
                )
                .count()
            )
            b_redemptions = (
                db.query(OfferRedemption)
                .join(Offer, OfferRedemption.offer_id == Offer.id)
                .filter(Offer.business_id == biz.id)
                .count()
            )
            active_offers = (
                db.query(Offer)
                .filter(
                    Offer.business_id == biz.id,
                    Offer.status == OfferStatus.ACTIVE,
                )
                .count()
            )

            biz_rev_count = biz.review_count if biz.review_count is not None else 0
            biz_avg_rating = (
                float(biz.average_rating) if biz.average_rating is not None else None
            )

            total_profile_views += p_views
            total_direction_requests += d_reqs
            total_calls += c_clicks
            total_reviews += biz_rev_count
            total_redemptions += b_redemptions

            if biz_avg_rating is not None and biz_rev_count > 0:
                weighted_rating_sum += biz_avg_rating * biz_rev_count
                total_rated_reviews += biz_rev_count

            card = BusinessSummaryCard(
                id=biz.id,
                name=biz.name,
                status=str(
                    biz.status.value if hasattr(biz.status, "value") else biz.status
                ),
                verification_status=str(
                    biz.verification_status.value
                    if hasattr(biz.verification_status, "value")
                    else biz.verification_status
                ),
                average_rating=biz_avg_rating,
                review_count=biz_rev_count,
                profile_views=p_views,
                direction_requests=d_reqs,
                calls=c_clicks,
                offer_redemptions=b_redemptions,
                active_offers_count=active_offers,
            )
            business_cards.append(card)

        overall_avg_rating = (
            round(weighted_rating_sum / total_rated_reviews, 2)
            if total_rated_reviews > 0
            else None
        )

        unread_notifs = (
            db.query(Notification)
            .filter(
                Notification.user_id == owner_id,
                Notification.is_read.is_(False),
            )
            .count()
        )

        return OwnerDashboardResponse(
            owner_id=owner_id,
            total_businesses=len(businesses),
            total_profile_views=total_profile_views,
            total_direction_requests=total_direction_requests,
            total_calls=total_calls,
            total_reviews=total_reviews,
            average_rating=overall_avg_rating,
            total_offer_redemptions=total_redemptions,
            unread_notifications_count=unread_notifs,
            businesses=business_cards,
        )
