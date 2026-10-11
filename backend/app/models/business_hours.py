"""Business Hours Model

Operating hours schedule for businesses.
"""

from sqlalchemy import Boolean, CheckConstraint, Column, ForeignKey, Integer, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


DAY_NAMES = [
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
]


class BusinessHours(BaseModel):
    """Business operating hours model.

    Supports day-of-week schedule (0=Sunday to 6=Saturday),
    opening/closing times, and closed status.
    """

    __tablename__ = "business_hours"

    business_id = Column(
        UUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    day_of_week = Column(Integer, nullable=False)  # 0=Sunday, 1=Monday, ..., 6=Saturday
    open_time = Column(Time, nullable=True)
    close_time = Column(Time, nullable=True)
    is_closed = Column(Boolean, nullable=False, default=False)

    # Relationship
    business = relationship("Business", back_populates="hours")

    __table_args__ = (
        CheckConstraint("day_of_week BETWEEN 0 AND 6", name="ck_business_hours_day"),
        CheckConstraint(
            "is_closed = TRUE OR (open_time IS NOT NULL AND close_time IS NOT NULL)",
            name="ck_business_hours_times",
        ),
    )

    @property
    def day_name(self) -> str:
        """Return human-readable day name."""
        if 0 <= self.day_of_week < len(DAY_NAMES):
            return DAY_NAMES[self.day_of_week]
        return "Unknown"

    def __repr__(self):
        return f"<BusinessHours(business_id={self.business_id}, day={self.day_name}, closed={self.is_closed})>"
