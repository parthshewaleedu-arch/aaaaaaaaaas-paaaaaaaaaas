# AAS PAAS - System Architecture

**Document Version:** 1.0  
**Last Updated:** 2026-09-19  
**Status:** Foundation - Pre-implementation architecture specification

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Technology Stack](#technology-stack)
3. [System Components](#system-components)
4. [Backend Architecture](#backend-architecture)
5. [Mobile Architecture](#mobile-architecture)
6. [Admin Architecture](#admin-architecture)
7. [Data Flow](#data-flow)
8. [Security Architecture](#security-architecture)
9. [Deployment Architecture](#deployment-architecture)
10. [Scalability Considerations](#scalability-considerations)

---

## Architecture Overview

AAS PAAS follows a **modular monolith architecture** with clear separation between client applications and the backend API. This architecture is designed to support the initial single-campus pilot while maintaining the flexibility to scale to multiple campuses and colleges.

### Core Architectural Principles

1. **Separation of Concerns** - Clear boundaries between presentation, business logic, and data access layers
2. **Server-Side Authorization** - All permission checks occur on the backend; frontend restrictions are UX-only
3. **API-First Design** - Backend exposes RESTful APIs that any authorized client can consume
4. **Data Integrity** - Database constraints and application-level validation ensure data consistency
5. **Audit Trail** - All sensitive administrative actions are logged
6. **Location-Aware** - PostGIS powers geospatial queries for campus-centric discovery
7. **Verification Layers** - Multiple trust levels (verified student, verified business, verified transaction)

### System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         AAS PAAS SYSTEM                          │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐                              ┌──────────────────┐
│  Flutter Mobile  │                              │  Next.js Admin   │
│   (iOS/Android)  │                              │    (Web Panel)   │
└────────┬─────────┘                              └────────┬─────────┘
         │                                                  │
         │              HTTPS / REST API                    │
         │                  (JSON)                          │
         └──────────────────┬──────────────────────────────┘
                            │
                    ┌───────▼────────┐
                    │   FastAPI      │
                    │   Backend      │
                    │  (Python 3.11) │
                    └───────┬────────┘
                            │
         ┌──────────────────┼──────────────────┐
         │                  │                  │
    ┌────▼─────┐    ┌──────▼──────┐    ┌─────▼────┐
    │PostgreSQL│    │Object Storage│    │  FCM     │
    │+ PostGIS │    │   (Images)   │    │(Push)    │
    └──────────┘    └──────────────┘    └──────────┘
```

---

## Technology Stack

### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **ORM**: SQLAlchemy 2.x
- **Migrations**: Alembic
- **Database**: PostgreSQL 15+ with PostGIS extension
- **Authentication**: JWT (JSON Web Tokens)
- **Password Hashing**: Argon2 or bcrypt
- **Validation**: Pydantic v2
- **Testing**: pytest, pytest-asyncio

### Mobile Application
- **Framework**: Flutter 3.x
- **Language**: Dart 3.x
- **State Management**: TBD (Provider, Riverpod, or Bloc)
- **HTTP Client**: dio or http package
- **Local Storage**: sqflite, shared_preferences
- **Maps**: google_maps_flutter or mapbox_gl
- **Push Notifications**: firebase_messaging

### Admin Panel
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript 5.x
- **UI Library**: TBD (Tailwind CSS, shadcn/ui, or similar)
- **State Management**: React Context / Zustand
- **HTTP Client**: fetch API or axios
- **Authentication**: JWT stored in httpOnly cookies

### Infrastructure
- **Image Storage**: S3-compatible object storage (AWS S3, MinIO, or Cloudinary)
- **Push Notifications**: Firebase Cloud Messaging
- **Maps Provider**: Google Maps Platform or Mapbox
- **Reverse Proxy**: Nginx (production)
- **Process Manager**: systemd or supervisor (production)

---

## System Components

### 1. Mobile Application (Flutter)

The primary interface for students and business owners.

**Key Responsibilities:**
- User authentication and profile management
- Business discovery and search
- Maps and location-based browsing
- Review creation with structured ratings
- Business detail views
- Offer browsing and redemption
- Owner dashboard (for business accounts)

**Does NOT Handle:**
- Server-side authorization logic
- Sensitive data validation
- Payment processing (future)
- Administrative functions

### 2. Backend API (FastAPI)

The central business logic and data access layer.

**Key Responsibilities:**
- User authentication and authorization
- College email verification
- Business CRUD operations
- Business verification workflow
- Review system with category-specific ratings
- Geospatial queries (nearby businesses)
- Search and filtering
- Offer management
- Admin operations
- Audit logging
- Rate limiting
- Data validation

### 3. Admin Panel (Next.js)

Web-based administrative interface for platform management.

**Key Responsibilities:**
- Business verification approval workflow
- Content moderation (reviews, photos)
- Report management
- User management
- College and campus configuration
- Category management
- Analytics dashboard
- Audit log inspection

### 4. Database (PostgreSQL + PostGIS)

Central data store with geospatial capabilities.

**Key Responsibilities:**
- Persistent data storage
- Referential integrity enforcement
- Geospatial indexing and queries
- Full-text search (initial implementation)
- Transaction support

### 5. Object Storage

External storage for user-generated media.

**Key Responsibilities:**
- Business photos
- Review photos
- Profile images
- Static assets

### 6. Firebase Cloud Messaging

Push notification delivery service.

**Key Responsibilities:**
- Deliver push notifications to mobile devices
- Handle device token management
- Support notification targeting

---

## Backend Architecture

### Layered Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                   │
│  - Route handlers (routers)                              │
│  - Request/response models (Pydantic schemas)            │
│  - Authentication/authorization middleware               │
│  - Error handling                                        │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                   Service Layer                          │
│  - Business logic                                        │
│  - Cross-cutting concerns (email, notifications)         │
│  - Complex operations                                    │
│  - Permission checks                                     │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                 Repository Layer                         │
│  - Data access abstraction                               │
│  - Query composition                                     │
│  - Transaction management                                │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                   ORM Layer (SQLAlchemy)                 │
│  - Model definitions                                     │
│  - Relationships                                         │
│  - Database session management                           │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  Database (PostgreSQL)                   │
└─────────────────────────────────────────────────────────┘
```

### Directory Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entrypoint
│   │
│   ├── api/                       # API routes
│   │   ├── __init__.py
│   │   └── v1/                    # API version 1
│   │       ├── __init__.py
│   │       ├── auth.py            # Authentication endpoints
│   │       ├── students.py        # Student endpoints
│   │       ├── businesses.py      # Business endpoints
│   │       ├── reviews.py         # Review endpoints
│   │       ├── offers.py          # Offer endpoints
│   │       ├── admin.py           # Admin endpoints
│   │       └── colleges.py        # College configuration
│   │
│   ├── core/                      # Core configuration
│   │   ├── __init__.py
│   │   ├── config.py              # Application settings
│   │   ├── security.py            # Auth utilities (JWT, password hashing)
│   │   ├── database.py            # Database session management
│   │   └── dependencies.py        # FastAPI dependencies
│   │
│   ├── models/                    # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── student.py
│   │   ├── college.py
│   │   ├── campus.py
│   │   ├── business.py
│   │   ├── category.py
│   │   ├── review.py
│   │   ├── offer.py
│   │   └── audit_log.py
│   │
│   ├── schemas/                   # Pydantic models for validation
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── student.py
│   │   ├── business.py
│   │   ├── review.py
│   │   └── common.py              # Shared schemas
│   │
│   ├── services/                  # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── student_service.py
│   │   ├── business_service.py
│   │   ├── review_service.py
│   │   ├── verification_service.py
│   │   └── notification_service.py
│   │
│   ├── repositories/              # Data access layer
│   │   ├── __init__.py
│   │   ├── user_repository.py
│   │   ├── business_repository.py
│   │   └── review_repository.py
│   │
│   └── utils/                     # Utility functions
│       ├── __init__.py
│       ├── email.py
│       ├── storage.py             # Object storage abstraction
│       └── geospatial.py          # PostGIS utilities
│
├── migrations/                    # Alembic migrations
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
│
├── tests/                         # Test suite
│   ├── unit/
│   ├── integration/
│   └── conftest.py
│
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variable template
└── README.md
```

### API Versioning

All API endpoints are versioned under `/api/v1/`. This allows future breaking changes to be introduced under `/api/v2/` without affecting existing clients.

Example endpoints:
- `POST /api/v1/auth/register`
- `GET /api/v1/businesses`
- `POST /api/v1/businesses/{id}/reviews`

### Authentication Flow

1. **Registration**: User registers with email/phone and password
2. **Email Verification**: Verification link sent to email
3. **Login**: User authenticates with credentials
4. **Token Issuance**: Backend returns JWT access token + refresh token
5. **Authenticated Requests**: Client includes `Authorization: Bearer <token>` header
6. **Token Refresh**: Client uses refresh token to obtain new access token before expiry

### Authorization Pattern

Every protected endpoint follows this pattern:

```python
@router.get("/businesses/{business_id}")
async def get_business(
    business_id: UUID,
    current_user: User = Depends(get_current_user),  # Authentication
    db: Session = Depends(get_db)
):
    business = business_service.get_business(db, business_id)
    
    # Authorization check (if needed)
    if not business_service.can_view(current_user, business):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return business
```

**Critical Rule**: Never trust authorization checks performed by the client. All permission validation occurs server-side.

---

## Mobile Architecture

### Feature-Based Structure (Recommended)

```
mobile/
└── lib/
    ├── main.dart
    │
    ├── core/                       # Shared core utilities
    │   ├── config/
    │   ├── constants/
    │   ├── theme/
    │   ├── utils/
    │   └── widgets/                # Reusable UI components
    │
    ├── features/                   # Feature modules
    │   ├── auth/
    │   │   ├── data/               # Data sources, repositories
    │   │   ├── domain/             # Business logic, entities
    │   │   └── presentation/       # UI, state management
    │   │
    │   ├── business/
    │   │   ├── data/
    │   │   ├── domain/
    │   │   └── presentation/
    │   │
    │   ├── review/
    │   └── profile/
    │
    └── shared/                     # Shared across features
        ├── models/
        ├── services/
        └── repositories/
```

### State Management

The specific state management solution (Provider, Riverpod, Bloc, or other) will be chosen during mobile implementation. The architecture must support:

- Separation of UI state from business logic
- Authentication state management
- API request state (loading, success, error)
- Offline capability considerations

---

## Admin Architecture

### Next.js App Router Structure

```
admin/
├── src/
│   ├── app/                       # App Router pages
│   │   ├── layout.tsx
│   │   ├── page.tsx              # Dashboard
│   │   ├── login/
│   │   ├── businesses/
│   │   ├── reviews/
│   │   ├── users/
│   │   └── audit-logs/
│   │
│   ├── components/               # React components
│   │   ├── ui/                   # Base UI components
│   │   ├── layout/
│   │   └── features/
│   │
│   ├── lib/                      # Utilities
│   │   ├── api/                  # API client
│   │   ├── auth/                 # Auth utilities
│   │   └── utils/
│   │
│   └── types/                    # TypeScript types
│
├── public/
├── package.json
└── tsconfig.json
```

---

## Data Flow

### Student Reviews Business Flow

```
1. Student opens business detail page
   ↓
2. Mobile app: GET /api/v1/businesses/{id}
   ↓
3. Backend validates request, queries database
   ↓
4. Response includes business details, reviews, ratings
   ↓
5. Student clicks "Write Review"
   ↓
6. Mobile app: POST /api/v1/businesses/{id}/reviews
   {
     overall_rating: 4,
     review_text: "Good food",
     ratings: [
       {dimension_id: "food-quality", rating: 5},
       {dimension_id: "hygiene", rating: 4}
     ]
   }
   ↓
7. Backend:
   - Validates authentication
   - Validates student is verified
   - Checks for existing review
   - Validates rating dimensions for category
   - Creates review record
   - Updates business cached ratings
   - Creates audit entry
   ↓
8. Response: Review created successfully
   ↓
9. Mobile app refreshes business detail page
```

### Business Verification Workflow

```
1. Owner creates business listing
   ↓
2. Owner submits for verification
   ↓
3. Business status: PENDING
   ↓
4. Admin receives notification
   ↓
5. Admin reviews in web panel
   ↓
6. Admin decision:
   - APPROVE → Business becomes ACTIVE + VERIFIED
   - REJECT → Business remains PENDING, owner notified
   - REQUEST_INFO → Owner asked for more details
   ↓
7. Audit log created with admin action
   ↓
8. Owner receives notification
```

---

## Security Architecture

### Authentication

**JWT-Based Authentication**

- **Access Token**: Short-lived (30 minutes), used for API requests
- **Refresh Token**: Longer-lived (7 days), used to obtain new access tokens
- **Token Storage**:
  - Mobile: Secure storage (Flutter Secure Storage)
  - Admin: httpOnly cookies (not accessible via JavaScript)

### Password Security

- **Hashing**: Argon2id or bcrypt with appropriate work factors
- **Password Requirements**: Minimum length, complexity rules (TBD)
- **Password Reset**: Time-limited tokens sent via email

### Authorization Levels

1. **Unauthenticated** - Public business browsing (limited)
2. **Authenticated Student** - Full discovery, review creation
3. **Verified Student** - Enhanced trust signals on reviews
4. **Business Owner** - Manage owned businesses only
5. **Admin** - Platform-wide moderation and configuration

### Input Validation

- **Client-Side**: UX convenience only (format hints, character limits)
- **Server-Side**: Authoritative validation via Pydantic schemas
- **Database**: Constraints enforce data integrity

### Rate Limiting

Protected endpoints (TBD specific limits):
- Login attempts: 5 per 15 minutes per IP
- Registration: 3 per hour per IP
- Review creation: 10 per day per user
- Password reset: 3 per hour per email

### SQL Injection Prevention

- **ORM Usage**: SQLAlchemy parameterized queries
- **Raw SQL**: Avoided; if necessary, always parameterized

### CORS Configuration

- **Production**: Whitelist specific origins (mobile app, admin panel)
- **Development**: Localhost exceptions only

### File Upload Security

- **Validation**:
  - MIME type checking
  - File signature verification
  - Maximum size limits (5MB for photos)
  - Image dimension validation
- **Storage**: Images stored in object storage, not served from backend
- **Access**: Signed URLs for private content

---

## Deployment Architecture

### Initial Production (Single Server)

```
┌─────────────────────────────────────────────────┐
│                  Production Server               │
│                                                  │
│  ┌──────────┐                                   │
│  │  Nginx   │  (Reverse Proxy, SSL)             │
│  └────┬─────┘                                   │
│       │                                          │
│  ┌────▼──────────┐                              │
│  │ FastAPI       │  (systemd/supervisor)        │
│  │ (uvicorn)     │                              │
│  └────┬──────────┘                              │
│       │                                          │
│  ┌────▼──────────┐                              │
│  │ PostgreSQL    │                              │
│  │ + PostGIS     │                              │
│  └───────────────┘                              │
│                                                  │
└─────────────────────────────────────────────────┘

External Services:
- S3 / Object Storage (images)
- Firebase (push notifications)
- Google Maps / Mapbox (maps)
```

### Database Backup Strategy

- Automated daily backups
- Point-in-time recovery capability (if using managed PostgreSQL)
- Off-server backup storage
- Regular restore testing

---

## Scalability Considerations

### Current Architecture (MVP)

The initial modular monolith is designed for:
- Single campus pilot
- ~500 verified students
- ~200 businesses
- Thousands of reviews
- Moderate concurrent usage

### Future Scalability Options

**Database:**
- Read replicas for read-heavy workloads
- Connection pooling (PgBouncer)
- Query optimization and indexing

**Application:**
- Horizontal scaling (multiple FastAPI instances behind load balancer)
- Redis caching layer for frequently accessed data
- Background job queue (Celery) for async operations

**Storage:**
- CDN for static assets and images
- Separate storage buckets per region

**Search:**
- Elasticsearch or similar for advanced search (when PostgreSQL full-text becomes insufficient)

**Future Separation:**
- Admin panel could be deployed separately
- Background workers could run on dedicated instances
- Microservices extraction if specific domains become complex

---

## Design Decisions Log

### Why Modular Monolith?

**Decision**: Start with a modular monolith rather than microservices.

**Rationale**:
- Simpler deployment and operations for MVP
- Easier to reason about data consistency
- Lower operational overhead
- Can be split into services later if specific modules require independent scaling
- Product requirements are still being validated

### Why FastAPI?

**Decision**: Use FastAPI for backend framework.

**Rationale**:
- Modern async Python framework
- Excellent type checking with Pydantic
- Automatic OpenAPI documentation
- High performance
- Easy integration with SQLAlchemy
- Good for future ML/AI features (Python ecosystem)

### Why Flutter?

**Decision**: Use Flutter for mobile application.

**Rationale**:
- Single codebase for iOS and Android
- Native performance
- Rich widget ecosystem
- Good developer experience
- Suitable for the app's requirements

### Why PostgreSQL + PostGIS?

**Decision**: Use PostgreSQL with PostGIS extension.

**Rationale**:
- Robust relational database with ACID guarantees
- PostGIS provides powerful geospatial capabilities
- Excellent full-text search for initial implementation
- JSON support for flexible data
- Mature ecosystem and tooling

### Why JWT for Authentication?

**Decision**: Use JWT tokens for authentication.

**Rationale**:
- Stateless authentication (no server-side session storage)
- Works well with mobile clients
- Can include user metadata in token
- Industry standard
- Easy to implement refresh token rotation

---

## Non-Functional Requirements

### Performance Targets (Initial)

- API response time: < 200ms (p95) for reads
- API response time: < 500ms (p95) for writes
- Database query time: < 100ms (p95)
- Image upload: < 3s for 2MB image

### Availability

- Target: 99% uptime during pilot
- Planned maintenance windows acceptable
- Graceful degradation (e.g., map features fail, but business browsing continues)

### Data Retention

- User data: Retained until account deletion
- Audit logs: Retained indefinitely (or per legal requirements)
- Deleted content: Soft-deleted, retained for 90 days

---

## Monitoring and Observability (Future)

- **Error Tracking**: Sentry or similar
- **Logging**: Structured JSON logs
- **Metrics**: Prometheus + Grafana or managed solution
- **Uptime Monitoring**: Uptime robot or similar
- **APM**: Application performance monitoring (TBD)

---

## Conclusion

This architecture is designed to:

1. **Support the MVP** - Handle single-campus pilot requirements
2. **Maintain Quality** - Clear separation of concerns, testable code
3. **Enable Growth** - Can scale to multiple campuses without rewrite
4. **Ensure Security** - Server-side authorization, audit logging, secure authentication
5. **Facilitate Development** - Well-defined layers, clear data flow

The architecture will evolve as requirements are validated during the pilot phase. Any major architectural changes must be documented and justified.

---

**Next Steps:**
- Implement Phase 1: Backend Foundation
- Create initial database models
- Set up authentication system
- Build first API endpoints
