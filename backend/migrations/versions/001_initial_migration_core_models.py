"""Initial migration - core models

Revision ID: 001
Revises:
Create Date: 2026-09-20 02:36:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import geoalchemy2

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types
    op.execute("CREATE TYPE user_role AS ENUM ('STUDENT', 'OWNER', 'ADMIN', 'COLLEGE_ADMIN')")
    op.execute("CREATE TYPE user_status AS ENUM ('ACTIVE', 'SUSPENDED', 'DELETED', 'PENDING')")
    op.execute("CREATE TYPE college_status AS ENUM ('ACTIVE', 'INACTIVE', 'PENDING')")
    op.execute("CREATE TYPE verification_status AS ENUM ('UNVERIFIED', 'PENDING', 'VERIFIED', 'SUSPENDED', 'EXPIRED')")
    op.execute("CREATE TYPE business_status AS ENUM ('PENDING', 'ACTIVE', 'SUSPENDED', 'REJECTED', 'REMOVED')")
    op.execute("CREATE TYPE business_verification_status AS ENUM ('UNVERIFIED', 'PENDING', 'VERIFIED', 'EXPIRED')")
    op.execute("CREATE TYPE price_level AS ENUM ('₹', '₹₹', '₹₹₹', '₹₹₹₹')")

    # Enable PostGIS extension
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('phone', sa.String(20), nullable=True, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('role', postgresql.ENUM('STUDENT', 'OWNER', 'ADMIN', 'COLLEGE_ADMIN', name='user_role', create_type=False), nullable=False, index=True),
        sa.Column('status', postgresql.ENUM('ACTIVE', 'SUSPENDED', 'DELETED', 'PENDING', name='user_status', create_type=False), nullable=False, server_default='ACTIVE', index=True),
        sa.Column('is_email_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_phone_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True, index=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    # Create colleges table
    op.create_table(
        'colleges',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('short_name', sa.String(100), nullable=True),
        sa.Column('email_domain', sa.String(100), nullable=False, unique=True, index=True),
        sa.Column('website_url', sa.Text(), nullable=True),
        sa.Column('logo_url', sa.Text(), nullable=True),
        sa.Column('status', postgresql.ENUM('ACTIVE', 'INACTIVE', 'PENDING', name='college_status', create_type=False), nullable=False, server_default='ACTIVE', index=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    # Create campuses table
    op.create_table(
        'campuses',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('college_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('colleges.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('address', sa.Text(), nullable=False),
        sa.Column('latitude', sa.Numeric(precision=10, scale=8), nullable=False),
        sa.Column('longitude', sa.Numeric(precision=11, scale=8), nullable=False),
        sa.Column('radius_meters', sa.Integer(), nullable=False, server_default='3000'),
        sa.Column('location', geoalchemy2.Geography(geometry_type='POINT', srid=4326), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint('latitude >= -90 AND latitude <= 90', name='ck_campuses_latitude'),
        sa.CheckConstraint('longitude >= -180 AND longitude <= 180', name='ck_campuses_longitude'),
        sa.CheckConstraint('radius_meters > 0', name='ck_campuses_radius'),
    )

    # Create students table
    op.create_table(
        'students',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True, index=True),
        sa.Column('college_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('colleges.id', ondelete='RESTRICT'), nullable=False, index=True),
        sa.Column('campus_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('campuses.id', ondelete='SET NULL'), nullable=True, index=True),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('profile_photo_url', sa.Text(), nullable=True),
        sa.Column('student_id', sa.String(100), nullable=True),
        sa.Column('department', sa.String(100), nullable=True),
        sa.Column('year', sa.Integer(), nullable=True),
        sa.Column('verification_status', postgresql.ENUM('UNVERIFIED', 'PENDING', 'VERIFIED', 'SUSPENDED', 'EXPIRED', name='verification_status', create_type=False), nullable=False, server_default='UNVERIFIED', index=True),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint('year IS NULL OR (year >= 1 AND year <= 7)', name='ck_students_year'),
    )

    # Create businesses table
    op.create_table(
        'businesses',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False, index=True),
        sa.Column('campus_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('campuses.id', ondelete='RESTRICT'), nullable=False, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('phone', sa.String(20), nullable=False),
        sa.Column('whatsapp', sa.String(20), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('website_url', sa.Text(), nullable=True),
        sa.Column('address', sa.Text(), nullable=False),
        sa.Column('latitude', sa.Numeric(precision=10, scale=8), nullable=False),
        sa.Column('longitude', sa.Numeric(precision=11, scale=8), nullable=False),
        sa.Column('location', geoalchemy2.Geography(geometry_type='POINT', srid=4326), nullable=True),
        sa.Column('status', postgresql.ENUM('PENDING', 'ACTIVE', 'SUSPENDED', 'REJECTED', 'REMOVED', name='business_status', create_type=False), nullable=False, server_default='PENDING', index=True),
        sa.Column('verification_status', postgresql.ENUM('UNVERIFIED', 'PENDING', 'VERIFIED', 'EXPIRED', name='business_verification_status', create_type=False), nullable=False, server_default='UNVERIFIED', index=True),
        sa.Column('price_level', postgresql.ENUM('₹', '₹₹', '₹₹₹', '₹₹₹₹', name='price_level', create_type=False), nullable=True),
        sa.Column('student_discount', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('student_discount_description', sa.Text(), nullable=True),
        sa.Column('average_rating', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('review_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True, index=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint('latitude >= -90 AND latitude <= 90', name='ck_businesses_latitude'),
        sa.CheckConstraint('longitude >= -180 AND longitude <= 180', name='ck_businesses_longitude'),
        sa.CheckConstraint('average_rating IS NULL OR (average_rating >= 1 AND average_rating <= 5)', name='ck_businesses_rating'),
        sa.CheckConstraint('review_count >= 0', name='ck_businesses_review_count'),
    )

    # Create indexes for geography columns
    op.execute("CREATE INDEX idx_campuses_location ON campuses USING GIST (location)")
    op.execute("CREATE INDEX idx_businesses_location ON businesses USING GIST (location)")

    # Create trigger to auto-populate location from lat/lng for campuses
    op.execute("""
        CREATE OR REPLACE FUNCTION update_campus_location()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.location = ST_SetSRID(ST_MakePoint(NEW.longitude, NEW.latitude), 4326)::geography;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE TRIGGER trg_update_campus_location
        BEFORE INSERT OR UPDATE OF latitude, longitude ON campuses
        FOR EACH ROW
        EXECUTE FUNCTION update_campus_location();
    """)

    # Create trigger to auto-populate location from lat/lng for businesses
    op.execute("""
        CREATE OR REPLACE FUNCTION update_business_location()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.location = ST_SetSRID(ST_MakePoint(NEW.longitude, NEW.latitude), 4326)::geography;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE TRIGGER trg_update_business_location
        BEFORE INSERT OR UPDATE OF latitude, longitude ON businesses
        FOR EACH ROW
        EXECUTE FUNCTION update_business_location();
    """)


def downgrade() -> None:
    # Drop triggers
    op.execute("DROP TRIGGER IF EXISTS trg_update_business_location ON businesses")
    op.execute("DROP TRIGGER IF EXISTS trg_update_campus_location ON campuses")
    op.execute("DROP FUNCTION IF EXISTS update_business_location()")
    op.execute("DROP FUNCTION IF EXISTS update_campus_location()")

    # Drop tables
    op.drop_table('businesses')
    op.drop_table('students')
    op.drop_table('campuses')
    op.drop_table('colleges')
    op.drop_table('users')

    # Drop enum types
    op.execute("DROP TYPE IF EXISTS price_level")
    op.execute("DROP TYPE IF EXISTS business_verification_status")
    op.execute("DROP TYPE IF EXISTS business_status")
    op.execute("DROP TYPE IF EXISTS verification_status")
    op.execute("DROP TYPE IF EXISTS college_status")
    op.execute("DROP TYPE IF EXISTS user_status")
    op.execute("DROP TYPE IF EXISTS user_role")
