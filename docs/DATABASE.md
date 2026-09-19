# AAS PAAS - Database Schema

**Document Version:** 1.0  
**Last Updated:** 2026-09-19  
**Status:** Foundation - Pre-implementation schema specification

---

## Table of Contents

1. [Database Overview](#database-overview)
2. [Schema Design Principles](#schema-design-principles)
3. [Core Tables](#core-tables)
4. [Entity Relationship Diagram](#entity-relationship-diagram)
5. [Detailed Table Specifications](#detailed-table-specifications)
6. [Indexes and Constraints](#indexes-and-constraints)
7. [Enumerations](#enumerations)
8. [Geospatial Queries](#geospatial-queries)
9. [Migration Strategy](#migration-strategy)

---

## Database Overview

**Database System**: PostgreSQL 15+  
**Extensions**: PostGIS (for geospatial queries)  
**ORM**: SQLAlchemy 2.x  
**Migration Tool**: Alembic

### Key Statistics (Expected for Pilot)

- **Users**: ~600 (500 students + 100 owners)
- **Businesses**: ~200
- **Reviews**: ~300-500
- **Categories**: ~50
- **Offers**: ~50-100

### Database Naming Conventions

- **Tables**: Lowercase, plural nouns (e.g., `users`, `businesses`)
- **Columns**: Lowercase, snake_case (e.g., `created_at`, `email_verified`)
- **Foreign Keys**: `{referenced_table_singular}_id` (e.g., `user_id`, `business_id`)
- **Indexes**: `ix_{table}_{column(s)}` (e.g., `ix_users_email`)
- **Unique Constraints**: `uq_{table}_{column(s)}` (e.g., `uq_users_email`)
- **Check Constraints**: `ck_{table}_{constraint_name}` (e.g., `ck_reviews_rating_range`)

---

## Schema Design Principles

1. **UUID Primary Keys** - Use UUID instead of auto-incrementing integers for all primary keys
2. **Foreign Key Constraints** - Enforce referential integrity at database level
3. **Timestamps** - Every table includes `created_at` and `updated_at` (where applicable)
4. **Soft Deletion** - Use `deleted_at` for important records rather than hard deletes
5. **Enum Types** - Use PostgreSQL ENUM types or VARCHAR with CHECK constraints
6. **NOT NULL** - Explicitly define which columns can be NULL
7. **Indexes** - Index foreign keys, frequently queried columns, and geospatial data
8. **Audit Trail** - Admin actions logged in `audit_logs` table
9. **Normalization** - Third normal form (3NF) with denormalization only for performance
10. **Data Integrity** - CHECK constraints for value validation

---

## Core Tables

### Identity & Authentication (4 tables)
- `users` - Core user accounts
- `students` - Student-specific information
- `colleges` - College/university definitions
- `campuses` - Campus locations and boundaries

### Business Entities (7 tables)
- `businesses` - Business listings
- `categories` - Business categories (hierarchical)
- `business_categories` - Many-to-many: businesses ↔ categories
- `business_hours` - Operating hours
- `business_photos` - Business images
- `services` - Services offered by businesses
- `service_price_history` - Price change tracking

### Review System (6 tables)
- `rating_dimensions` - Category-specific rating dimensions
- `reviews` - Student reviews
- `review_ratings` - Dimensional ratings for reviews
- `review_photos` - Review images
- `review_responses` - Business owner responses
- `review_reports` - Reported reviews

### Interactions (4 tables)
- `favorites` - Student saved businesses
- `offers` - Business offers/discounts
- `offer_redemptions` - Offer usage tracking
- `business_reports` - Reported businesses

### System (3 tables)
- `notifications` - User notifications
- `audit_logs` - Admin action audit trail
- `transactions` - Future payment/booking transactions

**Total: 27 core tables** (37 including future extensions)

---

## Entity Relationship Diagram

```
┌──────────┐         ┌──────────┐
│  users   │◄────────│ students │
└────┬─────┘         └────┬─────┘
     │                    │
     │              ┌─────▼────────┐
     │              │   colleges   │
     │              └─────┬────────┘
     │                    │
     │              ┌─────▼────────┐
     │              │   campuses   │
     │              └──────────────┘
     │
     ├──────────────┐
     │              │
┌────▼────┐   ┌────▼──────────┐
│favorites│   │  businesses   │
└─────────┘   └────┬──────────┘
                   │
         ┌─────────┼─────────┬─────────┬──────────┐
         │         │         │         │          │
   ┌─────▼──┐ ┌───▼────┐ ┌──▼─────┐ ┌▼────────┐ │
   │services│ │business│ │business│ │business │ │
   │        │ │_hours  │ │_photos │ │_reports │ │
   └────────┘ └────────┘ └────────┘ └─────────┘ │
                                                  │
                   ┌──────────────────────────────┘
                   │
          ┌────────┼────────┐
          │        │        │
      ┌───▼────┐ ┌▼──────┐ │
      │reviews │ │offers │ │
      └───┬────┘ └───────┘ │
          │                │
  ┌───────┼────────┐       │
  │       │        │       │
┌─▼────┐ ┌▼──────┐ ┌▼────▼┐
│review│ │review │ │review│
│_ratings│_photos│ │_responses
└───────┘ └───────┘ └──────┘
```

---

## Detailed Table Specifications

### 1. users

Core user account table supporting all roles.

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    is_email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    is_phone_verified BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    last_login_at TIMESTAMP WITH TIME ZONE,
    deleted_at TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT ck_users_role CHECK (role IN ('STUDENT', 'OWNER', 'ADMIN', 'COLLEGE_ADMIN')),
    CONSTRAINT ck_users_status CHECK (status IN ('ACTIVE', 'SUSPENDED', 'DELETED', 'PENDING'))
);

CREATE INDEX ix_users_email ON users(email);
CREATE INDEX ix_users_role ON users(role);
CREATE INDEX ix_users_status ON users(status);
CREATE INDEX ix_users_deleted_at ON users(deleted_at) WHERE deleted_at IS NULL;
```

**Columns:**
- `id`: Unique user identifier (UUID)
- `email`: User email address (unique, required)
- `phone`: Phone number (unique, optional)
- `password_hash`: Hashed password (Argon2/bcrypt)
- `role`: User role (STUDENT, OWNER, ADMIN, COLLEGE_ADMIN)
- `status`: Account status
- `is_email_verified`: Email verification status
- `is_phone_verified`: Phone verification status
- `created_at`: Account creation timestamp
- `updated_at`: Last update timestamp
- `last_login_at`: Last successful login
- `deleted_at`: Soft deletion timestamp (NULL = active)

### 2. students

Student-specific profile information.

```sql
CREATE TABLE students (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    college_id UUID NOT NULL REFERENCES colleges(id),
    campus_id UUID REFERENCES campuses(id),
    full_name VARCHAR(255) NOT NULL,
    profile_photo_url TEXT,
    student_id VARCHAR(100),
    department VARCHAR(100),
    year INTEGER,
    verification_status VARCHAR(20) NOT NULL DEFAULT 'UNVERIFIED',
    verified_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    CONSTRAINT ck_students_verification CHECK (
        verification_status IN ('UNVERIFIED', 'PENDING', 'VERIFIED', 'SUSPENDED', 'EXPIRED')
    ),
    CONSTRAINT ck_students_year CHECK (year BETWEEN 1 AND 7)
);

CREATE INDEX ix_students_user_id ON students(user_id);
CREATE INDEX ix_students_college_id ON students(college_id);
CREATE INDEX ix_students_campus_id ON students(campus_id);
CREATE INDEX ix_students_verification_status ON students(verification_status);
```

**Columns:**
- `user_id`: Reference to users table (one-to-one)
- `college_id`: Reference to colleges table
- `campus_id`: Reference to campuses table (optional)
- `full_name`: Student's full name
- `profile_photo_url`: Profile photo URL in object storage
- `student_id`: College-assigned student ID (optional)
- `department`: Academic department
- `year`: Academic year (1-7)
- `verification_status`: College email verification status
- `verified_at`: Timestamp when verification completed

### 3. colleges

College/university definitions.

```sql
CREATE TABLE colleges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    short_name VARCHAR(100),
    email_domain VARCHAR(100) NOT NULL,
    website_url TEXT,
    logo_url TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    CONSTRAINT ck_colleges_status CHECK (status IN ('ACTIVE', 'INACTIVE', 'PENDING'))
);

CREATE UNIQUE INDEX uq_colleges_email_domain ON colleges(email_domain);
CREATE INDEX ix_colleges_status ON colleges(status);
```

**Columns:**
- `name`: Full college name (e.g., "MIT Academy of Engineering")
- `short_name`: Abbreviated name (e.g., "MIT AOE")
- `email_domain`: Allowed email domain for verification (e.g., "mitaoe.ac.in")
- `website_url`: College website
- `logo_url`: College logo URL
- `status`: College status

**Critical**: Email domains must be configurable in the database, NOT hardcoded.

### 4. campuses

Campus locations and geographic boundaries.

```sql
CREATE TABLE campuses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    college_id UUID NOT NULL REFERENCES colleges(id),
    name VARCHAR(255) NOT NULL,
    address TEXT NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    radius_meters INTEGER NOT NULL DEFAULT 3000,
    location GEOGRAPHY(POINT, 4326),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    CONSTRAINT ck_campuses_latitude CHECK (latitude BETWEEN -90 AND 90),
    CONSTRAINT ck_campuses_longitude CHECK (longitude BETWEEN -180 AND 180),
    CONSTRAINT ck_campuses_radius CHECK (radius_meters > 0)
);

CREATE INDEX ix_campuses_college_id ON campuses(college_id);
CREATE INDEX ix_campuses_location ON campuses USING GIST(location);
```

**Columns:**
- `college_id`: Reference to colleges table
- `name`: Campus name
- `address`: Full address
- `latitude`: Geographic latitude (-90 to 90)
- `longitude`: Geographic longitude (-180 to 180)
- `radius_meters`: Discovery radius around campus (default 3000m = 3km)
- `location`: PostGIS geography point for spatial queries

**PostGIS Note**: The `location` column is automatically populated from lat/lng using a trigger.

### 5. businesses

Business listings.

```sql
CREATE TABLE businesses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL REFERENCES users(id),
    campus_id UUID NOT NULL REFERENCES campuses(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    phone VARCHAR(20) NOT NULL,
    whatsapp VARCHAR(20),
    email VARCHAR(255),
    website_url TEXT,
    address TEXT NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    location GEOGRAPHY(POINT, 4326),
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    verification_status VARCHAR(20) NOT NULL DEFAULT 'UNVERIFIED',
    price_level VARCHAR(10),
    student_discount BOOLEAN NOT NULL DEFAULT FALSE,
    student_discount_description TEXT,
    average_rating DECIMAL(3, 2),
    review_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    verified_at TIMESTAMP WITH TIME ZONE,
    deleted_at TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT ck_businesses_status CHECK (
        status IN ('PENDING', 'ACTIVE', 'SUSPENDED', 'REJECTED', 'REMOVED')
    ),
    CONSTRAINT ck_businesses_verification CHECK (
        verification_status IN ('UNVERIFIED', 'PENDING', 'VERIFIED', 'EXPIRED')
    ),
    CONSTRAINT ck_businesses_price_level CHECK (
        price_level IN ('₹', '₹₹', '₹₹₹', '₹₹₹₹')
    ),
    CONSTRAINT ck_businesses_latitude CHECK (latitude BETWEEN -90 AND 90),
    CONSTRAINT ck_businesses_longitude CHECK (longitude BETWEEN -180 AND 180),
    CONSTRAINT ck_businesses_rating CHECK (
        average_rating IS NULL OR (average_rating >= 1 AND average_rating <= 5)
    ),
    CONSTRAINT ck_businesses_review_count CHECK (review_count >= 0)
);

CREATE INDEX ix_businesses_owner_id ON businesses(owner_id);
CREATE INDEX ix_businesses_campus_id ON businesses(campus_id);
CREATE INDEX ix_businesses_status ON businesses(status);
CREATE INDEX ix_businesses_verification_status ON businesses(verification_status);
CREATE INDEX ix_businesses_location ON businesses USING GIST(location);
CREATE INDEX ix_businesses_deleted_at ON businesses(deleted_at) WHERE deleted_at IS NULL;
```

**Columns:**
- `owner_id`: Reference to user who owns this business
- `campus_id`: Reference to associated campus
- `name`: Business name
- `description`: Business description
- `phone`: Primary contact phone
- `whatsapp`: WhatsApp number (optional)
- `email`: Business email
- `website_url`: Business website
- `address`: Full street address
- `latitude`, `longitude`: Geographic coordinates
- `location`: PostGIS geography point
- `status`: Business listing status
- `verification_status`: Admin verification status
- `price_level`: Price range indicator (₹ to ₹₹₹₹)
- `student_discount`: Whether student discount is available
- `student_discount_description`: Discount details
- `average_rating`: Cached average rating (source of truth: reviews)
- `review_count`: Cached review count (source of truth: reviews)
- `verified_at`: When admin verified the business
- `deleted_at`: Soft deletion timestamp

**Note**: `average_rating` and `review_count` are denormalized for performance. Reviews remain the source of truth.

### 6. categories

Business categories (supports hierarchical structure).

```sql
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    icon VARCHAR(50),
    parent_id UUID REFERENCES categories(id) ON DELETE SET NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    display_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_categories_parent_id ON categories(parent_id);
CREATE INDEX ix_categories_is_active ON categories(is_active);
CREATE INDEX ix_categories_slug ON categories(slug);
```

**Example Hierarchy:**
```
Food (parent_id: NULL)
├── Restaurant (parent_id: Food.id)
├── Cafe (parent_id: Food.id)
└── Mess (parent_id: Food.id)

Health (parent_id: NULL)
├── Medical (parent_id: Health.id)
└── Hospital (parent_id: Health.id)
```

### 7. business_categories

Many-to-many relationship between businesses and categories.

```sql
CREATE TABLE business_categories (
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    category_id UUID NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    PRIMARY KEY (business_id, category_id)
);

CREATE INDEX ix_business_categories_business_id ON business_categories(business_id);
CREATE INDEX ix_business_categories_category_id ON business_categories(category_id);
```

### 8. business_hours

Business operating hours.

```sql
CREATE TABLE business_hours (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    day_of_week INTEGER NOT NULL,
    open_time TIME,
    close_time TIME,
    is_closed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    CONSTRAINT ck_business_hours_day CHECK (day_of_week BETWEEN 0 AND 6),
    CONSTRAINT ck_business_hours_times CHECK (
        is_closed = TRUE OR (open_time IS NOT NULL AND close_time IS NOT NULL)
    ),
    CONSTRAINT uq_business_hours UNIQUE (business_id, day_of_week, open_time)
);

CREATE INDEX ix_business_hours_business_id ON business_hours(business_id);
```

**Columns:**
- `day_of_week`: 0=Sunday, 1=Monday, ..., 6=Saturday
- `open_time`: Opening time
- `close_time`: Closing time
- `is_closed`: TRUE if closed on this day

**Note**: Multiple periods per day supported via multiple rows with same day_of_week.

### 9. business_photos

Business images.

```sql
CREATE TABLE business_photos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    uploaded_by UUID NOT NULL REFERENCES users(id),
    image_url TEXT NOT NULL,
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    uploader_type VARCHAR(20) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    CONSTRAINT ck_business_photos_status CHECK (
        status IN ('ACTIVE', 'REMOVED', 'PENDING_MODERATION')
    ),
    CONSTRAINT ck_business_photos_uploader CHECK (
        uploader_type IN ('OWNER', 'STUDENT', 'ADMIN')
    )
);

CREATE INDEX ix_business_photos_business_id ON business_photos(business_id);
CREATE INDEX ix_business_photos_uploaded_by ON business_photos(uploaded_by);
CREATE INDEX ix_business_photos_is_primary ON business_photos(business_id, is_primary)
    WHERE is_primary = TRUE;
```

### 10. services

Services offered by businesses.

```sql
CREATE TABLE services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'INR',
    unit VARCHAR(50),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    CONSTRAINT ck_services_price CHECK (price >= 0)
);

CREATE INDEX ix_services_business_id ON services(business_id);
CREATE INDEX ix_services_is_active ON services(is_active);
```

### 11. service_price_history

Price change tracking for transparency.

```sql
CREATE TABLE service_price_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_id UUID NOT NULL REFERENCES services(id) ON DELETE CASCADE,
    price DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'INR',
    effective_from TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    effective_to TIMESTAMP WITH TIME ZONE,
    changed_by UUID REFERENCES users(id),
    
    CONSTRAINT ck_service_price_history_price CHECK (price >= 0)
);

CREATE INDEX ix_service_price_history_service_id ON service_price_history(service_id);
CREATE INDEX ix_service_price_history_effective_from ON service_price_history(effective_from);
```

**Purpose**: Track all price changes to display "Price updated X days ago" and maintain trust.

### 12. rating_dimensions

Category-specific rating dimensions (e.g., Food quality, Hygiene).

```sql
CREATE TABLE rating_dimensions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id UUID NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) NOT NULL,
    display_order INTEGER NOT NULL DEFAULT 0,
    
    CONSTRAINT uq_rating_dimensions UNIQUE (category_id, slug)
);

CREATE INDEX ix_rating_dimensions_category_id ON rating_dimensions(category_id);
```

**Example for "Mess" category:**
- Food Quality
- Hygiene
- Quantity
- Variety
- Value for Money
- Service

**Example for "Gym" category:**
- Equipment
- Cleanliness
- Crowd Level
- Trainers
- Price
- Operating Hours

### 13. reviews

Student reviews of businesses.

```sql
CREATE TABLE reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id),
    overall_rating INTEGER NOT NULL,
    review_text TEXT,
    verification_level VARCHAR(30) NOT NULL DEFAULT 'UNVERIFIED',
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    helpful_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT ck_reviews_rating CHECK (overall_rating BETWEEN 1 AND 5),
    CONSTRAINT ck_reviews_verification CHECK (
        verification_level IN ('UNVERIFIED', 'VERIFIED_STUDENT', 'VERIFIED_VISIT', 'VERIFIED_TRANSACTION')
    ),
    CONSTRAINT ck_reviews_status CHECK (
        status IN ('ACTIVE', 'REMOVED', 'PENDING_MODERATION')
    ),
    CONSTRAINT ck_reviews_helpful_count CHECK (helpful_count >= 0),
    CONSTRAINT uq_reviews_user_business UNIQUE (user_id, business_id, deleted_at)
);

