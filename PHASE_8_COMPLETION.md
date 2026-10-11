# Phase 8 Completion: Business Details & Offerings Module

## Overview
Phase 8 implements the **Business Details & Offerings Module** for the AAS PAAS platform, delivering weekly operating hours scheduling with live open/closed status calculation, business service catalog management, and automated price change audit logging for student trust indicators ("Price updated X days ago").

---

## Deliverables & Components

### 1. Database Models & Schema
- **`BusinessHours`** (`app/models/business_hours.py`):
  - Weekly schedule `day_of_week` (0=Sunday to 6=Saturday), `open_time`, `close_time`, `is_closed`.
  - Constraints `ck_business_hours_day` and `ck_business_hours_times`.
  - Day name helper property (`day_name`).
- **`Service`** (`app/models/service.py`):
  - Offerings with `name`, `description`, `price`, `currency` (default 'INR'), `unit` (e.g. 'plate', 'month', 'page'), `is_active`.
  - Cascade relationship with price history log.
- **`ServicePriceHistory`** (`app/models/service_price_history.py`):
  - Audit trail storing `service_id`, `price`, `currency`, `effective_from`, `effective_to`, `changed_by`.
- **`Business` Model Updates** (`app/models/business.py`):
  - Associated `hours` and `services` relationships on `Business`.

### 2. Alembic Migration
- **`migrations/versions/003_business_hours_and_services.py`**:
  - DDL migration creating `business_hours`, `services`, and `service_price_history` tables with indexes, foreign keys, and check constraints.

### 3. Pydantic Validation Schemas
- **`app/schemas/service.py`**:
  - `ServiceCreate`, `ServiceUpdate`, `ServiceResponse`, `ServicePriceHistoryResponse`, `ServiceListResponse`.
  - Exposes `days_since_update` for student trust indicators.
- **`app/schemas/business.py`**:
  - `BusinessHoursItem`, `BusinessHoursCreate`, `BusinessHoursBatchUpdate`, `BusinessHoursResponse`, `BusinessHoursScheduleResponse`.
  - Updated `BusinessResponse` and `BusinessDetailResponse` to include `is_open_now`, `current_status`, and `services`.

### 4. Business Services Logic
- **`ServiceService`** (`app/services/service_service.py`):
  - `create_service`: Creates offering and logs initial price into `ServicePriceHistory`.
  - `update_service`: When price changes, closes previous active record (`effective_to = now`) and appends new active entry.
  - `list_services`: Fetches offerings for a business.
  - `get_service_by_id`, `delete_service`, `get_price_history`.
  - `calculate_days_since_update`: Returns elapsed days from timestamp for UI badges.
- **`BusinessService` Enhancements** (`app/services/business_service.py`):
  - `set_business_hours`: Validates constraints and batch upserts weekly schedule.
  - `get_business_hours`: Retrieves ordered schedule.
  - `calculate_open_status`: Live calculation determining `is_open_now` and status descriptions ("Open until 10:00 PM", "Closed • Opens at 9:00 AM", "Closed • Opens tomorrow at 9:00 AM", with overnight shift support).
  - `enrich_business_details`: Dynamically decorates business models with `is_open_now`, `current_status`, and service `days_since_update`.
  - `list_businesses`: Added `open_now: Optional[bool]` filter parameter.

### 5. API Endpoints
- **Business Hours & Offerings** (`app/api/v1/endpoints/businesses.py`):
  - `GET /api/v1/businesses/{id}/hours` — View operating hours and real-time open status (Public).
  - `PUT /api/v1/businesses/{id}/hours` — Batch update weekly operating hours (Owner / Admin).
  - `GET /api/v1/businesses/{id}/services` — List business service offerings with price freshness indicators (Public).
  - `POST /api/v1/businesses/{id}/services` — Add a new service offering (Owner / Admin).
  - `GET /api/v1/businesses` — Search & list businesses, now supporting `open_now` boolean filter (Public).
- **Service Management & Auditing** (`app/api/v1/endpoints/services.py`):
  - `GET /api/v1/services/{service_id}` — View service details (Public).
  - `PATCH /api/v1/services/{service_id}` — Update service details and price with automated history tracking (Owner / Admin).
  - `DELETE /api/v1/services/{service_id}` — Delete service offering (Owner / Admin).
  - `GET /api/v1/services/{service_id}/price-history` — Retrieve price change audit trail (Public).
- **FastAPI Router Mounting** (`app/main.py`):
  - Mounted `services.router` at `/api/v1/services`.

---

## Verification & Testing
- **Unit Tests Added**:
  - `tests/unit/test_business_hours.py`: Weekly schedule upserts, validation errors, open status calculations (day shifts, overnight shifts, closed days, before open, after close).
  - `tests/unit/test_service_service.py`: Initial price logging, price change interval tracking, non-price updates, days since update calculation, deletion.
  - `tests/unit/test_services_api.py`: Hours endpoints, services endpoints, patch price change, deletion, and price history audit trail.
- **Test Results**:
  - Ran `pytest`: **54 passed, 0 failed** (and 76 live PostgreSQL-dependent integration tests safely skipped).
  - Ran `black --check`: All Phase 8 code formatted according to PEP 8 standards.
  - Ran `flake8`: 0 errors / 0 warnings.
