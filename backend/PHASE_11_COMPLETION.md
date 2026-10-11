# Phase 11: Student Offers, Discounts & Merchant Redemption Engine

## Overview
Phase 11 implements the complete Student Offers, Promotions, and Merchant Redemption verification system in alignment with `PROJECT_SPEC.md` (Sections 24, 25, 32, 57, 58, 69) and `docs/DATABASE.md` (Sections 20 & 21).

---

## Deliverables & Architecture

### 1. Database Layer (`app/models/`)
- [`Offer`](file:///c:/Users/Acer/Desktop/AAS%20PAAS/aas%20paas/backend/app/models/offer.py):
  - Primary Key: `id` (UUID).
  - Foreign Key: `business_id` (cascading).
  - Fields: `title`, `description`, `discount_type` (`PERCENTAGE`, `FIXED_AMOUNT`, `SERVICE_DISCOUNT`), `discount_value`, `terms_conditions`, `valid_from`, `valid_until`, `max_redemptions`, `redemption_count`, `status` (`DRAFT`, `ACTIVE`, `PAUSED`, `EXPIRED`, `CANCELLED`), `created_at`, `updated_at`.
  - Database Constraints: check positive discount, valid until > valid from, non-negative redemption count, positive max redemptions.
  - Property: `remaining_redemptions` computed dynamically.
- [`OfferRedemption`](file:///c:/Users/Acer/Desktop/AAS%20PAAS/aas%20paas/backend/app/models/offer_redemption.py):
  - Primary Key: `id` (UUID).
  - Foreign Keys: `offer_id` (cascading), `user_id` (cascading).
  - Verification & Status: Unique uppercase verification code (e.g. `OFR-ABC123`), `status` (`PENDING`, `COMPLETED`, `CANCELLED`, `EXPIRED`), `expires_at`, `redeemed_at`.
- Relationships integrated with [`Business`](file:///c:/Users/Acer/Desktop/AAS%20PAAS/aas%20paas/backend/app/models/business.py) and [`User`](file:///c:/Users/Acer/Desktop/AAS%20PAAS/aas%20paas/backend/app/models/user.py).

### 2. Validation & Serialization Layer (`app/schemas/`)
- [`app/schemas/offer.py`](file:///c:/Users/Acer/Desktop/AAS%20PAAS/aas%20paas/backend/app/schemas/offer.py):
  - `OfferBase`, `OfferCreate`, `OfferUpdate`, `OfferResponse`, `OfferListResponse`, `OfferBusinessInfo`.
  - `OfferRedeemResponse`, `OfferRedemptionResponse`, `OfferRedemptionListResponse`.
  - `OfferRedemptionValidateRequest`, `OfferRedemptionValidateResponse`.

### 3. Service Layer (`app/services/`)
- [`OfferService`](file:///c:/Users/Acer/Desktop/AAS%20PAAS/aas%20paas/backend/app/services/offer_service.py):
  - `create_offer`: Business ownership / admin permission checks, date validations.
  - `get_offer`: Public visibility for active offers; owner/admin access to non-active drafts.
  - `list_offers`: Filters by campus, business, category, keyword, and active validity window.
  - `update_offer`: Granular property updates with date check integrity.
  - `delete_or_cancel_offer`: Soft-cancellation to `CANCELLED` status preserving redemption history.
  - `redeem_offer`: Restricts redemptions to verified students (`VerificationStatus.VERIFIED`), checks max caps, generates unique codes, prevents uncompleted duplicate pending spam.
  - `validate_redemption`: Merchant verification route, checks business match, validates expiration, marks `COMPLETED`, and returns privacy-masked student display details.
  - `list_user_redemptions`: History of student redemption codes and statuses.
  - `list_business_offers`: Business offers list with owner/admin state visibility.

### 4. REST API Endpoints (`app/api/v1/endpoints/`)
- **Offers API** (`/api/v1/offers`):
  - `GET /api/v1/offers`: List active offers (public)
  - `GET /api/v1/offers/my-redemptions`: Current student redemptions (student)
  - `GET /api/v1/offers/{id}`: Offer details (public)
  - `PATCH /api/v1/offers/{id}`: Update offer (owner/admin)
  - `DELETE /api/v1/offers/{id}`: Cancel offer (owner/admin)
  - `POST /api/v1/offers/{id}/redeem`: Redeem offer (verified student)
- **Business Promotions API** (`/api/v1/businesses`):
  - `POST /api/v1/businesses/{id}/offers`: Create offer (owner/admin)
  - `GET /api/v1/businesses/{id}/offers`: List business offers (public)
  - `POST /api/v1/businesses/{id}/offers/validate`: Merchant validate code (owner/admin)

### 5. Database Migration
- [`migrations/versions/006_offers_and_redemptions.py`](file:///c:/Users/Acer/Desktop/AAS%20PAAS/aas%20paas/backend/migrations/versions/006_offers_and_redemptions.py):
  - Creates `offer_discount_type`, `offer_status`, `offer_redemption_status` PostgreSQL enum types.
  - Creates `offers` table with check constraints and foreign keys.
  - Creates `offer_redemptions` table with unique verification code constraint and indexes.

---

## Test Verification

| Test Suite | Tests | Result |
| :--- | :--- | :--- |
| [`tests/unit/test_offer_service.py`](file:///c:/Users/Acer/Desktop/AAS%20PAAS/aas%20paas/backend/tests/unit/test_offer_service.py) | 12 | **Passed** |
| [`tests/unit/test_offers_api.py`](file:///c:/Users/Acer/Desktop/AAS%20PAAS/aas%20paas/backend/tests/unit/test_offers_api.py) | 9 | **Passed** |
| **All Backend Unit Tests** | **118 passed, 1 skipped** | **Passed** |

- Code formatted with `black`.
- Zero linting issues with `flake8 --max-line-length=120`.
