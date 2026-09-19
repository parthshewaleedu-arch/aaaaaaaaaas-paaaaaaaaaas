# AAS PAAS - API Specification

**Document Version:** 1.0  
**Last Updated:** 2026-09-20  
**Status:** Foundation - Pre-implementation API specification

---

## Table of Contents

1. [API Overview](#api-overview)
2. [Authentication](#authentication)
3. [Response Format](#response-format)
4. [Error Handling](#error-handling)
5. [Pagination](#pagination)
6. [Authentication Endpoints](#authentication-endpoints)
7. [Student Endpoints](#student-endpoints)
8. [College Endpoints](#college-endpoints)
9. [Business Endpoints](#business-endpoints)
10. [Service Endpoints](#service-endpoints)
11. [Review Endpoints](#review-endpoints)
12. [Offer Endpoints](#offer-endpoints)
13. [Report Endpoints](#report-endpoints)
14. [Admin Endpoints](#admin-endpoints)

---

## API Overview

**Base URL**: `/api/v1`

**Protocol**: HTTPS (production), HTTP (development)

**Data Format**: JSON

**Character Encoding**: UTF-8

**API Style**: RESTful

### General Principles

1. **Versioning**: All endpoints under `/api/v1/` namespace
2. **Idempotency**: GET, PUT, DELETE are idempotent; POST is not
3. **HTTP Methods**:
   - `GET`: Retrieve resources
   - `POST`: Create resources
   - `PUT`: Update entire resource (rarely used)
   - `PATCH`: Partial update
   - `DELETE`: Remove resource
4. **Status Codes**: Standard HTTP status codes
5. **Authentication**: JWT Bearer tokens in Authorization header
6. **Rate Limiting**: Applied per endpoint basis

---

## Authentication

### Request Headers

**Required for protected endpoints:**

```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Optional:**

```http
X-Request-ID: <unique-request-id>
```

### Authentication Flow

1. User registers or logs in
2. Server returns access token (30 min) + refresh token (7 days)
3. Client includes access token in subsequent requests
4. Before expiry, client uses refresh token to get new access token
5. Refresh token rotation: each refresh returns new tokens

### Token Storage

- **Mobile**: Secure storage (Flutter Secure Storage)
- **Admin Panel**: httpOnly cookies

---

## Response Format

### Success Response

```json
{
  "success": true,
  "data": {
    // Resource data or array of resources
  },
  "message": "Optional success message",
  "meta": {
    // Optional metadata (pagination, etc.)
  }
}
```

### Error Response

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      // Optional additional error details
    }
  }
}
```

### Common Error Codes

- `VALIDATION_ERROR` - Invalid request data
- `AUTHENTICATION_REQUIRED` - Missing or invalid token
- `AUTHORIZATION_FAILED` - Insufficient permissions
- `RESOURCE_NOT_FOUND` - Requested resource doesn't exist
- `RESOURCE_CONFLICT` - Resource already exists
- `RATE_LIMIT_EXCEEDED` - Too many requests
- `SERVER_ERROR` - Internal server error

---

## Error Handling

### HTTP Status Codes

- `200 OK` - Successful GET, PATCH
- `201 Created` - Successful POST creating resource
- `204 No Content` - Successful DELETE
- `400 Bad Request` - Validation error
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Authorization failed
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource conflict
- `422 Unprocessable Entity` - Semantic errors
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

### Validation Errors

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": {
      "email": ["Invalid email format"],
      "password": ["Password must be at least 8 characters"]
    }
  }
}
```

---

## Pagination

### Query Parameters

```
?page=1&page_size=20
```

- `page`: Page number (1-indexed, default: 1)
- `page_size`: Items per page (default: 20, max: 100)

### Paginated Response

```json
{
  "success": true,
  "data": [...],
  "meta": {
    "page": 1,
    "page_size": 20,
    "total_items": 156,
    "total_pages": 8,
    "has_next": true,
    "has_prev": false
  }
}
```

---

## Authentication Endpoints

### Register User

**POST** `/api/v1/auth/register`

Create a new user account.

**Request Body:**
```json
{
  "email": "student@mitaoe.ac.in",
  "password": "SecurePass123!",
  "role": "STUDENT",
  "full_name": "Rahul Sharma"
}
```

**Response:** `201 Created`
```json
{
  "success": true,
  "data": {
    "user_id": "uuid",
    "email": "student@mitaoe.ac.in",
    "role": "STUDENT",
    "is_email_verified": false,
    "created_at": "2026-09-20T10:30:00Z"
  },
  "message": "Registration successful. Please verify your email."
}
```

---

### Login

**POST** `/api/v1/auth/login`

Authenticate user and receive tokens.

**Request Body:**
```json
{
  "email": "student@mitaoe.ac.in",
  "password": "SecurePass123!"
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "Bearer",
    "expires_in": 1800,
    "user": {
      "id": "uuid",
      "email": "student@mitaoe.ac.in",
      "role": "STUDENT",
      "is_email_verified": true
    }
  }
}
```

---

### Refresh Token

**POST** `/api/v1/auth/refresh`

Get new access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "Bearer",
    "expires_in": 1800
  }
}
```

---

### Verify Email

**POST** `/api/v1/auth/verify-email`

Verify email address using token sent via email.

**Request Body:**
```json
{
  "token": "verification_token_from_email"
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "is_verified": true,
    "verified_at": "2026-09-20T10:35:00Z"
  },
  "message": "Email verified successfully"
}
```

---

### Get Current User

**GET** `/api/v1/auth/me`

Get authenticated user's information.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "email": "student@mitaoe.ac.in",
    "role": "STUDENT",
    "is_email_verified": true,
    "created_at": "2026-09-20T10:30:00Z"
  }
}
```

---

## Student Endpoints

### Verify College Email

**POST** `/api/v1/students/verify-college-email`

Request college email verification.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "college_id": "uuid",
  "college_email": "student@mitaoe.ac.in"
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Verification email sent to student@mitaoe.ac.in"
}
```

---

### Confirm College Email

**POST** `/api/v1/students/confirm-college-email`

Confirm college email with verification code.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "token": "verification_code_from_email"
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "verification_status": "VERIFIED",
    "verified_at": "2026-09-20T10:40:00Z"
  },
  "message": "College email verified successfully"
}
```

---

### Get Student Profile

**GET** `/api/v1/students/me`

Get current student's profile.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "user_id": "uuid",
    "college": {
      "id": "uuid",
      "name": "MIT Academy of Engineering",
      "short_name": "MIT AOE"
    },
    "campus": {
      "id": "uuid",
      "name": "Alandi Campus"
    },
    "full_name": "Rahul Sharma",
    "profile_photo_url": "https://storage.../photo.jpg",
    "department": "Computer Engineering",
    "year": 3,
    "verification_status": "VERIFIED",
    "verified_at": "2026-09-20T10:40:00Z"
  }
}
```

---

### Update Student Profile

**PATCH** `/api/v1/students/me`

Update student profile information.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "full_name": "Rahul Kumar Sharma",
  "department": "Computer Engineering",
  "year": 3
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    // Updated student profile
  },
  "message": "Profile updated successfully"
}
```

---

### Get Favorites

**GET** `/api/v1/students/me/favorites`

Get student's saved businesses.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `page` (optional): Page number
- `page_size` (optional): Items per page

**Response:** `200 OK`
```json
{
  "success": true,
  "data": [
    {
      "business_id": "uuid",
      "business_name": "Sharma Mess",
      "rating": 4.3,
      "distance_meters": 450,
      "saved_at": "2026-09-15T14:20:00Z"
    }
  ],
  "meta": {
    // Pagination metadata
  }
}
```

---

### Add Favorite

**POST** `/api/v1/students/me/favorites/{business_id}`

Save a business to favorites.

**Headers:** `Authorization: Bearer <token>`

**Response:** `201 Created`
```json
{
  "success": true,
  "message": "Business added to favorites"
}
```

---

### Remove Favorite

**DELETE** `/api/v1/students/me/favorites/{business_id}`

Remove business from favorites.

**Headers:** `Authorization: Bearer <token>`

**Response:** `204 No Content`

---

## College Endpoints

### List Colleges

**GET** `/api/v1/colleges`

Get list of colleges (public endpoint).

**Query Parameters:**
- `status` (optional): Filter by status (ACTIVE, INACTIVE)
- `search` (optional): Search by name

**Response:** `200 OK`
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "name": "MIT Academy of Engineering",
      "short_name": "MIT AOE",
      "logo_url": "https://storage.../logo.png",
      "website_url": "https://mitaoe.ac.in",
      "status": "ACTIVE"
    }
  ]
}
```

---

### Get College Details

**GET** `/api/v1/colleges/{id}`

Get specific college information.

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "MIT Academy of Engineering",
    "short_name": "MIT AOE",
    "email_domain": "mitaoe.ac.in",
    "website_url": "https://mitaoe.ac.in",
    "logo_url": "https://storage.../logo.png",
    "status": "ACTIVE",
    "campuses": [
      {
        "id": "uuid",
        "name": "Alandi Campus",
        "address": "Alandi, Pune, Maharashtra"
      }
    ]
  }
}
```

---

## Business Endpoints

### List Businesses

**GET** `/api/v1/businesses`

Search and filter businesses (public endpoint).

**Query Parameters:**
- `campus_id` (optional): Filter by campus
- `category_id` (optional): Filter by category
- `latitude` & `longitude` (optional): User location for distance calculation
- `max_distance` (optional): Maximum distance in meters (default: 5000)
- `min_rating` (optional): Minimum average rating (1-5)
- `price_level` (optional): Price level filter (₹, ₹₹, ₹₹₹, ₹₹₹₹)
- `open_now` (optional): Filter for currently open businesses (true/false)
- `student_discount` (optional): Filter for student discounts (true/false)
- `verified_only` (optional): Only verified businesses (true/false)
- `search` (optional): Search query
- `sort` (optional): Sort order (relevance, distance, rating, newest)
- `page` (optional): Page number
- `page_size` (optional): Items per page

**Response:** `200 OK`
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "name": "Sharma Mess",
      "description": "Homestyle vegetarian meals",
      "categories": ["Mess", "Food"],
      "address": "Near MIT AOE Gate 2",
      "latitude": 18.7830,
      "longitude": 73.9375,
      "distance_meters": 450,
      "phone": "+91 98765 43210",
      "verification_status": "VERIFIED",
      "average_rating": 4.3,
      "review_count": 287,
      "price_level": "₹",
      "student_discount": true,
      "is_open_now": true,
      "primary_photo_url": "https://storage.../photo.jpg"
    }
  ],
  "meta": {
    "page": 1,
    "page_size": 20,
    "total_items": 156,
    "total_pages": 8
  }
}
```

---

### Get Business Details

**GET** `/api/v1/businesses/{id}`

Get detailed business information (public endpoint).

**Query Parameters:**
- `latitude` & `longitude` (optional): For distance calculation

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "Sharma Mess",
    "description": "Homestyle vegetarian meals served with love",
    "categories": [
      {"id": "uuid", "name": "Mess"},
      {"id": "uuid", "name": "Food"}
    ],
    "address": "Shop No. 5, Near MIT AOE Gate 2, Alandi",
    "latitude": 18.7830,
    "longitude": 73.9375,
    "distance_meters": 450,
    "phone": "+91 98765 43210",
    "whatsapp": "+91 98765 43210",
    "website_url": null,
    "verification_status": "VERIFIED",
    "verified_at": "2026-08-15T09:00:00Z",
    "average_rating": 4.3,
    "review_count": 287,
    "price_level": "₹",
    "student_discount": true,
    "student_discount_description": "10% off for MIT AOE students",
    "is_open_now": true,
    "hours": [
      {
        "day_of_week": 1,
        "open_time": "07:00",
        "close_time": "22:00",
        "is_closed": false
      }
    ],
    "photos": [
      {
        "id": "uuid",
        "image_url": "https://storage.../photo1.jpg",
        "is_primary": true,
        "uploaded_by_type": "OWNER"
      }
    ],
    "rating_breakdown": {
      "food_quality": 4.4,
      "hygiene": 3.8,
      "quantity": 4.5,
      "value": 4.3,
      "service": 4.1
    },
    "created_at": "2026-07-10T10:00:00Z",
    "updated_at": "2026-09-18T14:30:00Z"
  }
}
```

---

### Create Business (Owner)

**POST** `/api/v1/businesses`

Create new business listing.

**Headers:** `Authorization: Bearer <token>` (Role: OWNER)

**Request Body:**
```json
{
  "campus_id": "uuid",
  "name": "Sharma Mess",
  "description": "Homestyle vegetarian meals",
  "category_ids": ["uuid1", "uuid2"],
  "phone": "+91 98765 43210",
  "whatsapp": "+91 98765 43210",
  "address": "Shop No. 5, Near MIT AOE Gate 2",
  "latitude": 18.7830,
  "longitude": 73.9375,
  "price_level": "₹",
  "student_discount": true,
  "student_discount_description": "10% off for MIT AOE students"
}
```

**Response:** `201 Created`
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "status": "PENDING",
    "verification_status": "UNVERIFIED",
    // ... other business fields
  },
  "message": "Business created successfully. Awaiting admin verification."
}
```

