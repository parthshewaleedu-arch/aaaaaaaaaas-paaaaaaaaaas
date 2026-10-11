"""Offers and offer redemptions tables

Revision ID: 006
Revises: 005
Create Date: 2026-10-09 23:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Create Enums for Offers and Redemptions
    offer_discount_type = postgresql.ENUM(
        "PERCENTAGE",
        "FIXED_AMOUNT",
        "SERVICE_DISCOUNT",
        name="offer_discount_type",
    )
    offer_discount_type.create(op.get_bind(), checkfirst=True)

    offer_status = postgresql.ENUM(
        "DRAFT",
        "ACTIVE",
        "PAUSED",
        "EXPIRED",
        "CANCELLED",
        name="offer_status",
    )
    offer_status.create(op.get_bind(), checkfirst=True)

    offer_redemption_status = postgresql.ENUM(
        "PENDING",
        "COMPLETED",
        "CANCELLED",
        "EXPIRED",
        name="offer_redemption_status",
    )
    offer_redemption_status.create(op.get_bind(), checkfirst=True)

    # 2. Create offers table
    op.create_table(
        "offers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "business_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("businesses.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "discount_type",
            postgresql.ENUM(
                "PERCENTAGE",
                "FIXED_AMOUNT",
                "SERVICE_DISCOUNT",
                name="offer_discount_type",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("discount_value", sa.Numeric(10, 2), nullable=False),
        sa.Column("terms_conditions", sa.Text(), nullable=True),
        sa.Column("valid_from", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "valid_until", sa.DateTime(timezone=True), nullable=False, index=True
        ),
        sa.Column("max_redemptions", sa.Integer(), nullable=True),
        sa.Column("redemption_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "status",
            postgresql.ENUM(
                "DRAFT",
                "ACTIVE",
                "PAUSED",
                "EXPIRED",
                "CANCELLED",
                name="offer_status",
                create_type=False,
            ),
            nullable=False,
            server_default="DRAFT",
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
        sa.CheckConstraint("discount_value > 0", name="ck_offers_discount_value"),
        sa.CheckConstraint(
            "max_redemptions IS NULL OR max_redemptions > 0",
            name="ck_offers_redemptions",
        ),
        sa.CheckConstraint("redemption_count >= 0", name="ck_offers_redemption_count"),
        sa.CheckConstraint("valid_until > valid_from", name="ck_offers_dates"),
    )

    op.create_index("ix_offers_business_id", "offers", ["business_id"])
    op.create_index("ix_offers_status", "offers", ["status"])
    op.create_index("ix_offers_valid_until", "offers", ["valid_until"])

    # 3. Create offer_redemptions table
    op.create_table(
        "offer_redemptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "offer_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("offers.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "redeemed_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
            index=True,
        ),
        sa.Column(
            "status",
            postgresql.ENUM(
                "PENDING",
                "COMPLETED",
                "CANCELLED",
                "EXPIRED",
                name="offer_redemption_status",
                create_type=False,
            ),
            nullable=False,
            server_default="PENDING",
        ),
        sa.Column(
            "verification_code", sa.String(50), nullable=False, unique=True, index=True
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('PENDING', 'COMPLETED', 'CANCELLED', 'EXPIRED')",
            name="ck_offer_redemptions_status",
        ),
    )

    op.create_index("ix_offer_redemptions_offer_id", "offer_redemptions", ["offer_id"])
    op.create_index("ix_offer_redemptions_user_id", "offer_redemptions", ["user_id"])
    op.create_index(
        "ix_offer_redemptions_redeemed_at", "offer_redemptions", ["redeemed_at"]
    )
    op.create_index(
        "ix_offer_redemptions_verification_code",
        "offer_redemptions",
        ["verification_code"],
        unique=True,
    )


def downgrade() -> None:
    # Drop tables
    op.drop_table("offer_redemptions")
    op.drop_table("offers")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS offer_redemption_status")
    op.execute("DROP TYPE IF EXISTS offer_status")
    op.execute("DROP TYPE IF EXISTS offer_discount_type")
