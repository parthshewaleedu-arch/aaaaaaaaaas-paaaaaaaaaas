"""Audit Log Model.

Captures immutable audit trail records for high-impact administrator and moderation actions.
"""

from sqlalchemy import Column, ForeignKey, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class AuditLog(BaseModel):
    """Audit log tracking administrative events and moderation actions."""

    __tablename__ = "audit_logs"

    admin_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    action = Column(String(100), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    old_data = Column(JSON, nullable=True)
    new_data = Column(JSON, nullable=True)
    reason = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)

    # Relationships
    admin = relationship("User", foreign_keys=[admin_id])

    def __repr__(self):
        return (
            f"<AuditLog(id={self.id}, admin_id={self.admin_id}, action={self.action}, "
            f"entity={self.entity_type}:{self.entity_id})>"
        )