CREATE INDEX ix_reviews_business_id ON reviews(business_id);
CREATE INDEX ix_reviews_user_id ON reviews(user_id);
CREATE INDEX ix_reviews_status ON reviews(status);
CREATE INDEX ix_reviews_created_at ON reviews(created_at DESC);
```

**Verification Levels:**
- `UNVERIFIED`: Basic user review
- `VERIFIED_STUDENT`: From verified college student
- `VERIFIED_VISIT`: Platform confirmed visit (future)
- `VERIFIED_TRANSACTION`: Confirmed transaction through platform (future)

**Constraint**: One active review per student per business (enforced via unique constraint with deleted_at).

### 14. review_ratings

Dimensional ratings for reviews.

```sql
CREATE TABLE review_ratings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    review_id UUID NOT NULL REFERENCES reviews(id) ON DELETE CASCADE,
    dimension_id UUID NOT NULL REFERENCES rating_dimensions(id),
    rating INTEGER NOT NULL,
    
    CONSTRAINT ck_review_ratings_rating CHECK (rating BETWEEN 1 AND 5),
    CONSTRAINT uq_review_ratings UNIQUE (review_id, dimension_id)
);

CREATE INDEX ix_review_ratings_review_id ON review_ratings(review_id);
CREATE INDEX ix_review_ratings_dimension_id ON review_ratings(dimension_id);
```

### 15. review_photos

Photos attached to reviews.

```sql
CREATE TABLE review_photos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    review_id UUID NOT NULL REFERENCES reviews(id) ON DELETE CASCADE,
    image_url TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_review_photos_review_id ON review_photos(review_id);
