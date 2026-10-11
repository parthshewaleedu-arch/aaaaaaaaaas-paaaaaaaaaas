# Phase 12: Maps, Geospatial Exploration & Campus Navigation System

## Overview
Phase 12 implements the interactive campus discovery, geospatial viewport/radius pin exploration, and pedestrian walking navigation routing engine in strict alignment with `PROJECT_SPEC.md` (Sections 27 & 124), `docs/DATABASE.md` (Sections 3 & 6), and `docs/API_SPEC.md` (Sections 7 & 8).

---

## Deliverables & Architecture

### 1. Data Schemas (`app/schemas/`)
- [`app/schemas/campus.py`](file:///c:/Users/Acer/Desktop/AAS%20PAAS/aas%20paas/backend/app/schemas/campus.py):
  - `CampusCollegeInfo`: Nested college metadata (`id`, `name`, `short_name`, `city`, `state`).
  - `CampusBase`, `CampusResponse`: Comprehensive campus response including coordinates (`latitude`, `longitude`, `radius_meters`) and dynamic active business count.
  - `CampusListResponse`: Paginated campus list wrapper.
- [`app/schemas/map.py`](file:///c:/Users/Acer/Desktop/AAS%20PAAS/aas%20paas/backend/app/schemas/map.py):
  - `BoundingBox`: Viewport coordinate box (`min_latitude`, `min_longitude`, `max_latitude`, `max_longitude`).
  - `MapMarkerResponse`: High-performance, lightweight map pin with coordinates, distance (meters), category badge, average rating, price level, student discount flag, primary photo URL, and live opening status.
  - `MapMarkersListResponse`: List wrapper for markers query with count.
  - `CampusMapResponse`: Campus center coordinates, dynamic discovery bounding box, radius, and list of all active campus business markers.
  - `DirectionsResponse`: Walking directions metadata including distance in meters & km, walking time estimate in minutes, compass bearing degrees (0–360°), 8-point cardinal abbreviation, and universal Google Maps walking navigation deep link URL.

### 2. Service Layer (`app/services/`)
- [`CampusService`](file:///c:/Users/Acer/Desktop/AAS%20PAAS/aas%20paas/backend/app/services/campus_service.py):
  - `list_campuses`: Retrieves campuses filtered by college or keyword, joined with college details and counting active businesses.
  - `get_campus_by_id`: Fetches single campus details with attached college info.
  - `get_campus_map_data`: Calculates geographic bounding box for campus perimeter and gathers all active businesses sorted by proximity to campus center.
- [`MapService`](file:///c:/Users/Acer/Desktop/AAS%20PAAS/aas%20paas/backend/app/services/map_service.py):
  - `calculate_distance`: Exact great-circle distance (meters) using the Haversine formula.
  - `calculate_bearing`: Computes forward azimuth compass bearing (0–360°) and resolves into 8-point cardinal direction (`N`, `NE`, `E`, `SE`, `S`, `SW`, `W`, `NW`).
  - `calculate_walking_minutes`: Walking duration estimate assuming standard pedestrian pace (4.8 km/h or 80 m/min).
  - `build_marker`: Maps business entity into optimized marker pin, loading primary photo, rating, category, and real-time open status via `BusinessService.is_open_now`.
  - `get_markers_in_bounding_box`: Viewport geospatial query for web and mobile map canvases, supporting category and student discount filters.
  - `get_markers_within_radius`: Circular radius search around coordinates with bounding box pre-filtering.
  - `get_directions`: Computes distance, walking time, bearing, and deep link URL (`https://www.google.com/maps/dir/?api=1&origin=...&destination=...&travelmode=walking`).

### 3. REST API Endpoints (`app/api/v1/endpoints/`)
- **Campuses API** (`/api/v1/campuses`):
  - `GET /api/v1/campuses`: List campuses with college metadata and business count (public).
  - `GET /api/v1/campuses/{id}`: Detailed campus information (public).
  - `GET /api/v1/campuses/{id}/map`: Campus map center, bounding box, and active business pins (public).
- **Map Exploration API** (`/api/v1/map`):
  - `GET /api/v1/map/markers`: Viewport bounding box (`min_lat`, `min_lng`, `max_lat`, `max_lng`) or circular radius query (`lat`, `lng`, `radius_meters`) with category & discount filters (public).
  - `GET /api/v1/map/campuses`: Campus geographic points, radius perimeter, and active business counts for map layer overlay rendering (public).
- **Walking Directions API** (`/api/v1/businesses`):
  - `GET /api/v1/businesses/{id}/directions`: Walking navigation calculation from user coordinates to destination business (public).

---

## Test Verification

| Test Suite | Tests | Result |
| :--- | :--- | :--- |
| [`tests/unit/test_campus_service.py`](file:///c:/Users/Acer/Desktop/AAS%20PAAS/aas%20paas/backend/tests/unit/test_campus_service.py) | 4 | **Passed** |
| [`tests/unit/test_map_service.py`](file:///c:/Users/Acer/Desktop/AAS%20PAAS/aas%20paas/backend/tests/unit/test_map_service.py) | 7 | **Passed** |
| [`tests/unit/test_maps_and_campuses_api.py`](file:///c:/Users/Acer/Desktop/AAS%20PAAS/aas%20paas/backend/tests/unit/test_maps_and_campuses_api.py) | 8 | **Passed** |
| **All Backend Unit Tests** | **137 passed, 1 skipped** | **Passed** |

- Code formatted with `black`.
- Zero linting issues with `flake8 --max-line-length=120`.
