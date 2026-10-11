"""Business reports and audit logs tables

Revision ID: 007
Revises: 006
Create Date: 2026-10-10 01:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Create Enums for Business Reports
    business_report_reason = postgresql.ENUM(
        "FAKE_LISTING",
        "INCORRECT_INFORMATION",
        "CLOSED_BUSINESS",
        "INCORRECT_PRICES",
        "FRAUD",
        "HARASSMENT",
        "OTHER",
        name="business_report_reason",
    )
    business_report_reason.create(op.get_bind(), checkfirst=True)

    business_report_status = postgresql.ENUM(
        "PENDING",
        "UNDER_REVIEW",
        "RESOLVED",
        "DISMISSED",
        name="business_report_status",
    )
    business_report_status.create(op.get_bind(), checkfirst=True)

    # 2. Create business_reports table
    op.create_table(
        "business_reports",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "business_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("businesses.id", ondelete="CASCADE"),
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
                "FAKE_LISTING",
                "INCORRECT_INFORMATION",
                "CLOSED_BUSINESS",
                "INCORRECT_PRICES",
                "FRAUD",
                "HARASSMENT",
                "OTHER",
                name="business_report_reason",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "PENDING",
                "UNDER_REVIEW",
                "RESOLVED",
                "DISMISSED",
                name="business_report_status",
                create_type=False,
            ),
            nullable=False,
            server_default="PENDING",
            index=True,
        ),
        sa.Column(
            "resolved_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
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
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "reason IN ('FAKE_LISTING', 'INCORRECT_INFORMATION', 'CLOSED_BUSINESS', "
            "'INCORRECT_PRICES', 'FRAUD', 'HARASSMENT', 'OTHER')",
            name="ck_business_reports_reason",
        ),
        sa.CheckConstraint(
            "status IN ('PENDING', 'UNDER_REVIEW', 'RESOLVED', 'DISMISSED')",
            name="ck_business_reports_status",
        ),
    )

    op.create_index(
        "ix_business_reports_business_id", "business_reports", ["business_id"]
    )
    op.create_index(
        "ix_business_reports_reported_by", "business_reports", ["reported_by"]
    )
    op.create_index("ix_business_reports_status", "business_reports", ["status"])

    # 3. Create audit_logs table
    op.create_table(
        "audit_logs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "admin_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("action", sa.String(length=100), nullable=False, index=True),
        sa.Column("entity_type", sa.String(length=50), nullable=False, index=True),
        sa.Column(
            "entity_id", postgresql.UUID(as_uuid=True), nullable=False, index=True
        ),
        sa.Column("old_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("new_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_index("ix_audit_logs_admin_id", "audit_logs", ["admin_id"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])
    op.create_index("ix_audit_logs_entity_type", "audit_logs", ["entity_type"])
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])


def downgrade() -> None:
    # Drop tables
    op.drop_table("audit_logs")
    op.drop_table("business_reports")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS business_report_status")
    op.execute("DROP TYPE IF EXISTS business_report_reason")