```

### 16. review_responses

Business owner responses to reviews.

```sql
CREATE TABLE review_responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    review_id UUID NOT NULL UNIQUE REFERENCES reviews(id) ON DELETE CASCADE,
    owner_id UUID NOT NULL REFERENCES users(id),
    response_text TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_review_responses_review_id ON review_responses(review_id);
CREATE INDEX ix_review_responses_owner_id ON review_responses(owner_id);
```

**Constraint**: One response per review (enforced via UNIQUE on review_id).

### 17. review_reports

Reports of problematic reviews.

```sql
CREATE TABLE review_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    review_id UUID NOT NULL REFERENCES reviews(id) ON DELETE CASCADE,
    reported_by UUID NOT NULL REFERENCES users(id),
    reason VARCHAR(50) NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolved_by UUID REFERENCES users(id),
    resolution_notes TEXT,
    
    CONSTRAINT ck_review_reports_reason CHECK (
        reason IN ('SPAM', 'FAKE_REVIEW', 'HARASSMENT', 'PERSONAL_INFORMATION', 
                   'ABUSE', 'IRRELEVANT', 'EXTORTION', 'OTHER')
    ),
    CONSTRAINT ck_review_reports_status CHECK (
        status IN ('PENDING', 'UNDER_REVIEW', 'RESOLVED', 'DISMISSED')
    )
);