---

### Update Business (Owner)

**PATCH** `/api/v1/businesses/{id}`

Update business information (owner only).

**Headers:** `Authorization: Bearer <token>` (Role: OWNER)

**Request Body:** (partial update)
```json
{
  "description": "Updated description",
  "phone": "+91 98765 43210",
  "student_discount_description": "15% off for MIT AOE students"
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    // Updated business
  },
  "message": "Business updated successfully"
}
```

---

### Submit for Verification (Owner)

**POST** `/api/v1/businesses/{id}/submit-verification`

Submit business for admin verification.

**Headers:** `Authorization: Bearer <token>` (Role: OWNER)

**Request Body:**
```json
{
  "additional_info": "Operational since 2020. FSSAI license number: 12345678901234"
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "verification_status": "PENDING",
    "submitted_at": "2026-09-20T11:00:00Z"
  },
  "message": "Business submitted for verification"
}
```

---

### Get Business Services

**GET** `/api/v1/businesses/{id}/services`

Get services offered by business (public endpoint).

**Response:** `200 OK`
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "name": "Lunch Thali",
      "description": "2 Sabzi, 5 Roti, Rice, Dal",
      "price": 80.00,
      "currency": "INR",
      "unit": "plate",
      "is_active": true,
      "updated_at": "2026-09-15T10:00:00Z",
      "days_since_update": 5
    }
  ]
}
```

---

### Get Business Hours

**GET** `/api/v1/businesses/{id}/hours`

Get business operating hours (public endpoint).

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "is_open_now": true,
    "current_status": "Open until 10:00 PM",
    "hours": [
      {
        "day_of_week": 0,
        "day_name": "Sunday",
        "open_time": "07:00",
        "close_time": "22:00",
        "is_closed": false
      }
      // ... other days
    ]
  }
}
```

