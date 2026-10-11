"""Base Model

Base class with common fields for all models.
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr

from app.core.database import Base


class BaseModel(Base):
    """Abstract base model with common fields.

    All models inherit from this to get:
    - UUID primary key
    - created_at timestamp
    - updated_at timestamp (auto-updated)
    """

    __abstract__ = True

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    @declared_attr
    def __tablename__(cls) -> str:
        """Generate table name from class name.

        Converts CamelCase to snake_case plural.
        Example: BusinessHour -> business_hours
        """
        import re

        name = cls.__name__
        # Insert underscore before capital letters
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        # Insert underscore before capital letters in acronyms
        name = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
        # Make plural (simple pluralization)
        if not name.endswith("s"):
            name += "s"
        return name

    def __repr__(self):
        """String representation of model."""
        return f"<{self.__class__.__name__}(id={self.id})>"
