"""Categories, business categories and verification audit fields

Revision ID: 002
Revises: 001
Create Date: 2026-10-08 23:55:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create categories table
    op.create_table(
        "categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, index=True),
        sa.Column("slug", sa.String(100), nullable=False, unique=True, index=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("icon", sa.String(100), nullable=True),
        sa.Column(
            "parent_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("categories.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default="true", index=True
        ),
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
    )

    # Create business_categories association table
    op.create_table(
        "business_categories",
        sa.Column(
            "business_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("businesses.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "category_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("categories.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )

    # Add indexes for business_categories
    op.create_index(
        "idx_business_categories_business_id", "business_categories", ["business_id"]
    )
    op.create_index(
        "idx_business_categories_category_id", "business_categories", ["category_id"]
    )

    # Add verification audit columns to businesses table
    op.add_column(
        "businesses", sa.Column("verification_notes", sa.Text(), nullable=True)
    )
    op.add_column("businesses", sa.Column("rejection_reason", sa.Text(), nullable=True))


def downgrade() -> None:
    # Drop columns from businesses
    op.drop_column("businesses", "rejection_reason")
    op.drop_column("businesses", "verification_notes")

    # Drop indexes and tables
    op.drop_index(
        "idx_business_categories_category_id", table_name="business_categories"
    )
    op.drop_index(
        "idx_business_categories_business_id", table_name="business_categories"
    )
    op.drop_table("business_categories")
    op.drop_table("categories")