---

### Get Business Photos

**GET** `/api/v1/businesses/{id}/photos`

Get business photos (public endpoint).

**Response:** `200 OK`
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "image_url": "https://storage.../photo.jpg",
      "is_primary": true,
      "uploader_type": "OWNER",
      "created_at": "2026-08-20T10:00:00Z"
    }
  ]
}
```

---

## Service Endpoints

### Add Service (Owner)

**POST** `/api/v1/businesses/{business_id}/services`

Add service to business (owner only).

**Headers:** `Authorization: Bearer <token>` (Role: OWNER)

**Request Body:**
```json
{
  "name": "Dinner Thali",
  "description": "3 Sabzi, 6 Roti, Rice, Dal, Sweet",
  "price": 100.00,
  "unit": "plate"
}
```

**Response:** `201 Created`
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "Dinner Thali",
    "price": 100.00,
    "currency": "INR",
    "is_active": true,
    "created_at": "2026-09-20T11:30:00Z"
  },
  "message": "Service added successfully"
}
```

---

### Update Service (Owner)

**PATCH** `/api/v1/services/{service_id}`

Update service information (owner only).

**Headers:** `Authorization: Bearer <token>` (Role: OWNER)

**Request Body:**
```json
{
  "price": 110.00,
  "description": "Updated description"
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    // Updated service
  },
  "message": "Service updated successfully. Price history recorded."
}
```