CREATE INDEX ix_review_reports_review_id ON review_reports(review_id);
CREATE INDEX ix_review_reports_status ON review_reports(status);
CREATE INDEX ix_review_reports_reported_by ON review_reports(reported_by);
```

### 18. business_reports

Reports of problematic businesses.

```sql
CREATE TABLE business_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    reported_by UUID NOT NULL REFERENCES users(id),
    reason VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolved_by UUID REFERENCES users(id),
    resolution_notes TEXT,
    
    CONSTRAINT ck_business_reports_reason CHECK (
        reason IN ('FAKE_LISTING', 'INCORRECT_INFORMATION', 'CLOSED_BUSINESS', 
                   'INCORRECT_PRICES', 'FRAUD', 'HARASSMENT', 'OTHER')
    ),
    CONSTRAINT ck_business_reports_status CHECK (
        status IN ('PENDING', 'UNDER_REVIEW', 'RESOLVED', 'DISMISSED')
    )
);

CREATE INDEX ix_business_reports_business_id ON business_reports(business_id);
CREATE INDEX ix_business_reports_status ON business_reports(status);
CREATE INDEX ix_business_reports_reported_by ON business_reports(reported_by);
```

### 19. favorites

Student saved/bookmarked businesses.

```sql
CREATE TABLE favorites (
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    PRIMARY KEY (user_id, business_id)
);

