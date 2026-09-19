# AAS PAAS

**Everything You Need, Aas Paas.**

A campus-focused marketplace where verified college students can discover, compare, review, and eventually transact with businesses and services around their campus.

## Project Status

🏗️ **Phase 0: Foundation** - Repository initialization and architecture documentation

## Product Overview

AAS PAAS is a trust-based local marketplace platform designed specifically for college campuses. The platform connects verified students with local businesses through:

- **Verified student identity** via college email verification
- **Verified businesses** through admin approval workflow
- **Structured reviews** with category-specific rating dimensions
- **Transparent pricing** with update timestamps
- **Location-aware discovery** using geospatial search
- **Student-specific benefits** including discounts and offers

### Initial Pilot

- **Campus**: MIT Academy of Engineering (MIT AOE), Alandi, Pune, Maharashtra
- **Geographic scope**: ~3 km radius around campus
- **Target**: 100-200 businesses, 500+ verified students, 300+ reviews

## Technology Stack

### Mobile Application
- **Framework**: Flutter + Dart
- **Platform**: iOS & Android

### Backend
- **Framework**: FastAPI (Python)
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Database**: PostgreSQL + PostGIS
- **Authentication**: JWT-based (implementation TBD)

### Admin Panel
- **Framework**: Next.js + TypeScript
- **Platform**: Web

### Infrastructure
- **Image Storage**: S3-compatible object storage (provider TBD)
- **Push Notifications**: Firebase Cloud Messaging
- **Maps**: Google Maps Platform or Mapbox (TBD)

## Repository Structure

```
aas-paas/
├── backend/           # FastAPI backend application
├── mobile/            # Flutter mobile application
├── admin/             # Next.js admin panel
├── docs/              # Project documentation
├── docker/            # Docker configuration (future)
├── PROJECT_SPEC.md    # Complete product specification
└── README.md          # This file
```

## Documentation

- **[PROJECT_SPEC.md](PROJECT_SPEC.md)** - Complete product and technical specification
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System architecture and design decisions
- **[DATABASE.md](docs/DATABASE.md)** - Database schema and data model
- **[API_SPEC.md](docs/API_SPEC.md)** - API endpoints and contracts
- **[SECURITY.md](docs/SECURITY.md)** - Security requirements and guidelines

## Prerequisites

### Backend Development
- Python 3.11 or higher
- PostgreSQL 15+ with PostGIS extension
- pip or poetry for dependency management

### Mobile Development
- Flutter SDK 3.x
- Dart SDK
- Android Studio / Xcode (for respective platforms)

### Admin Development
- Node.js 18+ LTS
- npm or yarn

## Getting Started

### Backend Setup

1. **Create virtual environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Setup database**
   ```bash
   # Create PostgreSQL database with PostGIS
   createdb aaspaas_dev
   psql -d aaspaas_dev -c "CREATE EXTENSION IF NOT EXISTS postgis;"
   
   # Run migrations
   alembic upgrade head
   ```

5. **Run development server**
   ```bash
   uvicorn app.main:app --reload
   ```

   Backend will be available at `http://localhost:8000`
   API documentation at `http://localhost:8000/docs`

### Mobile Setup

1. **Navigate to mobile directory**
   ```bash
   cd mobile
   ```

2. **Install dependencies**
   ```bash
   flutter pub get
   ```

3. **Configure environment**
   ```bash
   # Create environment configuration
   # Edit lib/core/config/environment.dart
   ```

4. **Run application**
   ```bash
   flutter run
   ```

### Admin Setup

1. **Navigate to admin directory**
   ```bash
   cd admin
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your configuration
   ```

4. **Run development server**
   ```bash
   npm run dev
   ```

   Admin panel will be available at `http://localhost:3000`

## Testing

### Backend Tests
```bash
cd backend
pytest                           # Run all tests
pytest tests/unit               # Unit tests only
pytest tests/integration        # Integration tests only
pytest --cov=app                # With coverage report
```

### Mobile Tests
```bash
cd mobile
flutter test                    # Run all tests
flutter test --coverage         # With coverage report
```

### Admin Tests
```bash
cd admin
npm test                        # Run all tests
npm run test:watch              # Watch mode
```

## Development Workflow

### Branch Strategy
- `main` - Production-ready code
- `develop` - Integration branch
- `feature/*` - Feature development
- `fix/*` - Bug fixes

### Commit Convention
```
feat(auth): add student registration
feat(review): add structured ratings
fix(business): prevent unauthorized edits
docs(api): update authentication endpoints
test(review): add review creation tests
```

### Code Quality
- **Backend**: Use `black` for formatting, `flake8` for linting, `mypy` for type checking
- **Mobile**: Use `dart format`, `dart analyze`
- **Admin**: Use `prettier` for formatting, `eslint` for linting

## Incremental Development Phases

The project follows an 18-phase incremental development strategy:

**Phase 0**: Repository + Architecture (CURRENT)  
**Phase 1**: Backend Foundation  
**Phase 2**: Database + Migrations  
**Phase 3**: Authentication  
**Phase 4**: College/Student Verification  
**Phase 5**: Student Profiles  
**Phase 6**: Business Module  
**Phase 7**: Categories + Search  
**Phase 8**: Business Details  
**Phase 9**: Reviews  
**Phase 10**: Photos  
**Phase 11**: Maps/Location  
**Phase 12**: Favorites  
**Phase 13**: Offers  
**Phase 14**: Owner Dashboard  
**Phase 15**: Admin Dashboard  
**Phase 16**: Reports + Moderation  
**Phase 17**: Testing/Security  
**Phase 18**: Deployment Preparation  

Each phase must be functional and tested before proceeding to the next.

## Core Product Principles

1. **Trust before growth** - Do not sacrifice review integrity for listing count
2. **Student-first discovery** - Answer student needs quickly
3. **Transparent information** - Show prices, hours, and freshness
4. **Business accountability** - Owners cannot arbitrarily delete legitimate reviews
5. **No pay-to-trust** - Verification is earned, not purchased
6. **Campus density first** - Deep campus coverage before geographic expansion

## User Roles

- **STUDENT** - Browse, search, review, save businesses
- **OWNER** - Manage business listings, respond to reviews, create offers
- **ADMIN** - Verify businesses, moderate content, manage platform
- **COLLEGE_ADMIN** - Future role for college-specific administration

## Security Notes

- All passwords hashed using Argon2 or bcrypt
- JWT tokens with refresh rotation
- Server-side authorization for all protected endpoints
- Rate limiting on sensitive operations
- Input validation on all user data
- Audit logging for all admin actions
- No secrets in source code - use environment variables

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://user:password@localhost/aaspaas_dev
JWT_SECRET=<generate-secure-secret>
JWT_REFRESH_SECRET=<generate-secure-secret>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Storage
STORAGE_TYPE=s3  # or cloudinary
STORAGE_BUCKET=<bucket-name>
STORAGE_ACCESS_KEY=<access-key>
STORAGE_SECRET_KEY=<secret-key>

# Maps
GOOGLE_MAPS_API_KEY=<api-key>

# Notifications
FIREBASE_CREDENTIALS_PATH=<path-to-firebase-credentials>

# Environment
ENVIRONMENT=development
DEBUG=True
```

### Mobile (environment.dart)
```dart
// Configure in lib/core/config/environment.dart
```

### Admin (.env.local)
```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_ENVIRONMENT=development
```

## License

Proprietary - All rights reserved

## Contact

For questions or support during development, contact the project team.

---

**Note**: This is an active development project. The specification in `PROJECT_SPEC.md` is the authoritative source for all product and technical decisions.
