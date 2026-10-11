"""Reviews, ratings, dimensions, responses and reports tables

Revision ID: 004
Revises: 003
Create Date: 2026-10-09 01:10:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Create rating_dimensions table
    op.create_table(
        "rating_dimensions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "category_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("categories.id", ondelete="CASCADE"),
            nullable=True,
            index=True,
        ),
        sa.Column("name", sa.String(100), nullable=False, index=True),
        sa.Column("slug", sa.String(100), nullable=False, index=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
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
        sa.UniqueConstraint("category_id", "slug", name="uq_rating_dimensions"),
    )
    op.create_index(
        "ix_rating_dimensions_category_id", "rating_dimensions", ["category_id"]
    )

    # 2. Create Enums for Reviews and Moderation
    review_verification_level = postgresql.ENUM(
        "UNVERIFIED",
        "VERIFIED_STUDENT",
        "VERIFIED_VISIT",
        "VERIFIED_TRANSACTION",
        name="review_verification_level",
    )
    review_verification_level.create(op.get_bind(), checkfirst=True)

    review_status = postgresql.ENUM(
        "ACTIVE",
        "REMOVED",
        "PENDING_MODERATION",
        name="review_status",
    )
    review_status.create(op.get_bind(), checkfirst=True)

    review_report_reason = postgresql.ENUM(
        "SPAM",
        "FAKE_REVIEW",
        "HARASSMENT",
        "PERSONAL_INFORMATION",
        "ABUSE",
        "IRRELEVANT",
        "EXTORTION",
        "OTHER",
        name="review_report_reason",
    )
    review_report_reason.create(op.get_bind(), checkfirst=True)

    review_report_status = postgresql.ENUM(
        "PENDING",
        "UNDER_REVIEW",
        "RESOLVED",
        "DISMISSED",
        name="review_report_status",
    )
    review_report_status.create(op.get_bind(), checkfirst=True)

    # 3. Create reviews table
    op.create_table(
        "reviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "business_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("businesses.id", ondelete="CASCADE"),
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
        sa.Column("overall_rating", sa.Integer(), nullable=False),
        sa.Column("review_text", sa.Text(), nullable=True),
        sa.Column(
            "verification_level",
            sa.Enum(
                "UNVERIFIED",
                "VERIFIED_STUDENT",
                "VERIFIED_VISIT",
                "VERIFIED_TRANSACTION",
                name="review_verification_level",
                create_type=False,
            ),
            nullable=False,
            server_default="UNVERIFIED",
        ),
        sa.Column(
            "status",
            sa.Enum(
                "ACTIVE",
                "REMOVED",
                "PENDING_MODERATION",
                name="review_status",
                create_type=False,
            ),
            nullable=False,
            server_default="ACTIVE",
            index=True,
        ),
        sa.Column("helpful_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True, index=True),
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
            "overall_rating >= 1 AND overall_rating <= 5", name="ck_reviews_rating"
        ),
        sa.CheckConstraint("helpful_count >= 0", name="ck_reviews_helpful_count"),
    )
    op.create_index("ix_reviews_business_id", "reviews", ["business_id"])
    op.create_index("ix_reviews_user_id", "reviews", ["user_id"])
    op.create_index("ix_reviews_status", "reviews", ["status"])
    op.create_index("ix_reviews_deleted_at", "reviews", ["deleted_at"])

    # 4. Create review_ratings table
    op.create_table(
        "review_ratings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "review_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("reviews.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "dimension_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("rating_dimensions.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("rating", sa.Integer(), nullable=False),
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
            "rating >= 1 AND rating <= 5", name="ck_review_ratings_rating"
        ),
        sa.UniqueConstraint("review_id", "dimension_id", name="uq_review_ratings"),
    )
    op.create_index("ix_review_ratings_review_id", "review_ratings", ["review_id"])
    op.create_index(
        "ix_review_ratings_dimension_id", "review_ratings", ["dimension_id"]
    )

    # 5. Create review_photos table
    op.create_table(
        "review_photos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "review_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("reviews.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("image_url", sa.Text(), nullable=False),
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
    )
    op.create_index("ix_review_photos_review_id", "review_photos", ["review_id"])

    # 6. Create review_responses table
    op.create_table(
        "review_responses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "review_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("reviews.id", ondelete="CASCADE"),
            unique=True,
            nullable=False,
            index=True,
        ),
        sa.Column(
            "owner_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("response_text", sa.Text(), nullable=False),
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
    )
    op.create_index("ix_review_responses_review_id", "review_responses", ["review_id"])
    op.create_index("ix_review_responses_owner_id", "review_responses", ["owner_id"])

    # 7. Create review_reports table
    op.create_table(
        "review_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "review_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("reviews.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "reported_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "reason",
            sa.Enum(
                "SPAM",
                "FAKE_REVIEW",
                "HARASSMENT",
                "PERSONAL_INFORMATION",
                "ABUSE",
                "IRRELEVANT",
                "EXTORTION",
                "OTHER",
                name="review_report_reason",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "PENDING",
                "UNDER_REVIEW",
                "RESOLVED",
                "DISMISSED",
                name="review_report_status",
                create_type=False,
            ),
            nullable=False,
            server_default="PENDING",
            index=True,
        ),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "resolved_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("resolution_notes", sa.Text(), nullable=True),
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
    )
    op.create_index("ix_review_reports_review_id", "review_reports", ["review_id"])
    op.create_index("ix_review_reports_reported_by", "review_reports", ["reported_by"])
    op.create_index("ix_review_reports_status", "review_reports", ["status"])


def downgrade() -> None:
    # Drop tables
    op.drop_table("review_reports")
    op.drop_table("review_responses")
    op.drop_table("review_photos")
    op.drop_table("review_ratings")
    op.drop_table("reviews")
    op.drop_table("rating_dimensions")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS review_report_status")
    op.execute("DROP TYPE IF EXISTS review_report_reason")
    op.execute("DROP TYPE IF EXISTS review_status")
    op.execute("DROP TYPE IF EXISTS review_verification_level")
