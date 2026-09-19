# AAS PAAS Backend

FastAPI backend application for AAS PAAS campus marketplace platform.

## Project Structure

```
backend/
├── app/
│   ├── api/                    # API routes
│   │   └── v1/                 # API version 1
│   ├── core/                   # Core configuration
│   ├── models/                 # SQLAlchemy ORM models
│   ├── schemas/                # Pydantic validation schemas
│   ├── services/               # Business logic layer
│   ├── repositories/           # Data access layer
│   ├── utils/                  # Utility functions
│   └── main.py                 # Application entrypoint
│
├── migrations/                 # Alembic database migrations
├── tests/                      # Test suite
│   ├── unit/                   # Unit tests
│   └── integration/            # Integration tests
│
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable template
└── README.md                   # This file
```

## Prerequisites

- Python 3.11 or higher
- PostgreSQL 15+ with PostGIS extension
- pip or poetry for dependency management

## Setup

### 1. Create Virtual Environment

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 4. Setup Database

```bash
# Create PostgreSQL database with PostGIS
createdb aaspaas_dev
psql -d aaspaas_dev -c "CREATE EXTENSION IF NOT EXISTS postgis;"

# Run migrations
alembic upgrade head
```

### 5. Run Development Server

```bash
uvicorn app.main:app --reload
```

Backend will be available at `http://localhost:8000`  
API documentation at `http://localhost:8000/docs`

## Development

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history

# View current version
alembic current
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/unit/test_auth.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code
black app/ tests/

# Lint code
flake8 app/ tests/

# Type checking
mypy app/
```

## Environment Variables

Required environment variables (see `.env.example`):

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/aaspaas_dev

# JWT Authentication
JWT_SECRET=your-secret-key
JWT_REFRESH_SECRET=your-refresh-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Storage (S3/Cloudinary)
STORAGE_TYPE=s3
STORAGE_BUCKET=your-bucket-name
STORAGE_ACCESS_KEY=your-access-key
STORAGE_SECRET_KEY=your-secret-key

# Maps
GOOGLE_MAPS_API_KEY=your-api-key

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@aaspaas.com
SMTP_PASSWORD=your-password

# Firebase (Push Notifications)
FIREBASE_CREDENTIALS_PATH=path/to/firebase-credentials.json

# Application
ENVIRONMENT=development
DEBUG=True
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
```

## API Documentation

Once the server is running:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Project Status

**Current Phase**: Phase 0 - Foundation (Complete)
**Next Phase**: Phase 1 - Backend Foundation

## Architecture

The backend follows a layered architecture:

```
API Layer (FastAPI Routes)
    ↓
Service Layer (Business Logic)
    ↓
Repository Layer (Data Access)
    ↓
ORM Layer (SQLAlchemy)
    ↓
Database (PostgreSQL + PostGIS)
```

## Key Technologies

- **FastAPI** - Modern async web framework
- **SQLAlchemy** - ORM for database operations
- **Alembic** - Database migration tool
- **Pydantic** - Data validation
- **PostgreSQL** - Primary database
- **PostGIS** - Geospatial extension
- **pytest** - Testing framework

## Security Notes

- All passwords hashed with Argon2/bcrypt
- JWT tokens for authentication
- Server-side authorization on all protected endpoints
- Input validation via Pydantic schemas
- SQL injection protection via ORM
- Rate limiting on sensitive endpoints
- Audit logging for admin actions

See `../docs/SECURITY.md` for complete security guidelines.

## Documentation

- [PROJECT_SPEC.md](../PROJECT_SPEC.md) - Complete product specification
- [ARCHITECTURE.md](../docs/ARCHITECTURE.md) - System architecture
- [DATABASE.md](../docs/DATABASE.md) - Database schema
- [API_SPEC.md](../docs/API_SPEC.md) - API endpoints
- [SECURITY.md](../docs/SECURITY.md) - Security guidelines

## License

Proprietary - All rights reserved