---

## Review Endpoints

### Get Business Reviews

**GET** `/api/v1/businesses/{id}/reviews`

Get reviews for a business (public endpoint).

**Query Parameters:**
- `sort` (optional): Sort order (newest, highest_rated, lowest_rated, most_helpful)
- `min_rating` (optional): Minimum rating filter (1-5)
- `verification_level` (optional): Filter by verification level
- `page` (optional): Page number
- `page_size` (optional): Items per page

**Response:** `200 OK`
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "user": {
        "display_name": "Verified MIT AOE Student",
        "is_verified_student": true
      },
      "overall_rating": 4,
      "review_text": "Good food and quantity. Dinner gets crowded.",
      "verification_level": "VERIFIED_STUDENT",
      "ratings": [
        {"dimension": "Food Quality", "rating": 5},
        {"dimension": "Hygiene", "rating": 4},
        {"dimension": "Quantity", "rating": 5},
        {"dimension": "Value", "rating": 5},
        {"dimension": "Service", "rating": 4}
      ],
      "photos": [
        {"image_url": "https://storage.../review_photo.jpg"}
      ],
      "helpful_count": 12,
      "has_response": true,
      "response": {
        "response_text": "Thank you for the feedback!",
        "created_at": "2026-09-18T15:00:00Z"
      },
      "created_at": "2026-09-18T14:30:00Z",
      "updated_at": "2026-09-18T14:30:00Z"
    }
  ],
  "meta": {
    "page": 1,
    "page_size": 20,
    "total_items": 287
  }
}
```

---

### Create Review (Student)

**POST** `/api/v1/businesses/{id}/reviews`

Submit review for business (verified student only).

**Headers:** `Authorization: Bearer <token>` (Role: STUDENT)

**Request Body:**
```json
{
  "overall_rating": 4,
  "review_text": "Great food and service!",
  "ratings": [
    {"dimension_id": "uuid", "rating": 5},
    {"dimension_id": "uuid", "rating": 4}
  ],
  "photo_urls": [
    "https://storage.../review_photo.jpg"
  ]
}
```

**Response:** `201 Created`
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "overall_rating": 4,
    "verification_level": "VERIFIED_STUDENT",
    "created_at": "2026-09-20T12:00:00Z"
  },
  "message": "Review submitted successfully"
}
```

