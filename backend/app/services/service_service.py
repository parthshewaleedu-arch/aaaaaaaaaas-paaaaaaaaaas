"""Service Service

Business logic for managing business services and tracking price history.
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.models.business import Business
from app.models.service import Service
from app.models.service_price_history import ServicePriceHistory
from app.schemas.service import ServiceCreate, ServiceUpdate


class ServiceService:
    """Service for managing business offerings and price transparency history."""

    @staticmethod
    def calculate_days_since_update(dt: Optional[datetime]) -> Optional[int]:
        """Calculate the number of days elapsed since the given timestamp.

        Args:
            dt: The timestamp to measure from.

        Returns:
            Number of full days elapsed, or None if timestamp is None.
        """
        if not dt:
            return None
        now = datetime.now(timezone.utc)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        delta = now - dt
        return max(0, delta.days)

    @classmethod
    def create_service(
        cls,
        business_id: UUID,
        service_data: ServiceCreate,
        db: Session,
        changed_by: Optional[UUID] = None,
    ) -> Service:
        """Create a new service offering and record its initial price in history.

        Args:
            business_id: Business UUID.
            service_data: Service creation payload.
            db: Database session.
            changed_by: User UUID who created this service (owner).

        Returns:
            Created Service instance.
        """
        business = db.query(Business).filter(Business.id == business_id).first()
        if not business:
            raise ValueError("Business not found")

        now = datetime.now(timezone.utc)
        service = Service(
            id=uuid4(),
            business_id=business_id,
            name=service_data.name.strip(),
            description=service_data.description.strip()
            if service_data.description
            else None,
            price=service_data.price,
            currency=service_data.currency.upper(),
            unit=service_data.unit.strip() if service_data.unit else None,
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        db.add(service)
        db.flush()

        # Log initial price history entry
        price_history = ServicePriceHistory(
            id=uuid4(),
            service_id=service.id,
            price=service_data.price,
            currency=service_data.currency.upper(),
            effective_from=now,
            effective_to=None,
            changed_by=changed_by,
        )
        db.add(price_history)

        db.commit()
        db.refresh(service)
        return service

    @classmethod
    def update_service(
        cls,
        service_id: UUID,
        update_data: ServiceUpdate,
        db: Session,
        changed_by: Optional[UUID] = None,
    ) -> Optional[Service]:
        """Update an existing service offering and track price changes.

        If the price is updated, closes the previous price history interval
        and inserts a new active history record.

        Args:
            service_id: Service UUID.
            update_data: Fields to update.
            db: Database session.
            changed_by: User UUID who performed the update.

        Returns:
            Updated Service instance, or None if not found.
        """
        service = db.query(Service).filter(Service.id == service_id).first()
        if not service:
            return None

        now = datetime.now(timezone.utc)
        data = update_data.model_dump(exclude_unset=True)

        # Price update handling
        if "price" in data and data["price"] is not None:
            new_price = round(float(data["price"]), 2)
            old_price = round(float(service.price), 2)

            if new_price != old_price:
                # Close out current active price history record
                current_active = (
                    db.query(ServicePriceHistory)
                    .filter(
                        ServicePriceHistory.service_id == service.id,
                        ServicePriceHistory.effective_to.is_(None),
                    )
                    .order_by(ServicePriceHistory.effective_from.desc())
                    .first()
                )
                if current_active:
                    current_active.effective_to = now

                # Add new price record
                currency = (data.get("currency") or service.currency).upper()
                new_history = ServicePriceHistory(
                    id=uuid4(),
                    service_id=service.id,
                    price=new_price,
                    currency=currency,
                    effective_from=now,
                    effective_to=None,
                    changed_by=changed_by,
                )
                db.add(new_history)
                service.price = new_price

        # Update remaining fields
        if "name" in data and data["name"] is not None:
            service.name = data["name"].strip()
        if "description" in data:
            service.description = (
                data["description"].strip() if data["description"] else None
            )
        if "currency" in data and data["currency"] is not None:
            service.currency = data["currency"].upper()
        if "unit" in data:
            service.unit = data["unit"].strip() if data["unit"] else None
        if "is_active" in data and data["is_active"] is not None:
            service.is_active = data["is_active"]

        service.updated_at = now
        db.commit()
        db.refresh(service)
        return service

    @classmethod
    def get_service_by_id(cls, service_id: UUID, db: Session) -> Optional[Service]:
        """Retrieve a service by ID.

        Args:
            service_id: Service UUID.
            db: Database session.

        Returns:
            Service instance or None.
        """
        return db.query(Service).filter(Service.id == service_id).first()

    @classmethod
    def list_services(
        cls,
        business_id: UUID,
        db: Session,
        active_only: bool = True,
    ) -> list[Service]:
        """List services for a business.

        Args:
            business_id: Business UUID.
            db: Database session.
            active_only: Whether to return only active services.

        Returns:
            List of Service instances.
        """
        query = db.query(Service).filter(Service.business_id == business_id)
        if active_only:
            query = query.filter(Service.is_active.is_(True))
        return query.order_by(Service.name.asc()).all()

    @classmethod
    def delete_service(cls, service_id: UUID, db: Session) -> bool:
        """Permanently delete a service offering.

        Args:
            service_id: Service UUID.
            db: Database session.

        Returns:
            True if deleted, False if not found.
        """
        service = db.query(Service).filter(Service.id == service_id).first()
        if not service:
            return False

        db.delete(service)
        db.commit()
        return True

    @classmethod
    def get_price_history(
        cls,
        service_id: UUID,
        db: Session,
    ) -> list[ServicePriceHistory]:
        """Retrieve the price history audit trail for a service.

        Args:
            service_id: Service UUID.
            db: Database session.

        Returns:
            List of ServicePriceHistory records ordered by date descending.
        """
        return (
            db.query(ServicePriceHistory)
            .filter(ServicePriceHistory.service_id == service_id)
            .order_by(ServicePriceHistory.effective_from.desc())
            .all()
        )