CREATE INDEX ix_favorites_user_id ON favorites(user_id);
CREATE INDEX ix_favorites_business_id ON favorites(business_id);
```

### 20. offers

Business offers and discounts.

```sql
CREATE TABLE offers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    discount_type VARCHAR(20) NOT NULL,
    discount_value DECIMAL(10, 2) NOT NULL,
    terms_conditions TEXT,
    valid_from TIMESTAMP WITH TIME ZONE NOT NULL,
    valid_until TIMESTAMP WITH TIME ZONE NOT NULL,
    max_redemptions INTEGER,
    redemption_count INTEGER NOT NULL DEFAULT 0,
    status VARCHAR(20) NOT NULL DEFAULT 'DRAFT',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    CONSTRAINT ck_offers_discount_type CHECK (
        discount_type IN ('PERCENTAGE', 'FIXED_AMOUNT', 'SERVICE_DISCOUNT')
    ),
    CONSTRAINT ck_offers_discount_value CHECK (discount_value > 0),
    CONSTRAINT ck_offers_status CHECK (
        status IN ('DRAFT', 'ACTIVE', 'PAUSED', 'EXPIRED', 'CANCELLED')
    ),
    CONSTRAINT ck_offers_redemptions CHECK (
        max_redemptions IS NULL OR max_redemptions > 0
    ),
    CONSTRAINT ck_offers_redemption_count CHECK (redemption_count >= 0),
    CONSTRAINT ck_offers_dates CHECK (valid_until > valid_from)
);