---

### Update Review (Student)

**PATCH** `/api/v1/reviews/{id}`

Update own review (student only).

**Headers:** `Authorization: Bearer <token>` (Role: STUDENT)

**Request Body:**
```json
{
  "overall_rating": 5,
  "review_text": "Updated review text",
  "ratings": [
    {"dimension_id": "uuid", "rating": 5}
  ]
}
```

**Response:** `200 OK`

---

### Delete Review (Student)

**DELETE** `/api/v1/reviews/{id}`

Delete own review (student only).

**Headers:** `Authorization: Bearer <token>` (Role: STUDENT)

**Response:** `204 No Content`

---

### Report Review

**POST** `/api/v1/reviews/{id}/report`

Report problematic review.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "reason": "SPAM",
  "description": "This is clearly spam content"
}
```

**Response:** `201 Created`
```json
{
  "success": true,
  "data": {
    "report_id": "uuid",
    "status": "PENDING"
  },
  "message": "Review reported successfully"
}
```

---

### Respond to Review (Owner)

**POST** `/api/v1/reviews/{id}/response`

Business owner responds to review.

**Headers:** `Authorization: Bearer <token>` (Role: OWNER)

**Request Body:**
```json
{
  "response_text": "Thank you for your feedback! We're glad you enjoyed your meal."
}
```

**Response:** `201 Created`

---

## Offer Endpoints

### List Offers

**GET** `/api/v1/offers`

Get active offers (public endpoint).

**Query Parameters:**
- `campus_id` (optional): Filter by campus
- `business_id` (optional): Filter by business
- `category_id` (optional): Filter by category

**Response:** `200 OK`
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "business": {
        "id": "uuid",
        "name": "Sharma Mess"
      },
      "title": "Student Lunch Special",
      "description": "15% off on lunch thali",
      "discount_type": "PERCENTAGE",
      "discount_value": 15.00,
      "valid_from": "2026-09-01T00:00:00Z",
      "valid_until": "2026-09-30T23:59:59Z",
      "max_redemptions": 100,
      "remaining_redemptions": 45,
      "status": "ACTIVE"
    }
  ]
}
```

---

### Get Offer Details

**GET** `/api/v1/offers/{id}`

Get specific offer details (public endpoint).

**Response:** `200 OK`

---

### Redeem Offer (Student)

**POST** `/api/v1/offers/{id}/redeem`

Redeem an offer (verified student only).

**Headers:** `Authorization: Bearer <token>` (Role: STUDENT)

**Response:** `201 Created`
```json
{
  "success": true,
  "data": {
    "redemption_id": "uuid",
    "verification_code": "ABCD1234",
    "expires_at": "2026-09-20T13:00:00Z"
  },
  "message": "Offer redeemed. Show verification code to merchant."
}
```

---

## Report Endpoints

### Report Business

**POST** `/api/v1/businesses/{id}/report`

