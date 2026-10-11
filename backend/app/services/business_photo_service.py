"""Business Photo Service

Business logic for managing business photo gallery, uploads, primary cover selection, and deletions.
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.business import Business
from app.models.business_photo import (
    BusinessPhoto,
    BusinessPhotoStatus,
    BusinessPhotoUploaderType,
)
from app.models.user import User, UserRole
from app.schemas.business_photo import BusinessPhotoCreate


class BusinessPhotoService:
    """Service for business photo gallery management."""

    @classmethod
    def upload_photo(
        cls,
        business_id: UUID,
        user: User,
        photo_data: BusinessPhotoCreate,
        db: Session,
    ) -> BusinessPhoto:
        """Upload a photo for a business gallery.

        Args:
            business_id: Target business UUID.
            user: Authenticated user uploading the photo.
            photo_data: Upload payload.
            db: Database session.

        Returns:
            Created BusinessPhoto model.
        """
        business = db.query(Business).filter(Business.id == business_id).first()
        if not business:
            raise ValueError("Business not found")

        # Determine uploader type
        is_owner = business.owner_id == user.id
        is_admin = user.role == UserRole.ADMIN

        if is_admin:
            uploader_type = BusinessPhotoUploaderType.ADMIN
        elif is_owner:
            uploader_type = BusinessPhotoUploaderType.OWNER
        else:
            uploader_type = BusinessPhotoUploaderType.STUDENT

        # Only owner or admin can set photo as primary cover photo
        is_primary = False
        if photo_data.is_primary:
            if not (is_owner or is_admin):
                raise PermissionError(
                    "Only the business owner or admin can set a primary cover photo"
                )
            is_primary = True

        # If marking as primary, demote any currently active primary photo for this business
        if is_primary:
            db.query(BusinessPhoto).filter(
                BusinessPhoto.business_id == business_id,
                BusinessPhoto.is_primary.is_(True),
            ).update({"is_primary": False}, synchronize_session=False)

        photo = BusinessPhoto(
            id=uuid4(),
            business_id=business_id,
            uploaded_by=user.id,
            image_url=photo_data.image_url.strip(),
            caption=photo_data.caption.strip() if photo_data.caption else None,
            is_primary=is_primary,
            uploader_type=uploader_type,
            status=BusinessPhotoStatus.ACTIVE,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(photo)
        db.commit()
        db.refresh(photo)
        return photo

    @classmethod
    def list_photos(
        cls,
        business_id: UUID,
        db: Session,
        status: Optional[str] = "ACTIVE",
        limit: int = 50,
    ) -> tuple[list[BusinessPhoto], int]:
        """List photos for a business gallery ordered by primary first, then newest.

        Args:
            business_id: Target business UUID.
            db: Database session.
            status: Moderation status filter (default ACTIVE).
            limit: Maximum photos to return.

        Returns:
            Tuple of (photo_list, total_count).
        """
        query = db.query(BusinessPhoto).filter(BusinessPhoto.business_id == business_id)
        if status:
            query = query.filter(BusinessPhoto.status == status)

        total = query.count()
        photos = (
            query.order_by(
                desc(BusinessPhoto.is_primary),
                desc(BusinessPhoto.created_at),
            )
            .limit(limit)
            .all()
        )
        return photos, total

    @classmethod
    def get_photo_by_id(cls, photo_id: UUID, db: Session) -> Optional[BusinessPhoto]:
        """Retrieve a specific business photo by ID."""
        return db.query(BusinessPhoto).filter(BusinessPhoto.id == photo_id).first()

    @classmethod
    def set_primary_photo(
        cls,
        business_id: UUID,
        photo_id: UUID,
        user: User,
        db: Session,
    ) -> BusinessPhoto:
        """Designate a photo as the primary cover photo for the business.

        Args:
            business_id: Target business UUID.
            photo_id: Photo UUID to designate as primary.
            user: Requesting user (must be owner or admin).
            db: Database session.

        Returns:
            Updated BusinessPhoto model.
        """
        business = db.query(Business).filter(Business.id == business_id).first()
        if not business:
            raise ValueError("Business not found")

        is_owner = business.owner_id == user.id
        is_admin = user.role == UserRole.ADMIN
        if not (is_owner or is_admin):
            raise PermissionError(
                "Only the business owner or admin can set the primary photo"
            )

        photo = (
            db.query(BusinessPhoto)
            .filter(
                BusinessPhoto.id == photo_id,
                BusinessPhoto.business_id == business_id,
                BusinessPhoto.status == BusinessPhotoStatus.ACTIVE,
            )
            .first()
        )
        if not photo:
            raise ValueError("Photo not found")

        # Unset all other primary photos for this business
        db.query(BusinessPhoto).filter(
            BusinessPhoto.business_id == business_id,
            BusinessPhoto.is_primary.is_(True),
        ).update({"is_primary": False}, synchronize_session=False)

        photo.is_primary = True
        photo.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(photo)
        return photo

    @classmethod
    def delete_photo(
        cls,
        business_id: UUID,
        photo_id: UUID,
        user: User,
        db: Session,
    ) -> bool:
        """Remove a photo from the gallery.

        Allowed for photo uploader, business owner, or platform admin.

        Args:
            business_id: Target business UUID.
            photo_id: Photo UUID to delete.
            user: Requesting user.
            db: Database session.

        Returns:
            True if deleted, False if not found.
        """
        photo = (
            db.query(BusinessPhoto)
            .filter(
                BusinessPhoto.id == photo_id,
                BusinessPhoto.business_id == business_id,
                BusinessPhoto.status != BusinessPhotoStatus.REMOVED,
            )
            .first()
        )
        if not photo:
            return False

        business = db.query(Business).filter(Business.id == business_id).first()
        is_uploader = photo.uploaded_by == user.id
        is_owner = business and business.owner_id == user.id
        is_admin = user.role == UserRole.ADMIN

        if not (is_uploader or is_owner or is_admin):
            raise PermissionError("You do not have permission to delete this photo")

        photo.status = BusinessPhotoStatus.REMOVED
        photo.is_primary = False
        photo.updated_at = datetime.now(timezone.utc)
        db.commit()
        return True