CREATE INDEX ix_offers_business_id ON offers(business_id);
CREATE INDEX ix_offers_status ON offers(status);
CREATE INDEX ix_offers_valid_until ON offers(valid_until);
```

### 21. offer_redemptions

Tracking of offer usage.

```sql
CREATE TABLE offer_redemptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    offer_id UUID NOT NULL REFERENCES offers(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id),
    redeemed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    verification_code VARCHAR(50),
    
    CONSTRAINT ck_offer_redemptions_status CHECK (
        status IN ('PENDING', 'COMPLETED', 'CANCELLED', 'EXPIRED')
    )
);

CREATE INDEX ix_offer_redemptions_offer_id ON offer_redemptions(offer_id);
CREATE INDEX ix_offer_redemptions_user_id ON offer_redemptions(user_id);
CREATE INDEX ix_offer_redemptions_redeemed_at ON offer_redemptions(redeemed_at);
```

### 22. transactions

Future-ready table for payment/booking transactions.

```sql
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES students(id),
    business_id UUID NOT NULL REFERENCES businesses(id),
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'INR',
    status VARCHAR(30) NOT NULL,
    payment_provider VARCHAR(50),
    provider_reference VARCHAR(255),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT ck_transactions_amount CHECK (amount > 0),
    CONSTRAINT ck_transactions_status CHECK (
        status IN ('PENDING', 'PAID', 'SERVICE_COMPLETED', 'REFUND_REQUESTED', 
                   'REFUNDED', 'DISPUTED', 'FAILED', 'CANCELLED')
    )
);