Report problematic business.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "reason": "INCORRECT_INFORMATION",
  "description": "Listed prices are outdated"
}
```

**Response:** `201 Created`

---

## Admin Endpoints

All admin endpoints require `Authorization: Bearer <token>` with `ADMIN` role.

### Dashboard

**GET** `/api/v1/admin/dashboard`

Get admin dashboard metrics.

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "students": {
      "total": 523,
      "verified": 487,
      "pending_verification": 36
    },
    "businesses": {
      "total": 178,
      "active": 156,
      "pending_verification": 22,
      "verified": 142
    },
    "reviews": {
      "total": 1847,
      "this_month": 234
    },
    "reports": {
      "pending_review_reports": 5,
      "pending_business_reports": 2
    }
  }
}
```

---

### Manage Users

**GET** `/api/v1/admin/users`

List all users with filters.

**Query Parameters:**
- `role` (optional): Filter by role
- `status` (optional): Filter by status
- `search` (optional): Search query
- `page`, `page_size`

**Response:** `200 OK`

---

**PATCH** `/api/v1/admin/users/{id}`

Update user status (suspend, activate, etc.).

**Request Body:**
```json
{
  "status": "SUSPENDED",
  "reason": "Violation of community guidelines"
}
```

**Response:** `200 OK`

---

### Manage Businesses

**GET** `/api/v1/admin/businesses`

List all businesses for admin review.

**Query Parameters:**
- `status` (optional)
- `verification_status` (optional)
- `campus_id` (optional)
- `search` (optional)

**Response:** `200 OK`

---

**PATCH** `/api/v1/admin/businesses/{id}/verify`

Approve or reject business verification.

**Request Body:**
```json
{
  "action": "APPROVE",
  "reason": "All documents verified"
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "verification_status": "VERIFIED",
    "verified_at": "2026-09-20T12:30:00Z"
  },
  "message": "Business verified successfully"
}
```

---

**PATCH** `/api/v1/admin/businesses/{id}/status`

Change business status (suspend, activate, remove).

**Request Body:**
```json
{
  "status": "SUSPENDED",
  "reason": "Multiple reports of fake information"
}
```

**Response:** `200 OK`

---

### Manage Reviews

**GET** `/api/v1/admin/reviews`

List all reviews for moderation.

**Query Parameters:**
- `status` (optional)
- `business_id` (optional)
- `reported_only` (optional): Only show reported reviews

**Response:** `200 OK`

---

**PATCH** `/api/v1/admin/reviews/{id}/moderate`

Moderate review (keep, remove).

**Request Body:**
```json
{
  "action": "REMOVE",
  "reason": "Spam content"
}
```

**Response:** `200 OK`

---

### Manage Reports

**GET** `/api/v1/admin/reports`

Get all reports (reviews and businesses).

**Query Parameters:**
- `type` (optional): review, business
- `status` (optional)

**Response:** `200 OK`

---

**PATCH** `/api/v1/admin/reports/{id}`

Resolve report.

**Request Body:**
```json
{
  "status": "RESOLVED",
  "resolution_notes": "Reviewed and took appropriate action"
}
```

**Response:** `200 OK`

---

### Audit Logs

**GET** `/api/v1/admin/audit-logs`

View admin action audit trail.

**Query Parameters:**
- `admin_id` (optional)
- `entity_type` (optional)
- `action` (optional)
- `from_date`, `to_date` (optional)
- `page`, `page_size`

**Response:** `200 OK`
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "admin": {
        "id": "uuid",
        "email": "admin@aaspaas.com"
      },
      "action": "VERIFY_BUSINESS",
      "entity_type": "business",
      "entity_id": "uuid",
      "reason": "All documents verified",
      "created_at": "2026-09-20T12:30:00Z"
    }
  ],
  "meta": {
    // Pagination
  }
}
```

---

## Rate Limiting

Default rate limits (per IP address):

- **Authentication**: 5 requests per 15 minutes
- **Registration**: 3 requests per hour
- **Review Creation**: 10 requests per day per user
- **General API**: 100 requests per minute

Rate limit headers included in response:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1632147600
```

When rate limit exceeded:
```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please try again later.",
    "details": {
      "retry_after": 60
    }
  }
}
```

---

## Versioning Strategy

- Current version: `v1`
- Breaking changes require new version
- Non-breaking changes added to existing version
- Deprecated endpoints announced 3 months before removal
- Old versions supported for minimum 6 months after new version release

---

## Testing Endpoints

Use provided test accounts and test mode configuration in development/staging environments. Production endpoints require real authentication.

---

**Next Document**: SECURITY.md - Security requirements and implementation guidelines
