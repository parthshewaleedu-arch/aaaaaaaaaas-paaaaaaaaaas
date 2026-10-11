# Phase 13: Reports, Content Moderation & Platform Administration System

## Overview
Phase 13 delivers the complete Reports, Content Moderation, and Platform Administration infrastructure in alignment with `PROJECT_SPEC.md` (Sections 33–36, 70, 71, 124) and `docs/DATABASE.md` (Sections 18 & 24) and `docs/API_SPEC.md` (Sections 13 & 14).

---

## Deliverables & Architecture

### 1. Database Models (`app/models/`)
- [`BusinessReport`](file:///c:/Users/Acer/Desktop/AAS%20PAAS/aas%20paas/backend/app/models/business_report.py):
  - Primary Key: `id` (UUID).
  - Foreign Keys: `business_id` (cascading), `reported_by` (cascading), `resolved_by` (`SET NULL`).
  - Enums:
    - `BusinessReportReason`: `FAKE_LISTING`, `INCORRECT_INFORMATION`, `CLOSED_BUSINESS`, `INCORRECT_PRICES`, `FRAUD`, `HARASSMENT`, `OTHER`.
    - `BusinessReportStatus`: `PENDING`, `UNDER_REVIEW`, `RESOLVED`, `DISMISSED`.
  - Check Constraints & Indexes: Enforces valid reason and status codes in database; indexes on `business_id`, `reported_by`, `status`.
- [`AuditLog`](file:///c:/Users/Acer/Desktop/AAS%20PAAS/aas%20paas/backend/app/models/audit_log.py):
  - Primary Key: `id` (UUID).
  - Foreign Key: `admin_id` (`users.id`, cascading).
  - Attributes: `action`, `entity_type`, `entity_id`, `old_data` (JSON), `new_data` (JSON), `reason`, `ip_address`, `user_agent`, `created_at`.
  - Purpose: Immutable audit log recording every high-impact admin operation (user suspensions, business verifications, listing status changes, review moderation, and report resolutions).
- Relationships wired into [`Business`](file:///c:/Users/Acer/Desktop/AAS%20PAAS/aas%20paas/backend/app/models/business.py) and exported in [`app/models/__init__.py`](file:///c:/Users/Acer/Desktop/AAS%20PAAS/aas%20paas/backend/app/models/__init__.py).

### 2. Database Migration (`migrations/versions/`)
- [`007_reports_and_audit_logs.py`](file:///c:/Users/Acer/Desktop/AAS%20PAAS/aas%20paas/backend/migrations/versions/007_reports_and_audit_logs.py):
  - Creates PostgreSQL enum types `business_report_reason` and `business_report_status`.
  - Creates table `business_reports` with check constraints and foreign keys.
  - Creates table `audit_logs` with JSONB payloads and indexes on `admin_id`, `action`, `entity_type`, `created_at`.

### 3. Pydantic Schemas (`app/schemas/`)
- [`app/schemas/report.py`](file:///c:/Users/Acer/Desktop/AAS%20PAAS/aas%20paas/backend/app/schemas/report.py):
  - `BusinessReportCreate`: User submission payload with reason validation.
  - `BusinessReportResponse`: Serialized business complaint item.
  - `AdminReportItemResponse`: Polymorphic unified moderation item representing either a business or a review complaint.
  - `AdminReportListResponse`: Paginated response envelope.
  - `ReportResolveRequest`: Admin resolution payload with target status and notes.
- [`app/schemas/admin.py`](file:///c:/Users/Acer/Desktop/AAS%20PAAS/aas%20paas/backend/app/schemas/admin.py):
  - Dashboard Metrics: `AdminStudentMetrics`, `AdminBusinessMetrics`, `AdminReviewMetrics`, `AdminReportMetrics`, `AdminDashboardData`, `AdminDashboardResponse`.
  - User Directory: `AdminUserItemResponse`, `AdminUserListResponse`, `AdminUserStatusUpdateRequest`.
  - Business Management: `AdminBusinessItemResponse`, `AdminBusinessListResponse`, `AdminBusinessVerifyRequest`, `AdminBusinessStatusUpdateRequest`.
  - Review Moderation: `AdminReviewItemResponse`, `AdminReviewListResponse`, `AdminReviewModerateRequest`.
  - Audit Trail: `AdminAuditLogAdminInfo`, `AdminAuditLogItemResponse`, `AdminAuditLogListResponse`.

### 4. Security & Role Dependencies (`app/auth/`)
- [`app/auth/dependencies.py`](file:///c:/Users/Acer/Desktop/AAS%20PAAS/aas%20paas/backend/app/auth/dependencies.py):
  - `get_current_admin_user`: Validates that the active token belongs to a user with `UserRole.ADMIN`, raising `403 Forbidden` otherwise.

### 5. Service Layer (`app/services/`)
- [`ReportService`](file:///c:/Users/Acer/Desktop/AAS%20PAAS/aas%20paas/backend/app/services/report_service.py):
  - `create_business_report`: Business existence verification, prevention of owner self-reporting, creation and persistence.
  - `get_business_report`: Fetch business report with joined business metadata.
  - `list_reports`: Merges and sorts business complaints and review complaints into a unified chronological moderation queue.
  - `resolve_report`: Resolves or dismisses target report, assigns resolver admin ID, records resolution notes, and writes an audit log.
- [`AdminService`](file:///c:/Users/Acer/Desktop/AAS%20PAAS/aas%20paas/backend/app/services/admin_service.py):
  - `record_audit_log`: Persists immutable administrative actions with client IP and user agent tracking.
  - `get_dashboard_metrics`: Aggregates active students, verified students, active and verified businesses, review activity, and pending moderation items.
  - `list_users`: Paginated user accounts filterable by role, status, and email keyword search.
  - `update_user_status`: Transitions user status (e.g. `SUSPENDED`) and records audit log.
  - `list_businesses`: Admin listing directory filterable by status, verification status, and campus.
  - `verify_business`: Handles approval (`VERIFIED`, activates listing) and rejection (`UNVERIFIED`, stores rejection reason) with audit log.
  - `update_business_status`: Suspends, activates, or soft-deletes a business listing with audit log.
  - `list_reviews`: Moderation queue displaying review text, ratings, and attached report counts.
  - `moderate_review`: Supports removing review (soft-deletes review, auto-resolves pending complaints, recalculates business rating) or keeping review (dismisses pending complaints) with audit log.
  - `list_audit_logs`: Paginated audit log retrieval filterable by admin ID, entity type, action, and date range.

### 6. REST API Endpoints (`app/api/v1/endpoints/`)
- **Business Reporting API** (`/api/v1/businesses`):
  - `POST /api/v1/businesses/{id}/report`: File a moderation report against a business listing (authenticated user).
- **Admin Administration API** (`/api/v1/admin`):
  - `GET /api/v1/admin/dashboard`: Platform KPI summary metrics (admin).
  - `GET /api/v1/admin/users`: User management directory with filters (admin).
  - `PATCH /api/v1/admin/users/{id}`: Modify user account lifecycle status (admin).
  - `GET /api/v1/admin/businesses`: Business oversight list with verification filters (admin).
  - `PATCH /api/v1/admin/businesses/{id}/verify`: Approve or reject merchant verification (admin).
  - `PATCH /api/v1/admin/businesses/{id}/status`: Suspend, activate, or remove business listing (admin).
  - `GET /api/v1/admin/reviews`: Review moderation queue with report counts (admin).
  - `PATCH /api/v1/admin/reviews/{id}/moderate`: Keep or remove student review (admin).
  - `GET /api/v1/admin/reports`: Unified moderation complaint inbox (admin).
  - `PATCH /api/v1/admin/reports/{id}`: Resolve or dismiss moderation complaint (admin).
  - `GET /api/v1/admin/audit-logs`: Immutable administration audit trail query (admin).

---

## Test Verification

| Test Suite | Tests | Result |
| :--- | :--- | :--- |
| [`tests/unit/test_report_service.py`](file:///c:/Users/Acer/Desktop/AAS%20PAAS/aas%20paas/backend/tests/unit/test_report_service.py) | 6 | **Passed** |
| [`tests/unit/test_admin_service.py`](file:///c:/Users/Acer/Desktop/AAS%20PAAS/aas%20paas/backend/tests/unit/test_admin_service.py) | 10 | **Passed** |
| [`tests/unit/test_admin_and_reports_api.py`](file:///c:/Users/Acer/Desktop/AAS%20PAAS/aas%20paas/backend/tests/unit/test_admin_and_reports_api.py) | 11 | **Passed** |
| **All Backend Unit Tests** | **164 passed, 1 skipped** | **Passed** |

- Code formatted with `black`.
- Zero linting issues with `flake8 --max-line-length=120`.