CREATE INDEX ix_transactions_student_id ON transactions(student_id);
CREATE INDEX ix_transactions_business_id ON transactions(business_id);
CREATE INDEX ix_transactions_status ON transactions(status);
CREATE INDEX ix_transactions_created_at ON transactions(created_at DESC);
```

**Note**: Do NOT implement escrow/payment logic in MVP. This table structure exists for future use.

### 23. notifications

User notifications.

```sql
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    type VARCHAR(50) NOT NULL,
    reference_type VARCHAR(50),
    reference_id UUID,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    read_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX ix_notifications_user_id ON notifications(user_id);
CREATE INDEX ix_notifications_is_read ON notifications(user_id, is_read);
CREATE INDEX ix_notifications_created_at ON notifications(created_at DESC);
```

### 24. audit_logs

Admin action audit trail.

```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    admin_id UUID NOT NULL REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID NOT NULL,
    old_data JSONB,
    new_data JSONB,
    reason TEXT,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_audit_logs_admin_id ON audit_logs(admin_id);
CREATE INDEX ix_audit_logs_entity_type ON audit_logs(entity_type);
CREATE INDEX ix_audit_logs_entity_id ON audit_logs(entity_id);
CREATE INDEX ix_audit_logs_created_at ON audit_logs(created_at DESC);
```

**Purpose**: Every sensitive admin action (approve business, suspend user, remove review) MUST create an audit log entry.

---

## Indexes and Constraints Summary

### Primary Keys
All tables use UUID primary keys via `gen_random_uuid()`.

### Foreign Keys
All foreign key relationships include `ON DELETE` clauses:
- `CASCADE`: Delete dependent records (e.g., reviews when business deleted)
- `SET NULL`: Clear reference (e.g., category parent when parent deleted)

### Unique Constraints
- `users.email` - Unique email addresses
- `users.phone` - Unique phone numbers
- `students.user_id` - One student profile per user
- `colleges.email_domain` - One college per email domain
- `categories.slug` - Unique category slugs
- `reviews (user_id, business_id, deleted_at)` - One active review per user/business
- `review_responses.review_id` - One response per review

### Check Constraints
- Rating values: 1-5 range
- Prices: >= 0
- Coordinates: Valid lat/lng ranges
- Status enums: Valid enum values
- Dates: logical date ordering

### Indexes
- All foreign keys are indexed
- Frequently queried columns (status, email, etc.)
- Geospatial indexes (GIST) on location columns
- Composite indexes for common query patterns

---

## Enumerations

### User Roles
- `STUDENT` - Verified college student
- `OWNER` - Business owner
- `ADMIN` - Platform administrator
- `COLLEGE_ADMIN` - College-specific admin (future)

### User/Business Status
- `PENDING` - Awaiting action
- `ACTIVE` - Active and operational
- `SUSPENDED` - Temporarily disabled
- `REJECTED` - Denied access
- `REMOVED` - Soft deleted

### Verification Status
- `UNVERIFIED` - Not yet verified
- `PENDING` - Verification in progress
- `VERIFIED` - Successfully verified
- `EXPIRED` - Verification expired (future)

### Review Verification Levels
- `UNVERIFIED` - Basic review
- `VERIFIED_STUDENT` - From verified student
- `VERIFIED_VISIT` - Visit confirmed (future)
- `VERIFIED_TRANSACTION` - Transaction confirmed (future)

---

## Geospatial Queries

### PostGIS Setup

```sql
CREATE EXTENSION IF NOT EXISTS postgis;
```

### Auto-populate Location from Lat/Lng

```sql
CREATE OR REPLACE FUNCTION update_location_from_coordinates()
RETURNS TRIGGER AS $$
BEGIN
    NEW.location = ST_SetSRID(ST_MakePoint(NEW.longitude, NEW.latitude), 4326)::geography;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_businesses_location
    BEFORE INSERT OR UPDATE OF latitude, longitude ON businesses
    FOR EACH ROW
    EXECUTE FUNCTION update_location_from_coordinates();

CREATE TRIGGER tr_campuses_location
    BEFORE INSERT OR UPDATE OF latitude, longitude ON campuses
    FOR EACH ROW
    EXECUTE FUNCTION update_location_from_coordinates();
```

### Find Businesses Within Radius

```sql
-- Find all businesses within 3km of a point
SELECT 
    b.id,
    b.name,
    ST_Distance(b.location, ST_SetSRID(ST_MakePoint(73.9375, 18.7830), 4326)::geography) AS distance_meters
