"""Business photos and favorites tables

Revision ID: 005
Revises: 004
Create Date: 2026-10-09 22:15:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Create Enums for Business Photos
    business_photo_uploader_type = postgresql.ENUM(
        "OWNER",
        "STUDENT",
        "ADMIN",
        name="business_photo_uploader_type",
    )
    business_photo_uploader_type.create(op.get_bind(), checkfirst=True)

    business_photo_status = postgresql.ENUM(
        "ACTIVE",
        "REMOVED",
        "PENDING_MODERATION",
        name="business_photo_status",
    )
    business_photo_status.create(op.get_bind(), checkfirst=True)

    # 2. Create business_photos table
    op.create_table(
        "business_photos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "business_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("businesses.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "uploaded_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("image_url", sa.Text(), nullable=False),
        sa.Column("caption", sa.String(255), nullable=True),
        sa.Column(
            "is_primary",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
        sa.Column(
            "uploader_type",
            sa.Enum(
                "OWNER",
                "STUDENT",
                "ADMIN",
                name="business_photo_uploader_type",
                create_type=False,
            ),
            nullable=False,
            server_default="OWNER",
        ),
        sa.Column(
            "status",
            sa.Enum(
                "ACTIVE",
                "REMOVED",
                "PENDING_MODERATION",
                name="business_photo_status",
                create_type=False,
            ),
            nullable=False,
            server_default="ACTIVE",
            index=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.CheckConstraint(
            "status IN ('ACTIVE', 'REMOVED', 'PENDING_MODERATION')",
            name="ck_business_photos_status",
        ),
        sa.CheckConstraint(
            "uploader_type IN ('OWNER', 'STUDENT', 'ADMIN')",
            name="ck_business_photos_uploader",
        ),
    )
    op.create_index(
        "ix_business_photos_business_id", "business_photos", ["business_id"]
    )
    op.create_index(
        "ix_business_photos_uploaded_by", "business_photos", ["uploaded_by"]
    )
    op.create_index(
        "ix_business_photos_is_primary",
        "business_photos",
        ["business_id", "is_primary"],
        postgresql_where=sa.text("is_primary = TRUE"),
    )

    # 3. Create favorites table
    op.create_table(
        "favorites",
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "business_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("businesses.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_index("ix_favorites_user_id", "favorites", ["user_id"])
    op.create_index("ix_favorites_business_id", "favorites", ["business_id"])


def downgrade() -> None:
    # Drop tables
    op.drop_table("favorites")
    op.drop_table("business_photos")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS business_photo_status")
    op.execute("DROP TYPE IF EXISTS business_photo_uploader_type")
