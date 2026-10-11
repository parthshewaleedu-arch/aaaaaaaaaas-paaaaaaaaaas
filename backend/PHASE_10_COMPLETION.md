# Phase 10: Business Photos Gallery & Student Bookmarks / Favorites System

## Overview
Phase 10 implements the full Business Photo Gallery and Student Bookmarks/Favorites system as specified in `PROJECT_SPEC.md` (Sections 23, 26, 46, 56) and `docs/API_SPEC.md`.

---

## Deliverables & Architecture

### 1. Database Models (`app/models/`)
- [`BusinessPhoto`](file:///c:/Users/Acer/Desktop/AAS%20PAAS/aas%20paas/backend/app/models/business_photo.py):
  - Primary Key: `id` (UUID).
  - Foreign Keys: `business_id` (cascading), `uploaded_by` (cascading).
  - Enums:
    - `BusinessPhotoUploaderType`: `OWNER`, `STUDENT`, `ADMIN`.
    - `BusinessPhotoStatus`: `ACTIVE`, `REMOVED`, `PENDING_MODERATION`.
  - Properties: `image_url`, `caption`, `is_primary`, `created_at`.
- [`Favorite`](file:///c:/Users/Acer/Desktop/AAS%20PAAS/aas%20paas/backend/app/models/favorite.py):
  - Composite Primary Key: `(user_id, business_id)`.
  - `created_at`: UTC timestamp with timezone.
- Relationships wired into [`Business`](file:///c:/Users/Acer/Desktop/AAS%20PAAS/aas%20paas/backend/app/models/business.py) and [`User`](file:///c:/Users/Acer/Desktop/AAS%20PAAS/aas%20paas/backend/app/models/user.py).

### 2. Pydantic Schemas (`app/schemas/`)
- [`app/schemas/business_photo.py`](file:///c:/Users/Acer/Desktop/AAS%20PAAS/aas%20paas/backend/app/schemas/business_photo.py):
  - `BusinessPhotoBase`, `BusinessPhotoCreate`, `BusinessPhotoResponse`, `BusinessPhotoListResponse`.
- [`app/schemas/favorite.py`](file:///c:/Users/Acer/Desktop/AAS%20PAAS/aas%20paas/backend/app/schemas/favorite.py):
  - `FavoriteItemResponse`, `FavoriteListResponse`, `FavoriteStatusResponse`, `FavoriteActionResponse`.

### 3. Business Logic & Services (`app/services/`)
- [`BusinessPhotoService`](file:///c:/Users/Acer/Desktop/AAS%20PAAS/aas%20paas/backend/app/services/business_photo_service.py):
  - `upload_photo`: Allows owner, student, or admin uploads with role validation. Enforces automatic primary flag handling for first photo.
  - `list_photos`: Public listing with optional status filtering.
  - `set_primary_photo`: Restricts cover assignment to business owners and admins. Ensures exclusivity (demotes previous primary photo).
  - `delete_photo`: Soft-deletes photo (`REMOVED`), permits photo uploader, business owner, or admin.
  - `get_photo_by_id`: Fetches photo by UUID.
- [`FavoriteService`](file:///c:/Users/Acer/Desktop/AAS%20PAAS/aas%20paas/backend/app/services/favorite_service.py):
  - `add_favorite`: Idempotent addition with business existence verification.
  - `remove_favorite`: Clean removal with boolean status response.
  - `is_favorite`: Quick boolean check.
  - `toggle_favorite`: Atomic toggle returning current favorited state.
  - `list_user_favorites`: Paginated list enriched with ratings, primary photo URL, distance (Haversine formula), and live open hours status.
- [`BusinessService`](file:///c:/Users/Acer/Desktop/AAS%20PAAS/aas%20paas/backend/app/services/business_service.py):
  - Enriched business detail representations to query and package active photos.

### 4. REST API Endpoints (`app/api/v1/endpoints/`)
- **Business Photos**:
  - `GET /api/v1/businesses/{id}/photos`: Public gallery listing.
  - `POST /api/v1/businesses/{id}/photos`: Upload photo (Owner, Student, Admin).
  - `PATCH /api/v1/businesses/{id}/photos/{photo_id}/primary`: Designate primary photo.
  - `DELETE /api/v1/businesses/{id}/photos/{photo_id}`: Remove photo.
- **Favorites & Bookmarks**:
  - `GET /api/v1/businesses/{id}/is-favorite`: Check favorite status.
  - `POST /api/v1/businesses/{id}/favorite`: Toggle favorite status.
  - `GET /api/v1/students/me/favorites`: Paginated bookmarks with distance and live open status.
  - `POST /api/v1/students/me/favorites/{business_id}`: Add favorite.
  - `DELETE /api/v1/students/me/favorites/{business_id}`: Remove favorite.

### 5. Database Migration
- [`migrations/versions/005_business_photos_and_favorites.py`](file:///c:/Users/Acer/Desktop/AAS%20PAAS/aas%20paas/backend/migrations/versions/005_business_photos_and_favorites.py):
  - DDL for `business_photos` table with enum types.
  - DDL for `favorites` table with composite primary key.
  - Partial index `idx_business_photos_primary` on `(business_id)` where `is_primary = TRUE`.

---

## Test Verification

| Test Suite | Tests Passed | Status |
| :--- | :--- | :--- |
| `tests/unit/test_business_photo_service.py` | 9 | Passed |
| `tests/unit/test_favorite_service.py` | 8 | Passed |
| `tests/unit/test_photos_and_favorites_api.py` | 9 | Passed |
| **All Unit Tests (`tests/unit`)** | **97 passed, 1 skipped** | **Passed** |

Linting and code style:
- `black app tests migrations` passed.
- `flake8 --max-line-length=120` passed with 0 errors.