FROM businesses b
WHERE 
    ST_DWithin(
        b.location,
        ST_SetSRID(ST_MakePoint(73.9375, 18.7830), 4326)::geography,
        3000  -- 3km in meters
    )
    AND b.status = 'ACTIVE'
    AND b.deleted_at IS NULL
ORDER BY distance_meters;
```

### Find Businesses Near Campus

```sql
-- Find businesses within campus radius
SELECT 
    b.id,
    b.name,
    c.name AS campus_name,
    ST_Distance(b.location, c.location) AS distance_meters
FROM businesses b
JOIN campuses c ON b.campus_id = c.id
WHERE 
    ST_DWithin(b.location, c.location, c.radius_meters)
    AND b.status = 'ACTIVE'
    AND b.deleted_at IS NULL;
```

---

## Migration Strategy

### Alembic Configuration

```python
# migrations/env.py
from app.core.database import Base
from app.models import *  # Import all models

target_metadata = Base.metadata
```

### Migration Naming Convention

```
{revision}_{description}.py

Examples:
001_initial_schema.py
002_add_business_hours.py
003_add_review_photos.py
```

### Migration Best Practices

1. **One logical change per migration** - Don't combine unrelated changes
2. **Always test rollback** - Ensure `downgrade()` works
3. **Never modify committed migrations** - Create new migration instead
4. **Add indexes separately** - Large indexes in separate migration
5. **Use batch operations** - For data migrations on large tables
6. **Test on production-like data** - Validate migration performance

### Creating Migrations

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add business verification workflow"

# Create empty migration for data changes
alembic revision -m "Populate initial categories"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history

# View current version
alembic current
```

---

## Database Seed Data

### Initial Data Requirements

1. **Admin User** - Platform administrator account
2. **Test College** - MIT Academy of Engineering
3. **Test Campus** - MIT AOE Alandi campus
4. **Categories** - Initial business categories (~50)
5. **Rating Dimensions** - Category-specific dimensions
6. **Test Students** - 5-10 verified test accounts
7. **Test Owners** - 3-5 business owner accounts
8. **Sample Businesses** - 20-30 sample listings
9. **Sample Services** - Services for sample businesses
10. **Sample Reviews** - 50-100 test reviews

### Seed Script Structure

```bash
backend/
└── app/
    └── utils/
        └── seed.py  # Seed data script
```

Run seed data:
```bash
python -m app.utils.seed
```

---

## Backup and Maintenance

### Daily Backups

```bash
pg_dump -Fc aaspaas_prod > backup_$(date +%Y%m%d).dump
```

### Point-in-Time Recovery

Enable WAL archiving in PostgreSQL configuration for production.

### Vacuum and Analyze

```sql
-- Regular maintenance
VACUUM ANALYZE;

-- Per table
VACUUM ANALYZE businesses;
```

---

## Performance Considerations

### Query Optimization
- Use `EXPLAIN ANALYZE` for slow queries
- Add indexes based on actual query patterns
- Use partial indexes where appropriate
- Consider materialized views for complex aggregations

### Connection Pooling
- Use PgBouncer or SQLAlchemy's built-in pooling
- Start with pool size of 10-20 connections

### Monitoring
- Track slow queries (> 100ms)
- Monitor connection usage
- Watch table bloat
- Monitor index usage

---

## Security Considerations

1. **No Secrets in Database** - Store sensitive config in environment variables
2. **Use SSL** - Enable SSL for database connections in production
3. **Least Privilege** - Application user has only necessary permissions
4. **Audit Logging** - All admin actions logged in audit_logs
5. **Soft Deletion** - Important records use soft delete (deleted_at)
6. **Input Validation** - Backend validates all data before insert/update
7. **No Raw SQL** - Use SQLAlchemy ORM to prevent SQL injection

---

## Conclusion

This database schema supports:

1. **MVP Requirements** - All features in PROJECT_SPEC.md
2. **Data Integrity** - Foreign keys, constraints, validation
3. **Scalability** - Indexed for common queries, PostGIS for geospatial
4. **Audit Trail** - Admin actions logged
5. **Trust Layers** - Verification statuses at multiple levels
6. **Future Growth** - Transaction table ready, extensible categories

The schema will evolve through Alembic migrations as features are implemented and validated during the pilot phase.

---

**Next Document**: API_SPEC.md - API endpoint specifications
