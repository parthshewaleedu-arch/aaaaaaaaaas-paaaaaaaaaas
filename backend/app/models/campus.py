"""Campus Model

Represents physical campuses with geographic locations.
"""

from sqlalchemy import (
    CheckConstraint,
    Column,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography

from app.models.base import BaseModel


class Campus(BaseModel):
    """Campus model.

    Represents a physical campus location with geographic boundaries.
    Uses PostGIS for geospatial queries.
    """

    __tablename__ = "campuses"

    # College relationship
    college_id = Column(
        UUID(as_uuid=True),
        ForeignKey("colleges.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Basic information
    name = Column(String(255), nullable=False)
    address = Column(Text, nullable=False)

    # Geographic coordinates
    latitude = Column(
        Numeric(precision=10, scale=8),
        nullable=False,
    )
    longitude = Column(
        Numeric(precision=11, scale=8),
        nullable=False,
    )

    # Discovery radius (in meters)
    radius_meters = Column(Integer, nullable=False, default=3000)

    # PostGIS geography point (auto-populated from lat/lng via trigger)
    location = Column(
        Geography(geometry_type="POINT", srid=4326),
        nullable=True,
    )

    # Relationships
    college = relationship("College", back_populates="campuses")
    students = relationship("Student", back_populates="campus")
    businesses = relationship("Business", back_populates="campus")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "latitude >= -90 AND latitude <= 90",
            name="ck_campuses_latitude",
        ),
        CheckConstraint(
            "longitude >= -180 AND longitude <= 180",
            name="ck_campuses_longitude",
        ),
        CheckConstraint(
            "radius_meters > 0",
            name="ck_campuses_radius",
        ),
    )

    def __repr__(self):
        return f"<Campus(id={self.id}, name={self.name})>"
