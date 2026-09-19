# AAS PAAS --- Complete Product & Technical Specification

**Document Version:** 1.0\
**Status:** Product foundation / pre-development specification\
**Product:** AAS PAAS\
**Tagline:** Everything You Need, Aas Paas.\
**Primary market:** College students and businesses operating around
college campuses\
**Initial launch strategy:** One-campus pilot, then campus-by-campus
expansion\
**Recommended pilot:** MIT Academy of Engineering (MIT AOE), Alandi,
Pune, Maharashtra\
**Initial geographic scope:** Approximately 3 km around the pilot
campus, adjustable by configuration

------------------------------------------------------------------------

# 1. Executive Summary

AAS PAAS is a college-focused local marketplace and trust platform
designed to help students discover, compare, verify, review, and
eventually transact with businesses and services located around their
college campus.

The problem is not that students cannot find businesses. Google Maps,
Justdial, Instagram, WhatsApp, and other platforms already solve basic
discovery. The actual problem is that students often cannot answer:

-   Is this place actually good?
-   Is the listed price accurate?
-   Is it hygienic?
-   Do students actually use it?
-   Are the photos genuine and recent?
-   Is it open right now?
-   Does it offer a student discount?
-   Can I trust the reviews?
-   Has anyone from my college actually used it?
-   What are the common complaints?
-   How far is it?
-   What services and prices are actually available?
-   What happens if the service is poor or the business information is
    misleading?

AAS PAAS addresses this through a campus-specific ecosystem built
around:

1.  Verified students
2.  Verified businesses
3.  Structured reviews
4.  Transaction/visit verification
5.  Transparent pricing
6.  Student-specific discounts
7.  Business accountability
8.  Location-aware discovery
9.  Moderation and audit trails
10. Eventually, bookings and payment/dispute infrastructure

The product must not become merely another business directory.

The strategic objective is to create a trusted campus marketplace where
the quality of information improves as verified students use the
platform.

------------------------------------------------------------------------

# 2. Core Product Thesis

## 2.1 Problem

Students frequently depend on:

-   Word of mouth
-   WhatsApp groups
-   Seniors
-   Google Maps reviews
-   Instagram pages
-   Random local recommendations
-   Physical exploration

These sources are fragmented and often unreliable.

Businesses also lack a campus-specific channel through which they can:

-   Reach verified students
-   Offer targeted discounts
-   Measure customer acquisition
-   Manage their local presence
-   Publish accurate prices and services
-   Receive structured feedback

## 2.2 Solution

AAS PAAS connects:

**Students + Local Businesses + College/Campus + Trust Infrastructure**

The basic loop:

``` text
Student has a need
        ↓
Searches AAS PAAS
        ↓
Finds nearby businesses
        ↓
Compares price / distance / ratings / reviews
        ↓
Chooses a business
        ↓
Visits / books / transacts
        ↓
Leaves structured feedback
        ↓
Future students receive better information
```

## 2.3 Strategic Differentiation

The app should not compete primarily on the number of listings.

Its differentiation should be:

> Verified campus users + trustworthy local business information +
> structured student reviews + measurable business outcomes.

------------------------------------------------------------------------

# 3. Product Principles

These principles should guide every future feature.

## 3.1 Trust before growth

Do not sacrifice review integrity or verification merely to increase
listing count.

## 3.2 Student-first discovery

The primary interface should answer a student's immediate need quickly.

## 3.3 Transparent information

Prices, opening hours, services, discounts, and review freshness should
be visible.

## 3.4 Business accountability

Businesses can respond to criticism but should not have arbitrary power
to remove legitimate negative reviews.

## 3.5 No pay-to-trust

Businesses may pay for services, promotions, analytics, or customer
acquisition tools, but payment must not automatically create a trust
badge.

## 3.6 Data-driven decisions

Use actual student behavior and verified interactions rather than
assumptions.

## 3.7 Campus density before geographic expansion

A dense, useful campus is more valuable than a huge database with empty
listings.

## 3.8 Build the MVP before complex infrastructure

Do not build escrow, advanced AI, loyalty systems, or sophisticated
recommendation engines before validating the basic marketplace.

------------------------------------------------------------------------

# 4. Target Users

## 4.1 Primary user: Student

Typical needs:

-   Food
-   Mess
-   Cafes
-   Grocery
-   Laundry
-   Salon
-   Gym
-   Medical store
-   Hospital
-   Stationery
-   Printing/Xerox
-   Electronics repair
-   Laptop repair
-   Mobile repair
-   Vehicle repair
-   Hotels
-   Hostels
-   Tutors
-   Coaching
-   Courier
-   Tailors
-   Photography
-   Bakery
-   Transportation
-   Emergency services

Students care about:

-   Price
-   Distance
-   Quality
-   Hygiene
-   Availability
-   Reviews
-   Trust
-   Convenience
-   Student discounts

## 4.2 Secondary user: Business owner

Business owners want:

-   Visibility
-   Student customers
-   Digital presence
-   Accurate listing
-   Offers
-   Analytics
-   Customer feedback
-   Booking
-   Customer acquisition
-   Reputation management

## 4.3 Platform administrator

Responsible for:

-   Platform safety
-   Verification
-   Moderation
-   Business approval
-   User management
-   Reports
-   Disputes
-   Platform configuration
-   Auditability

## 4.4 College administrator

Optional later-stage role.

Responsible only for their college/campus ecosystem.

------------------------------------------------------------------------

# 5. User Roles and Permissions

## 5.1 STUDENT

Can:

-   Register
-   Authenticate
-   Verify college email
-   Create profile
-   Browse businesses
-   Search
-   Filter
-   Sort
-   View business details
-   View prices
-   View services
-   View photos
-   View opening hours
-   View student discounts
-   View reviews
-   Write reviews
-   Upload review photos
-   Edit own reviews
-   Report reviews
-   Report businesses
-   Save businesses
-   Request directions
-   Call businesses
-   Redeem offers
-   View transaction history
-   Raise support requests
-   Manage notifications

Cannot:

-   Approve businesses
-   Remove other users
-   Remove reviews written by other students
-   Change platform settings
-   Access other users' private information

## 5.2 SHOP OWNER

Can:

-   Register
-   Verify identity
-   Create business listing
-   Submit business for verification
-   Edit business information
-   Add services
-   Add prices
-   Add photos
-   Manage hours
-   Create offers
-   Respond to reviews
-   View business analytics
-   View offer performance
-   View customer acquisition data

Cannot:

-   Delete legitimate reviews
-   Modify student reviews
-   Access private student information
-   Approve their own business verification
-   Change platform-wide settings

## 5.3 PLATFORM ADMIN

Can:

-   Manage all users
-   Manage all businesses
-   Manage categories
-   Approve/reject businesses
-   Verify businesses
-   Suspend users
-   Suspend businesses
-   Remove prohibited content
-   Moderate reviews
-   Handle reports
-   Handle disputes
-   Manage offers
-   Manage colleges
-   Manage campus boundaries
-   View transactions
-   Manage platform settings
-   Access audit logs

All sensitive admin actions must generate audit records.

## 5.4 COLLEGE ADMIN

Optional future role.

Can:

-   Manage college information
-   Manage campus information
-   View campus-level reports
-   Flag problematic businesses
-   Manage official campus announcements
-   Coordinate with platform administrators

Cannot:

-   Manage another college
-   Delete platform-wide reviews
-   Access unrelated colleges' student data

------------------------------------------------------------------------

# 6. Product Scope

## 6.1 MVP

### Student

-   Authentication
-   College email verification
-   Student profile
-   College selection
-   Campus selection
-   Home
-   Categories
-   Search
-   Filters
-   Business listing
-   Business details
-   Reviews
-   Ratings
-   Review photos
-   Directions
-   Favorites
-   Student discounts
-   Report business
-   Report review

### Business

-   Owner authentication
-   Owner profile
-   Business registration
-   Business verification workflow
-   Business profile
-   Categories
-   Services
-   Prices
-   Opening hours
-   Photos
-   Student discounts
-   Review responses
-   Basic analytics

### Admin

-   Admin authentication
-   Dashboard
-   User management
-   Business management
-   Business approval
-   Review moderation
-   Report management
-   Category management
-   College management
-   Audit logs

## 6.2 Post-MVP

-   Bookings
-   Transaction tracking
-   Payment processing
-   Refund workflows
-   Dispute resolution
-   AAS PAAS Pass
-   Loyalty
-   Advanced analytics
-   AI search
-   Personalized recommendations
-   College admin
-   Real-time store status
-   Price verification
-   Visit verification
-   Transaction verification
-   Advanced fraud detection
-   Merchant subscriptions
-   Sponsored placements
-   Business CRM

## 6.3 Explicitly not part of first release

-   Escrow
-   Wallet
-   Complex marketplace settlement
-   Full delivery infrastructure
-   Social media feed
-   Large-scale AI recommendation system
-   Multi-city launch
-   Complex loyalty points
-   Automated inspection system

------------------------------------------------------------------------

# 7. Core Feature: Verified Student Identity

AAS PAAS should distinguish between ordinary users and verified
students.

## 7.1 Verification flow

``` text
Student chooses college
        ↓
Student enters college email
        ↓
System validates allowed domain
        ↓
Verification email / OTP
        ↓
Student confirms
        ↓
Student marked VERIFIED
```

## 7.2 Verification statuses

-   UNVERIFIED
-   PENDING
-   VERIFIED
-   SUSPENDED
-   EXPIRED if a future revalidation mechanism is introduced

## 7.3 College domain configuration

College domains must be stored in the database.

Example:

``` text
College: MIT Academy of Engineering
Domain: mitaoe.ac.in
```

Do not hardcode domains in application logic.

## 7.4 Privacy

The public profile should not necessarily expose the student's college
email.

Public display:

``` text
Anonymous Student
🎓 Verified MIT AOE Student
```

Internal system:

``` text
real user identity
college
verification status
```

------------------------------------------------------------------------

# 8. Trust Levels

The platform should use layered trust.

## Level 0 --- Unverified

Basic user without college verification.

## Level 1 --- Verified Student

College email successfully verified.

## Level 2 --- Verified Visit

The platform has reasonable evidence that the student visited or
interacted with the business.

## Level 3 --- Verified Transaction

A transaction was recorded through AAS PAAS.

## Level 4 --- Verified Business

Business identity/location has been verified by the platform.

These levels must never be sold as ordinary advertising badges.

------------------------------------------------------------------------

# 9. Business Categories

Initial categories:

## Food

-   Restaurants
-   Cafes
-   Mess
-   Tiffin
-   Bakery
-   Fast food
-   Street food
-   Juice
-   Desserts

## Health

-   Medical stores
-   Hospitals
-   Clinics
-   Doctors
-   Diagnostics
-   Dental clinics
-   Optical stores

## Personal Care

-   Salons
-   Barbers
-   Beauty services
-   Spas where legally appropriate

## Fitness

-   Gyms
-   Yoga
-   Sports facilities
-   Fitness trainers

## Household

-   Laundry
-   Cleaning
-   Water/RO
-   Repair services

## Education

-   Coaching
-   Tutors
-   Training centers
-   Stationery
-   Printing
-   Xerox
-   Bookstores

## Technology

-   Laptop repair
-   Computer repair
-   Mobile repair
-   Electronics
-   Accessories
-   Internet services

## Shopping

-   Grocery
-   Clothing
-   Footwear
-   General stores
-   Gift stores

## Accommodation

-   Hotels
-   Hostels
-   PGs
-   Lodges

## Mobility

-   Auto services
-   Vehicle repair
-   Bike repair
-   Car repair
-   Rental services
-   Parking

## Professional/Utility

-   Courier
-   Photography
-   Tailors
-   Documentation
-   Banking
-   ATMs

## Emergency

-   Hospitals
-   Emergency clinics
-   Pharmacies
-   Police
-   Fire
-   Ambulance
-   Blood banks

Categories should be database-driven rather than hardcoded.

------------------------------------------------------------------------

# 10. Student Home Screen

The home screen should be task-oriented.

Recommended structure:

``` text
Good evening, [Name]

🎓 [College]

Search:
"What do you need?"

Quick Categories:
Food
Cafe
Laundry
Medical
Gym
Salon
Grocery
Stationery

Student Deals

Popular Near You

Highly Rated by Students

Recently Viewed
```

Bottom navigation:

``` text
Home
Search
Map
Saved
Profile
```

------------------------------------------------------------------------

# 11. Search

Search must support natural user intent even before AI is introduced.

Examples:

-   cheap haircut
-   laundry
-   medical open now
-   gym under 1000
-   cafe with wifi
-   printing
-   mess near hostel
-   laptop repair

Initial implementation:

-   PostgreSQL full-text search
-   Category matching
-   Service matching
-   Location filters
-   Price filters
-   Open/closed status
-   Rating filters

Future:

-   semantic search
-   AI intent classification
-   personalized search

------------------------------------------------------------------------

# 12. Search Filters

## Distance

-   \<500 m
-   \<1 km
-   \<2 km
-   \<5 km

## Rating

-   4+
-   3+
-   Any

## Price

-   ₹
-   ₹₹
-   ₹₹₹
-   ₹₹₹₹

## Availability

-   Open now
-   Open 24/7

## Verification

-   Verified business
-   Verified pricing

## Student benefits

-   Student discount
-   Offer available
-   Bookable

------------------------------------------------------------------------

# 13. Business Detail Page

Required information:

-   Photos
-   Business name
-   Categories
-   Overall rating
-   Review count
-   Verification badge
-   Distance
-   Address
-   Opening status
-   Opening hours
-   Phone
-   WhatsApp if available
-   Directions
-   About
-   Services
-   Prices
-   Price freshness
-   Student discount
-   Offers
-   Ratings by dimension
-   Reviews
-   Business responses
-   Report option

Example:

``` text
Sharma Mess
⭐ 4.3
287 reviews

🟢 Verified Business
📍 450 m
🟢 Open until 10:30 PM

🎓 10% Student Discount

Food Quality       4.4
Hygiene            3.8
Quantity           4.5
Value              4.3
Service            4.1

Last price update:
4 days ago
```

------------------------------------------------------------------------

# 14. Structured Review System

Reviews are central to the product.

A review must contain:

-   Overall rating
-   Category-specific ratings
-   Text
-   Optional photos
-   Verification level
-   Timestamp
-   Helpful count
-   Report capability

Example:

``` text
Anonymous Student
🎓 Verified Student
💳 Verified Transaction

Overall: 4.5

Food: 5
Hygiene: 4
Quantity: 5
Value: 5
Service: 4

Review:
"Good food and quantity. Dinner gets crowded."
```

------------------------------------------------------------------------

# 15. Category-Specific Review Dimensions

The platform should not use the same rating fields for every business.

## Mess

-   Food quality
-   Hygiene
-   Quantity
-   Variety
-   Value
-   Service

## Restaurant

-   Taste
-   Hygiene
-   Quantity
-   Price
-   Service
-   Ambience

## Cafe

-   Taste
-   Price
-   Ambience
-   Seating
-   Wi-Fi
-   Service

## Gym

-   Equipment
-   Cleanliness
-   Crowd
-   Trainers
-   Price
-   Operating hours

## Laundry

-   Cleaning quality
-   Delivery time
-   Pricing
-   Clothing handling
-   Staff

## Salon

-   Service quality
-   Hygiene
-   Pricing
-   Staff
-   Waiting time

Rating dimensions must be configurable in the database.

------------------------------------------------------------------------

# 16. Review Integrity

Businesses must not have arbitrary deletion rights.

Business owners can:

-   Respond
-   Report
-   Request moderation

Platform admins can remove reviews when they violate defined policies.

Reasons:

-   Spam
-   Fake review
-   Harassment
-   Personal information
-   Hate/abuse
-   Irrelevant content
-   Extortion
-   Fraud
-   Other policy violation

Every moderation decision should be auditable.

------------------------------------------------------------------------

# 17. Review Manipulation Detection

Future system should detect:

-   Many reviews from same device
-   Sudden review bursts
-   Duplicate review text
-   Suspicious new accounts
-   Business employees reviewing themselves
-   Review bombing
-   Incentivized fake reviews
-   Reviews without credible interaction signals

Initial version can use rule-based flags.

Future version can use ML.

Do not automatically delete based solely on a model.

Use:

``` text
signal → flag → human/admin review → decision
```

------------------------------------------------------------------------

# 18. Review Freshness

Business information must show freshness.

Examples:

``` text
Price updated 4 days ago
Hours confirmed 2 days ago
Photo uploaded 1 week ago
Most recent review 3 days ago
```

If information becomes stale:

``` text
⚠️ Price not updated in 6 months
```

This is better than pretending old information is current.

------------------------------------------------------------------------

# 19. Business Verification

Business verification should be a workflow.

## Owner submits

-   Business name
-   Phone
-   Address
-   Location
-   Category
-   Photos
-   Identity information where required
-   Business proof where appropriate

## Admin reviews

``` text
Pending
    ↓
Review
    ↓
Approve / Reject / Request More Information
```

Verification states:

-   UNVERIFIED
-   PENDING
-   VERIFIED
-   SUSPENDED
-   REJECTED

------------------------------------------------------------------------

# 20. Business Profile

Fields:

-   Business name
-   Description
-   Categories
-   Address
-   Latitude
-   Longitude
-   Phone
-   WhatsApp
-   Website
-   Opening hours
-   Photos
-   Services
-   Prices
-   Payment methods
-   Student discount
-   Offers
-   Verification state

------------------------------------------------------------------------

# 21. Price Transparency

Every service should have:

-   Service name
-   Price
-   Unit
-   Currency
-   Last updated timestamp

Example:

``` text
Haircut
₹150
Updated 3 days ago
```

Price history should be retained.

This allows future display of price changes.

------------------------------------------------------------------------

# 22. Business Hours

Business hours must support:

-   Day
-   Open time
-   Close time
-   Closed days
-   Multiple periods per day if required

Example:

``` text
Monday
11:00–15:00
19:00–22:30
```

Future feature:

-   Holiday overrides
-   Temporary closures
-   Special hours

------------------------------------------------------------------------

# 23. Business Photos

Photos may be uploaded by:

-   Owner
-   Student
-   Admin

Store metadata:

-   uploader
-   timestamp
-   status
-   primary image flag

Potential future labels:

-   Owner photo
-   Student photo
-   Verified photo

------------------------------------------------------------------------

# 24. Student Discounts

Businesses may optionally provide:

-   Percentage discount
-   Fixed discount
-   Specific service discount
-   Time-limited offer
-   Student-only offer

Example:

``` text
10% OFF
Verified students only
Valid until 30 Oct
```

Terms must be visible.

------------------------------------------------------------------------

# 25. Offer Redemption

Future flow:

``` text
Student opens offer
       ↓
Checks eligibility
       ↓
Redeem
       ↓
Unique redemption record
       ↓
Business validates
       ↓
Redemption marked completed
```

Do not rely solely on screenshots.

Future options:

-   QR redemption
-   One-time codes
-   POS integration
-   Merchant confirmation

------------------------------------------------------------------------

# 26. Favorites

Students can save businesses.

Data:

``` text
user_id
business_id
created_at
```

A student should be able to:

-   Save
-   Unsave
-   View saved businesses

Future:

-   Collections
-   "My favorite cafes"
-   "My mess options"

------------------------------------------------------------------------

# 27. Maps and Location

The app is fundamentally location-aware.

Core capabilities:

-   Current approximate location
-   Campus location
-   Business coordinates
-   Distance
-   Directions
-   Map markers
-   Search within radius

Recommended database:

**PostgreSQL + PostGIS**

This enables efficient geospatial queries.

Example:

``` text
Find all active businesses
within 3 km of selected campus.
```

Do not manually calculate distances in application code for large
datasets.

------------------------------------------------------------------------

# 28. Emergency Mode

Future feature.

Show:

-   Hospitals
-   Medical stores
-   Emergency clinics
-   Ambulance
-   Police
-   Fire station
-   Blood banks
-   Campus security
-   24/7 pharmacies

The app should provide directions and phone actions where available.

Emergency data should be sourced and periodically reviewed.

------------------------------------------------------------------------

# 29. Student Map

Map interface should show:

-   Business markers
-   Category filters
-   Search
-   Distance
-   Open now
-   Selected campus
-   Bottom-sheet business preview

Click marker:

``` text
Business
⭐ Rating
Distance
Open/Closed
[View]
```

------------------------------------------------------------------------

# 30. Owner Dashboard

Dashboard metrics:

-   Profile views
-   Direction requests
-   Calls
-   Offer views
-   Offer redemptions
-   Reviews
-   Rating
-   Search appearances
-   Customer acquisition
-   Booking count later
-   Transaction value later

Example:

``` text
Profile views: 1,284
Direction requests: 321
Offer redemptions: 74
Reviews: 126
Rating: 4.5
```

Do not expose sensitive student identity data.

------------------------------------------------------------------------

# 31. Owner Review Management

Owners can:

-   View reviews
-   Respond
-   Report problematic reviews
-   Monitor trends

Owners cannot:

-   Edit student reviews
-   Delete student reviews
-   Identify anonymous students through platform tools

------------------------------------------------------------------------

# 32. Owner Offer Management

Owner creates:

-   Offer title
-   Description
-   Discount type
-   Discount value
-   Start date
-   End date
-   Eligible services
-   Maximum redemptions

Status:

-   DRAFT
-   ACTIVE
-   PAUSED
-   EXPIRED
-   CANCELLED

------------------------------------------------------------------------

# 33. Admin Dashboard

Metrics:

``` text
Total students
Verified students
Businesses
Verified businesses
Reviews
Reports
Offers
Transactions
Active colleges
Active campuses
```

Pending actions:

``` text
Businesses awaiting approval
Reported reviews
Reported businesses
Verification requests
Support requests
Disputes
```

------------------------------------------------------------------------

# 34. Admin Business Management

Admin can:

-   Search
-   Filter
-   View
-   Approve
-   Reject
-   Suspend
-   Reactivate
-   Remove
-   Verify
-   Request information

Admin actions must be logged.

------------------------------------------------------------------------

# 35. Admin Review Moderation

Admin sees:

-   Review
-   Business
-   User
-   Verification state
-   Report reason
-   Transaction evidence if available
-   Visit evidence if available
-   Account history
-   Previous reports

Possible actions:

-   Keep
-   Remove
-   Escalate
-   Suspend user
-   Flag business

------------------------------------------------------------------------

# 36. Admin Audit Logs

Every high-impact action should create an audit record.

Examples:

``` text
ADMIN A102
Removed review #8291
Reason: Spam

ADMIN A102
Suspended business #221
Reason: Fraud

ADMIN A102
Changed business verification
Pending → Verified
```

Audit logs should be append-oriented and difficult for ordinary admins
to alter.

------------------------------------------------------------------------

# 37. Database Architecture

Recommended:

**PostgreSQL + PostGIS**

## Core tables

``` text
users
students
colleges
campuses
businesses
categories
business_categories
business_hours
business_photos
services
service_price_history
rating_dimensions
reviews
review_ratings
review_photos
review_responses
review_reports
business_reports
favorites
offers
offer_redemptions
transactions
notifications
audit_logs
```

------------------------------------------------------------------------

# 38. Users Table

``` text
users
-----
id UUID PK
email VARCHAR UNIQUE
phone VARCHAR UNIQUE NULL
password_hash VARCHAR NULL
role ENUM
status ENUM
is_email_verified BOOLEAN
is_phone_verified BOOLEAN
created_at TIMESTAMP
updated_at TIMESTAMP
last_login_at TIMESTAMP NULL
```

Roles:

``` text
STUDENT
OWNER
ADMIN
COLLEGE_ADMIN
```

Statuses:

``` text
ACTIVE
SUSPENDED
DELETED
PENDING
```

------------------------------------------------------------------------

# 39. Students Table

``` text
students
--------
id UUID PK
user_id UUID FK
college_id UUID FK
campus_id UUID FK
full_name VARCHAR
profile_photo_url TEXT NULL
student_id VARCHAR NULL
department VARCHAR NULL
year INTEGER NULL
verification_status ENUM
verified_at TIMESTAMP NULL
created_at TIMESTAMP
updated_at TIMESTAMP
```

------------------------------------------------------------------------

# 40. Colleges Table

``` text
colleges
--------
id UUID PK
name VARCHAR
short_name VARCHAR
email_domain VARCHAR
website_url TEXT NULL
logo_url TEXT NULL
status ENUM
created_at TIMESTAMP
updated_at TIMESTAMP
```

------------------------------------------------------------------------

# 41. Campuses Table

``` text
campuses
--------
id UUID PK
college_id UUID FK
name VARCHAR
address TEXT
latitude DECIMAL
longitude DECIMAL
radius_meters INTEGER
created_at TIMESTAMP
updated_at TIMESTAMP
```

------------------------------------------------------------------------

# 42. Businesses Table

``` text
businesses
----------
id UUID PK
owner_id UUID FK
campus_id UUID FK
name VARCHAR
description TEXT
phone VARCHAR
whatsapp VARCHAR NULL
address TEXT
latitude DECIMAL
longitude DECIMAL
status ENUM
verification_status ENUM
price_level ENUM
student_discount BOOLEAN
average_rating DECIMAL
review_count INTEGER
created_at TIMESTAMP
updated_at TIMESTAMP
verified_at TIMESTAMP NULL
```

Derived fields such as average_rating and review_count may be cached for
performance, but reviews remain the source of truth.

------------------------------------------------------------------------

# 43. Categories Table

``` text
categories
----------
id UUID PK
name VARCHAR
slug VARCHAR UNIQUE
icon VARCHAR NULL
parent_id UUID NULL
is_active BOOLEAN
```

Supports hierarchical categories.

------------------------------------------------------------------------

# 44. Business Categories

``` text
business_categories
-------------------
business_id UUID FK
category_id UUID FK

PRIMARY KEY (business_id, category_id)
```

------------------------------------------------------------------------

# 45. Business Hours

``` text
business_hours
--------------
id UUID PK
business_id UUID FK
day_of_week INTEGER
open_time TIME
close_time TIME
is_closed BOOLEAN
```

------------------------------------------------------------------------

# 46. Business Photos

``` text
business_photos
---------------
id UUID PK
business_id UUID FK
uploaded_by UUID FK
image_url TEXT
is_primary BOOLEAN
status ENUM
created_at TIMESTAMP
```

------------------------------------------------------------------------

# 47. Services

``` text
services
--------
id UUID PK
business_id UUID FK
name VARCHAR
description TEXT NULL
price DECIMAL
currency VARCHAR
unit VARCHAR NULL
is_active BOOLEAN
created_at TIMESTAMP
updated_at TIMESTAMP
```

------------------------------------------------------------------------

# 48. Service Price History

``` text
service_price_history
---------------------
id UUID PK
service_id UUID FK
price DECIMAL
effective_from TIMESTAMP
effective_to TIMESTAMP NULL
changed_by UUID FK
```

------------------------------------------------------------------------

# 49. Rating Dimensions

``` text
rating_dimensions
-----------------
id UUID PK
category_id UUID FK
name VARCHAR
```

------------------------------------------------------------------------

# 50. Reviews

``` text
reviews
-------
id UUID PK
business_id UUID FK
user_id UUID FK
overall_rating INTEGER
review_text TEXT
verification_level ENUM
status ENUM
created_at TIMESTAMP
updated_at TIMESTAMP
```

------------------------------------------------------------------------

# 51. Review Ratings

``` text
review_ratings
--------------
id UUID PK
review_id UUID FK
dimension_id UUID FK
rating INTEGER
```

------------------------------------------------------------------------

# 52. Review Photos

``` text
review_photos
-------------
id UUID PK
review_id UUID FK
image_url TEXT
created_at TIMESTAMP
```

------------------------------------------------------------------------

# 53. Review Responses

``` text
review_responses
----------------
id UUID PK
review_id UUID FK
owner_id UUID FK
response_text TEXT
created_at TIMESTAMP
updated_at TIMESTAMP
```

------------------------------------------------------------------------

# 54. Review Reports

``` text
review_reports
--------------
id UUID PK
review_id UUID FK
reported_by UUID FK
reason ENUM
description TEXT NULL
status ENUM
created_at TIMESTAMP
resolved_at TIMESTAMP NULL
resolved_by UUID NULL
```

------------------------------------------------------------------------

# 55. Business Reports

``` text
business_reports
----------------
id UUID PK
business_id UUID FK
reported_by UUID FK
reason ENUM
description TEXT
status ENUM
created_at TIMESTAMP
resolved_at TIMESTAMP NULL
resolved_by UUID NULL
```

------------------------------------------------------------------------

# 56. Favorites

``` text
favorites
---------
user_id UUID FK
business_id UUID FK
created_at TIMESTAMP

PRIMARY KEY (user_id, business_id)
```

------------------------------------------------------------------------

# 57. Offers

``` text
offers
------
id UUID PK
business_id UUID FK
title VARCHAR
description TEXT
discount_type ENUM
discount_value DECIMAL
valid_from TIMESTAMP
valid_until TIMESTAMP
max_redemptions INTEGER NULL
redemption_count INTEGER
status ENUM
created_at TIMESTAMP
updated_at TIMESTAMP
```

------------------------------------------------------------------------

# 58. Offer Redemptions

``` text
offer_redemptions
-----------------
id UUID PK
offer_id UUID FK
student_id UUID FK
redeemed_at TIMESTAMP
status ENUM
```

------------------------------------------------------------------------

# 59. Transactions

Future-ready table:

``` text
transactions
------------
id UUID PK
student_id UUID FK
business_id UUID FK
amount DECIMAL
currency VARCHAR
status ENUM
payment_provider VARCHAR NULL
provider_reference VARCHAR NULL
created_at TIMESTAMP
completed_at TIMESTAMP NULL
```

Future statuses:

``` text
PENDING
PAID
SERVICE_COMPLETED
REFUND_REQUESTED
REFUNDED
DISPUTED
```

Do not implement escrow merely because the table exists.

------------------------------------------------------------------------

# 60. Notifications

``` text
notifications
-------------
id UUID PK
user_id UUID FK
title VARCHAR
body TEXT
type VARCHAR
reference_id UUID NULL
is_read BOOLEAN
created_at TIMESTAMP
```

------------------------------------------------------------------------

# 61. Audit Logs

``` text
audit_logs
----------
id UUID PK
admin_id UUID FK
action VARCHAR
entity_type VARCHAR
entity_id UUID
old_data JSONB NULL
new_data JSONB NULL
reason TEXT NULL
created_at TIMESTAMP
```

------------------------------------------------------------------------

# 62. API Architecture

Backend:

**FastAPI + Python**

API style:

**REST**

Data format:

**JSON**

Base URL:

``` text
/api/v1
```

All API endpoints should be versioned.

------------------------------------------------------------------------

# 63. Authentication API

``` text
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/logout
POST /api/v1/auth/refresh
POST /api/v1/auth/verify-email
POST /api/v1/auth/resend-verification
GET  /api/v1/auth/me
```

College verification:

``` text
POST /api/v1/students/verify-college-email
POST /api/v1/students/confirm-college-email
```

------------------------------------------------------------------------

# 64. Student APIs

``` text
GET    /api/v1/students/me
PATCH  /api/v1/students/me
GET    /api/v1/students/me/favorites
POST   /api/v1/students/me/favorites/{business_id}
DELETE /api/v1/students/me/favorites/{business_id}
```

------------------------------------------------------------------------

# 65. College APIs

``` text
GET /api/v1/colleges
GET /api/v1/colleges/{id}
GET /api/v1/colleges/{id}/campuses
```

Admin:

``` text
POST   /api/v1/admin/colleges
PATCH  /api/v1/admin/colleges/{id}
DELETE /api/v1/admin/colleges/{id}
```

------------------------------------------------------------------------

# 66. Business APIs

Public:

``` text
GET /api/v1/businesses
GET /api/v1/businesses/{id}
GET /api/v1/businesses/{id}/services
GET /api/v1/businesses/{id}/hours
GET /api/v1/businesses/{id}/photos
GET /api/v1/businesses/{id}/reviews
GET /api/v1/businesses/{id}/offers
```

Owner:

``` text
POST  /api/v1/businesses
PATCH /api/v1/businesses/{id}
POST  /api/v1/businesses/{id}/submit-verification
```

------------------------------------------------------------------------

# 67. Service APIs

``` text
POST   /api/v1/businesses/{id}/services
PATCH  /api/v1/services/{service_id}
DELETE /api/v1/services/{service_id}
```

------------------------------------------------------------------------

# 68. Review APIs

``` text
GET    /api/v1/businesses/{id}/reviews
POST   /api/v1/businesses/{id}/reviews
PATCH  /api/v1/reviews/{id}
DELETE /api/v1/reviews/{id}
POST   /api/v1/reviews/{id}/report
POST   /api/v1/reviews/{id}/helpful
```

Owner:

``` text
POST /api/v1/reviews/{id}/response
```

Admin:

``` text
GET   /api/v1/admin/reviews
PATCH /api/v1/admin/reviews/{id}/moderate
```

------------------------------------------------------------------------

# 69. Offer APIs

``` text
GET  /api/v1/offers
GET  /api/v1/offers/{id}

POST  /api/v1/businesses/{id}/offers
PATCH /api/v1/offers/{id}

POST /api/v1/offers/{id}/redeem
```

------------------------------------------------------------------------

# 70. Report APIs

``` text
POST /api/v1/businesses/{id}/report
POST /api/v1/reviews/{id}/report
GET  /api/v1/admin/reports
PATCH /api/v1/admin/reports/{id}
```

------------------------------------------------------------------------

# 71. Admin API

``` text
GET /api/v1/admin/dashboard

GET /api/v1/admin/users
PATCH /api/v1/admin/users/{id}

GET /api/v1/admin/businesses
PATCH /api/v1/admin/businesses/{id}/status
PATCH /api/v1/admin/businesses/{id}/verify

GET /api/v1/admin/reviews
PATCH /api/v1/admin/reviews/{id}/moderate

GET /api/v1/admin/reports
PATCH /api/v1/admin/reports/{id}

GET /api/v1/admin/audit-logs
```

------------------------------------------------------------------------

# 72. Authorization

Authentication answers:

> Who are you?

Authorization answers:

> What are you allowed to do?

Implement role-based access control.

Example:

``` text
STUDENT
OWNER
ADMIN
COLLEGE_ADMIN
```

Additionally enforce object-level authorization.

A shop owner must only modify businesses they own.

A student must only modify their own profile and reviews.

An admin may access platform resources according to admin permissions.

------------------------------------------------------------------------

# 73. Security Requirements

Minimum:

-   Password hashing using Argon2 or bcrypt
-   JWT or secure session architecture
-   Refresh-token rotation if JWT is used
-   HTTPS in production
-   Input validation
-   SQL injection protection via ORM/parameterized queries
-   Rate limiting
-   Authentication throttling
-   File upload validation
-   Image size limits
-   MIME type validation
-   Authorization checks
-   Audit logs
-   Secure secrets management
-   CORS configuration
-   No secrets in source code
-   Environment variables
-   Database backups
-   Error messages that do not leak sensitive information

------------------------------------------------------------------------

# 74. Image Upload Security

Never blindly trust file extensions.

Validate:

-   MIME type
-   File signature
-   Maximum size
-   Dimensions
-   Extension
-   Content

Future:

-   Malware scanning
-   Image moderation
-   Duplicate detection
-   AI-generated image detection where useful

------------------------------------------------------------------------

# 75. Privacy

Student email should not be publicly displayed.

Public reviews may display:

``` text
Anonymous Student
🎓 Verified Student
```

Internal administrators may have access according to legitimate platform
needs.

Do not expose:

-   Personal phone
-   College email
-   Private transaction information
-   Exact personal location history

unless required and appropriately authorized.

------------------------------------------------------------------------

# 76. Location Privacy

Location should be requested only when useful.

Use cases:

-   Nearby businesses
-   Directions
-   Distance calculation

Do not permanently track students merely because the app is installed.

Prefer:

-   on-demand location
-   coarse location when sufficient
-   explicit permission
-   clear explanation

------------------------------------------------------------------------

# 77. Business Location Verification

Possible verification methods:

-   Owner-submitted coordinates
-   Address
-   Phone verification
-   Documentation
-   Admin verification
-   Future geospatial checks

Do not display a "verified location" badge unless the platform actually
verified it.

------------------------------------------------------------------------

# 78. Pricing Model

Do not make listing fees the only revenue source.

## Free business listing

Basic:

-   Name
-   Location
-   Category
-   Hours
-   Services
-   Basic profile

## Paid business plan

Potential:

-   Advanced analytics
-   Offers
-   Customer acquisition tracking
-   Booking
-   Enhanced profile
-   CRM tools
-   Promotional campaigns

## Transaction revenue

Future:

AAS PAAS can charge a transaction fee when it actually facilitates a
transaction.

## Sponsored placements

Possible later, but must be clearly labeled.

Never allow:

``` text
PAY → FAKE TRUST
```

------------------------------------------------------------------------

# 79. Student Economics

The app should be free for students initially.

Potential future monetization:

-   Student Pass
-   Premium deals
-   Partner subscriptions
-   Convenience fees where justified

But do not introduce student subscription fees before proving meaningful
value.

------------------------------------------------------------------------

# 80. "Money Only Moves When the Job Is Done Right"

This is a future product principle, not an MVP implementation
requirement.

Future transaction flow:

``` text
Student selects service
        ↓
Price shown
        ↓
Student books/pays
        ↓
Payment recorded
        ↓
Service performed
        ↓
Student confirms completion
        ↓
Business receives settlement
```

If there is a dispute:

``` text
Dispute
   ↓
Evidence
   ↓
Review
   ↓
Resolution
   ↓
Refund / partial settlement / release
```

This system requires serious payment, legal, regulatory, and operational
design before launch.

Do not claim "money-back guarantee" unless the exact terms, funding
mechanism, eligibility, and dispute process exist.

------------------------------------------------------------------------

# 81. Business Acquisition Strategy

Initial supply strategy:

1.  Select one campus.
2.  Map every useful business around it.
3.  Create a verified seed database.
4.  Contact businesses.
5.  Give them a free initial profile.
6.  Encourage accurate pricing and hours.
7.  Offer student deals.
8.  Measure student usage.
9.  Introduce paid features after demonstrated value.

The initial objective is **density and quality**, not revenue.

------------------------------------------------------------------------

# 82. Student Acquisition

Initial student acquisition:

-   College clubs
-   Student representatives
-   Campus ambassadors
-   QR posters
-   Orientation events
-   WhatsApp groups
-   Student communities
-   Referral system later

Do not build a referral system before the product itself is useful.

------------------------------------------------------------------------

# 83. Campus Ambassador Program

Future feature:

Ambassadors can:

-   Introduce businesses
-   Report outdated information
-   Promote verified deals
-   Collect feedback
-   Help onboard students

Do not give ambassadors unchecked moderation power.

------------------------------------------------------------------------

# 84. Campus Launch Strategy

Pilot target:

``` text
1 college
1 campus
3 km radius
100–200 businesses
500+ verified students
```

Success is not:

> "We got 10,000 downloads."

Success is:

-   Students repeatedly search
-   Students make decisions using the app
-   Businesses receive customers
-   Reviews accumulate
-   Information stays accurate
-   Users return

------------------------------------------------------------------------

# 85. Core Product Metrics

## Student metrics

-   Registered students
-   Verified students
-   Weekly active students
-   Monthly active students
-   Search count
-   Business views
-   Direction requests
-   Offer views
-   Offer redemptions
-   Reviews submitted
-   Repeat usage

## Business metrics

-   Registered businesses
-   Verified businesses
-   Active businesses
-   Profile views
-   Customer acquisition
-   Offer redemptions
-   Review responses
-   Paid conversion

## Trust metrics

-   Percentage verified reviews
-   Review reports
-   Fake review rate
-   Business verification rate
-   Price freshness
-   Hours freshness
-   Report resolution time

------------------------------------------------------------------------

# 86. North Star Metric

Potential North Star Metric:

> **Verified student-business interactions per week.**

This is more meaningful than downloads.

A verified interaction could eventually mean:

-   Verified visit
-   Offer redemption
-   Booking
-   Transaction
-   Confirmed service

The exact definition should be finalized after pilot data.

------------------------------------------------------------------------

# 87. Search Ranking

Do not rank solely by:

-   Payment
-   Rating
-   Review count

Initial ranking can combine:

-   Relevance
-   Distance
-   Open status
-   Verification
-   Rating
-   Review volume
-   Freshness
-   Student discount
-   Search intent

A paid promotion should be clearly labeled.

Avoid hidden pay-to-win ranking.

------------------------------------------------------------------------

# 88. Recommendation System

Future recommendation inputs:

-   Student's college
-   Distance
-   Search history
-   Saved businesses
-   Previous interactions
-   Category preferences
-   Price preferences
-   Time
-   Open status
-   Reviews
-   Deals

Do not infer sensitive characteristics unnecessarily.

------------------------------------------------------------------------

# 89. "Best" Labels

Avoid arbitrary editorial claims.

Instead of:

> Best gym

use:

> Highly rated by verified students

or:

> 4.6 average from 218 reviews

or:

> Most saved gym near campus

The system should show evidence rather than pretending to be an
authority without basis.

------------------------------------------------------------------------

# 90. Hygiene Information

Hygiene is subjective unless independently inspected.

Use:

> Student-reported cleanliness: 3.8/5

rather than:

> This restaurant is unhygienic.

If AAS PAAS eventually conducts inspections, create a separate verified
inspection system.

------------------------------------------------------------------------

# 91. Verified Pricing

Future feature.

Business submits:

``` text
Service
Price
```

Admin/verification process confirms it.

Badge:

``` text
✓ Pricing verified
Updated 5 days ago
```

If unverified:

``` text
Price provided by business
```

This distinction matters.

------------------------------------------------------------------------

# 92. Business Complaints

Business owners should have a formal process to dispute:

-   Fake reviews
-   False information
-   Unauthorized photos
-   Incorrect prices
-   Misleading categories

Every complaint becomes a case with:

-   status
-   evidence
-   timestamps
-   assigned moderator
-   resolution

------------------------------------------------------------------------

# 93. Student Disputes

Future transactions can support:

-   Service not delivered
-   Wrong service
-   Wrong price
-   Poor service
-   Cancellation
-   Refund request

Evidence:

-   Transaction
-   Booking
-   Photos
-   Messages
-   timestamps

------------------------------------------------------------------------

# 94. Notifications

Examples:

Student:

-   Review approved
-   Offer expiring
-   Booking reminder
-   Business responded
-   Report resolved

Owner:

-   New review
-   New offer redemption
-   Verification approved
-   Verification rejected
-   Profile views milestone
-   Report received

Admin:

-   New business verification
-   New review report
-   New business report
-   Dispute escalation

Avoid notification spam.

------------------------------------------------------------------------

# 95. App Navigation

## Student

``` text
Home
Search
Map
Saved
Profile
```

## Owner

``` text
Dashboard
Business
Offers
Reviews
Profile
```

## Admin

Web dashboard:

``` text
Overview
Users
Businesses
Reviews
Reports
Colleges
Categories
Offers
Transactions
Audit Logs
Settings
```

------------------------------------------------------------------------

# 96. Mobile Technology

Recommended:

**Flutter + Dart**

Reasons:

-   One codebase
-   Android and iOS
-   Good UI performance
-   Mature ecosystem
-   Suitable for this project

------------------------------------------------------------------------

# 97. Backend Technology

Recommended:

**Python + FastAPI**

Reasons:

-   Fast development
-   Strong typing support
-   Excellent API documentation
-   Async support
-   Easy integration with ML later
-   Familiar ecosystem

------------------------------------------------------------------------

# 98. ORM

Recommended:

**SQLAlchemy**

Use migrations with:

**Alembic**

Never manually change production schema without migrations.

------------------------------------------------------------------------

# 99. Database

Recommended:

**PostgreSQL + PostGIS**

Use PostGIS for:

-   Radius searches
-   Distance
-   Nearby businesses
-   Campus boundaries
-   Geospatial indexing

------------------------------------------------------------------------

# 100. Admin Frontend

Recommended:

**Next.js + TypeScript**

Admin panel should be web-based.

------------------------------------------------------------------------

# 101. File Storage

Use object storage rather than storing images directly in PostgreSQL.

Possible:

-   Amazon S3
-   Cloudinary
-   Supabase Storage
-   Other S3-compatible storage

Database stores:

``` text
image_url
metadata
uploader
status
```

------------------------------------------------------------------------

# 102. Push Notifications

Recommended:

**Firebase Cloud Messaging**

Mobile device tokens must be stored securely.

------------------------------------------------------------------------

# 103. Maps

Possible:

-   Google Maps Platform
-   Mapbox

The final provider should be chosen based on:

-   pricing
-   API limits
-   India coverage
-   SDK quality
-   required features

Do not hardcode a provider throughout the application.

Create a map abstraction where practical.

------------------------------------------------------------------------

# 104. Repository Structure

Recommended monorepo:

``` text
aas-paas/
│
├── mobile/
│   └── Flutter application
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── repositories/
│   │   ├── utils/
│   │   └── main.py
│   ├── migrations/
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
│
├── admin/
│   └── Next.js application
│
├── docs/
│   ├── product-spec.md
│   ├── api-spec.md
│   ├── database.md
│   └── architecture.md
│
├── docker/
│
├── README.md
└── .gitignore
```

------------------------------------------------------------------------

# 105. Backend Layering

Recommended:

``` text
API / Router
     ↓
Schema Validation
     ↓
Service Layer
     ↓
Repository / Data Access
     ↓
Database
```

Do not put all business logic inside FastAPI route handlers.

------------------------------------------------------------------------

# 106. API Response Format

Use a consistent format.

Success:

``` json
{
  "success": true,
  "data": {},
  "message": "Business retrieved successfully"
}
```

Error:

``` json
{
  "success": false,
  "error": {
    "code": "BUSINESS_NOT_FOUND",
    "message": "Business not found"
  }
}
```

Do not expose raw database exceptions.

------------------------------------------------------------------------

# 107. Pagination

All potentially large endpoints must support pagination.

Examples:

``` text
GET /businesses?page=1&page_size=20
```

Prefer cursor pagination for feeds that eventually require it.

------------------------------------------------------------------------

# 108. Filtering

Example:

``` text
GET /businesses
?campus_id=...
&category=gym
&open_now=true
&min_rating=4
&max_distance=2000
```

Validate all query parameters.

------------------------------------------------------------------------

# 109. Sorting

Possible:

``` text
relevance
distance
rating
review_count
newest
price_low_to_high
```

Avoid exposing arbitrary database sorting fields.

Whitelist valid values.

------------------------------------------------------------------------

# 110. Error Handling

Standard error types:

-   Validation error
-   Authentication error
-   Authorization error
-   Not found
-   Conflict
-   Rate limited
-   Server error

Never return stack traces to mobile clients in production.

------------------------------------------------------------------------

# 111. Logging

Backend logs should include:

-   request ID
-   timestamp
-   endpoint
-   status
-   latency
-   authenticated user ID where appropriate

Never log:

-   passwords
-   tokens
-   sensitive personal information

------------------------------------------------------------------------

# 112. Rate Limiting

Protect:

-   Login
-   Registration
-   Verification
-   Review creation
-   Review reporting
-   Offer redemption
-   Password reset
-   Admin endpoints

------------------------------------------------------------------------

# 113. Review Limits

Prevent spam.

Potential initial rules:

-   One active review per student/business
-   Student can edit existing review
-   Re-review can be supported after a defined period or verified new
    transaction
-   Rate-limit review creation

Do not make rules so strict that legitimate repeated experiences cannot
be represented.

------------------------------------------------------------------------

# 114. Business Ownership

One business should have:

-   One primary owner
-   Optional authorized staff later

Ownership transfer should require admin verification.

------------------------------------------------------------------------

# 115. Business Duplicate Detection

Before creating a new business, check:

-   Name similarity
-   Phone
-   Location
-   Address
-   Owner
-   Existing category

Admin should review possible duplicates.

------------------------------------------------------------------------

# 116. Account Deletion

Student should be able to request deletion.

Need to decide future policy for reviews.

Recommended approach:

-   Delete or anonymize personal identity
-   Retain review content only where legally and ethically appropriate
-   Preserve platform integrity without retaining unnecessary personal
    data

This requires a formal privacy policy before production.

------------------------------------------------------------------------

# 117. Terms and Policies

Before public launch, create:

-   Terms of Service
-   Privacy Policy
-   Community Guidelines
-   Review Policy
-   Business Listing Policy
-   Refund Policy if payments exist
-   Dispute Policy if payments exist
-   Student Discount Terms
-   Content Moderation Policy

Do not present these as legal advice; obtain appropriate legal review
before commercial launch.

------------------------------------------------------------------------

# 118. Content Moderation

Moderate:

-   Reviews
-   Photos
-   Business descriptions
-   Offers
-   Usernames
-   Profile images

Potential prohibited content:

-   Illegal goods/services
-   Threats
-   Hate
-   Harassment
-   Personal information
-   Fraud
-   Spam
-   Sexual exploitation
-   Malicious links
-   Fake business information

------------------------------------------------------------------------

# 119. Data Freshness

Important fields should track update timestamps.

Examples:

``` text
business.updated_at
service.updated_at
price_history
business_hours.updated_at
photo.created_at
review.created_at
```

Future freshness scoring can use these timestamps.

------------------------------------------------------------------------

# 120. Trust Score Concept

Do not launch a mysterious global "trust score" initially.

Instead expose understandable evidence:

-   Verified student
-   Verified business
-   Verified transaction
-   Verified pricing
-   Recent reviews
-   Recent information

Future trust scoring can be researched after sufficient data exists.

------------------------------------------------------------------------

# 121. Business Analytics

Basic:

-   Views
-   Searches
-   Direction requests
-   Calls
-   Offer views
-   Offer redemptions
-   Reviews

Future:

-   Conversion funnel
-   Repeat customers
-   Search ranking
-   Revenue attribution
-   Customer cohorts

------------------------------------------------------------------------

# 122. Student Analytics

Internal only:

-   Search frequency
-   Category popularity
-   Business views
-   Offer usage
-   Review creation
-   Retention

Avoid collecting unnecessary behavioral data.

------------------------------------------------------------------------

# 123. Product Analytics

Track events:

``` text
app_opened
search_performed
category_opened
business_viewed
directions_clicked
call_clicked
favorite_added
review_started
review_submitted
offer_viewed
offer_redeemed
business_reported
review_reported
```

Do not collect unnecessary sensitive information.

------------------------------------------------------------------------

# 124. MVP Development Order

## Phase 1

Project setup.

## Phase 2

Database models + migrations.

## Phase 3

Authentication.

## Phase 4

College verification.

## Phase 5

Student profiles.

## Phase 6

Business CRUD.

## Phase 7

Business verification.

## Phase 8

Categories/search.

## Phase 9

Business detail page.

## Phase 10

Reviews.

## Phase 11

Photos.

## Phase 12

Maps.

## Phase 13

Favorites.

## Phase 14

Offers.

## Phase 15

Owner dashboard.

## Phase 16

Admin dashboard.

## Phase 17

Reports/moderation.

## Phase 18

Testing/security.

## Phase 19

Pilot deployment.

------------------------------------------------------------------------

# 125. Development Rule for Claude Code

Claude Code should not be instructed to build the entire product in one
uncontrolled generation.

Use incremental implementation.

For every phase:

1.  Read existing architecture.
2.  Inspect current files.
3.  Identify affected modules.
4.  Implement only requested scope.
5.  Run tests.
6.  Run static checks.
7.  Run formatting.
8.  Run application.
9.  Verify API behavior.
10. Document changes.
11. Do not modify unrelated modules.

------------------------------------------------------------------------

# 126. Definition of Done

A feature is not complete merely because code exists.

It is complete when:

-   Backend implementation exists
-   Validation exists
-   Authorization exists
-   Database migration exists
-   Tests exist
-   Error handling exists
-   API documentation exists
-   UI is integrated
-   Loading state exists
-   Empty state exists
-   Error state exists
-   Success state exists
-   Security is considered
-   Existing tests still pass

------------------------------------------------------------------------

# 127. Testing Strategy

## Unit tests

Test:

-   Services
-   Validation
-   Permissions
-   Utility functions

## Integration tests

Test:

-   API + database
-   Authentication
-   Business creation
-   Review creation
-   Verification

## End-to-end

Test:

``` text
Student registration
→ email verification
→ search
→ business view
→ review
```

Owner:

``` text
registration
→ business submission
→ admin approval
→ profile management
```

Admin:

``` text
login
→ business approval
→ review moderation
→ audit log
```

------------------------------------------------------------------------

# 128. Seed Data

Development environment should contain:

-   Example college
-   Example campus
-   20--50 sample businesses
-   Categories
-   Services
-   Reviews
-   Offers
-   Test students
-   Test owners
-   Test admin

Never use real private data in development.

------------------------------------------------------------------------

# 129. Environment Configuration

Use:

``` text
.env
.env.example
```

Possible variables:

``` text
DATABASE_URL
JWT_SECRET
JWT_REFRESH_SECRET
GOOGLE_MAPS_API_KEY
FIREBASE_CONFIG
STORAGE_BUCKET
STORAGE_ACCESS_KEY
STORAGE_SECRET_KEY
```

Never commit `.env`.

------------------------------------------------------------------------

# 130. Deployment Architecture

Initial:

``` text
Flutter Mobile
       │
       ▼
Cloud Backend
       │
       ├── FastAPI
       │
       └── PostgreSQL + PostGIS
```

Admin:

``` text
Next.js
   ↓
FastAPI
```

Storage:

``` text
Object Storage
```

Notifications:

``` text
Firebase Cloud Messaging
```

------------------------------------------------------------------------

# 131. Backup Strategy

Database:

-   Automated daily backups
-   Point-in-time recovery where affordable
-   Periodic restore tests

Images:

-   Object storage redundancy
-   Versioning where useful

Never assume backups are valid without restore testing.

------------------------------------------------------------------------

# 132. Observability

Production should eventually have:

-   Error tracking
-   API metrics
-   Database metrics
-   Uptime monitoring
-   Log aggregation
-   Performance monitoring

Track:

-   API latency
-   error rate
-   database load
-   storage usage
-   crash rate

------------------------------------------------------------------------

# 133. Scalability Strategy

Initial scale:

One campus.

Architecture should still support:

``` text
College A
 ├── Campus 1
 └── Campus 2

College B
 └── Campus 1
```

Do not build separate databases for each college unless scale later
requires it.

Use relational identifiers:

``` text
college_id
campus_id
```

------------------------------------------------------------------------

# 134. Multi-Tenant Considerations

College data must be isolated logically.

Every college-specific entity should be associated with a college or
campus.

Authorization must ensure:

``` text
College Admin A
≠
College Admin B
```

------------------------------------------------------------------------

# 135. Search Index Future

PostgreSQL is sufficient initially.

Later, if scale requires:

-   Elasticsearch
-   OpenSearch
-   Meilisearch
-   Typesense

Do not add a search engine before PostgreSQL search becomes a real
bottleneck.

------------------------------------------------------------------------

# 136. Caching

Future:

-   Redis

Potential uses:

-   Popular categories
-   Nearby businesses
-   Business details
-   Rate limits
-   Sessions
-   Notification queues

Do not introduce Redis before it solves a real problem.

------------------------------------------------------------------------

# 137. Background Jobs

Future queue system for:

-   Email
-   Notifications
-   Image processing
-   Review moderation
-   Analytics
-   Offer expiration
-   Data freshness checks

Possible:

-   Celery
-   RQ
-   Dramatiq
-   Cloud-native job queues

------------------------------------------------------------------------

# 138. AI Features --- Future Only

Potential:

## AI Search

Student:

> "I need a cheap place to study with Wi-Fi near college."

System:

-   interprets intent
-   filters businesses
-   ranks relevant results

## AI Review Summaries

Example:

``` text
Students commonly praise:
- food quantity
- pricing

Common complaints:
- waiting time
- crowding
```

Summaries must link back to actual review evidence.

AI must not fabricate opinions.

## AI Fraud Detection

Use signals to flag suspicious reviews.

AI should assist moderation, not automatically become the final judge
for high-impact decisions.

------------------------------------------------------------------------

# 139. Personalized Recommendations --- Future

Potential:

``` text
Student preferences
      +
Location
      +
Time
      +
Business data
      +
Verified interactions
      ↓
Recommendations
```

Do not over-personalize the MVP.

------------------------------------------------------------------------

# 140. Social Features --- Caution

Potential:

-   Follow friends
-   Shared lists
-   Group recommendations

But social feeds create:

-   moderation burden
-   privacy issues
-   spam
-   distraction from core utility

Not MVP.

------------------------------------------------------------------------

# 141. AAS PAAS Pass --- Future

Potential subscription:

``` text
AAS PAAS PASS

₹99/month

Student-only offers
Exclusive discounts
Partner benefits
```

Only launch after the marketplace has enough valuable offers.

------------------------------------------------------------------------

# 142. Business Subscription --- Future

Possible tiers:

``` text
FREE
Basic listing

GROWTH
Analytics
Offers
Enhanced profile

PRO
Bookings
CRM
Advanced analytics
Promotions
```

Exact pricing should be determined by actual merchant willingness to
pay.

------------------------------------------------------------------------

# 143. Key Business Model Principle

Do not sell trust.

Sell:

-   Discovery
-   Customer acquisition
-   Analytics
-   Convenience
-   Booking
-   Transaction infrastructure
-   Promotions

Trust should be earned through evidence.

------------------------------------------------------------------------

# 144. Competitive Positioning

Existing platforms already solve:

-   Generic business discovery
-   Maps
-   Broad reviews
-   Food delivery
-   General local search

AAS PAAS focuses on:

``` text
College
+
Local radius
+
Verified students
+
Student-specific information
+
Structured reviews
+
Student discounts
+
Campus-specific trust
```

The differentiation is the combination, not any single feature.

------------------------------------------------------------------------

# 145. Biggest Risks

## Risk 1: Empty marketplace

No businesses → no students.

No students → no businesses.

Solution:

Start with manually curated supply around one campus.

## Risk 2: Fake reviews

Destroys trust.

Solution:

Verification layers + moderation + interaction evidence.

## Risk 3: Outdated information

Prices/hours become inaccurate.

Solution:

Freshness timestamps + business update workflows + student reports.

## Risk 4: Businesses refuse to pay

Solution:

Prove customer acquisition before monetization.

## Risk 5: Too many features

Solution:

Strict MVP.

## Risk 6: Admin abuse

Solution:

RBAC + audit logs + moderation policy.

## Risk 7: Legal/payment complexity

Solution:

Do not launch escrow/payment guarantees prematurely.

## Risk 8: Google Maps comparison

Solution:

Don't compete on maps. Compete on campus trust and student context.

------------------------------------------------------------------------

# 146. Brutal Product Reality

The hardest part of AAS PAAS is not coding.

The hard parts are:

1.  Getting businesses onto the platform.
2.  Keeping information accurate.
3.  Getting students to contribute reviews.
4.  Preventing fake reviews.
5.  Creating enough density around a campus.
6.  Getting businesses to provide real discounts.
7.  Creating repeat usage.

A technically beautiful app with 30 businesses and 12 reviews is
worthless.

A relatively simple app with 200 accurate businesses and hundreds of
verified student interactions is valuable.

------------------------------------------------------------------------

# 147. Pilot Success Criteria

Do not expand to another campus until the pilot demonstrates meaningful
usage.

Suggested targets:

-   500+ verified students
-   100+ quality business listings
-   50+ active businesses
-   300+ genuine reviews
-   50+ student offers
-   Repeat weekly usage
-   Businesses reporting measurable customer acquisition
-   Low fake-review rate
-   High information freshness

These are target hypotheses, not guaranteed benchmarks.

------------------------------------------------------------------------

# 148. Initial Business Categories to Prioritize

Do not onboard every possible category first.

Priority:

1.  Food
2.  Mess
3.  Cafes
4.  Laundry
5.  Medical
6.  Grocery
7.  Stationery/printing
8.  Salon
9.  Gym
10. Repair services

These are frequent student needs.

------------------------------------------------------------------------

# 149. Student Frequency Model

High-frequency categories:

-   Food
-   Grocery
-   Cafes
-   Laundry
-   Printing
-   Medical

Medium-frequency:

-   Salon
-   Gym
-   Repair
-   Clothing

Low-frequency:

-   Hotel
-   Photography
-   Documentation

Prioritize high-frequency categories during pilot.

------------------------------------------------------------------------

# 150. UX Principles

The app should feel:

-   Fast
-   Local
-   Trustworthy
-   Practical
-   Uncluttered

Avoid:

-   excessive animations
-   unnecessary onboarding
-   excessive popups
-   aggressive advertising
-   dark patterns

The student should find a useful business in seconds.

------------------------------------------------------------------------

# 151. Business Detail UX Principle

The user should not need to open five pages to determine:

-   Price
-   Distance
-   Hours
-   Rating
-   Student discount
-   Services

These should be visible immediately.

------------------------------------------------------------------------

# 152. Empty States

Every screen must have a useful empty state.

Example:

``` text
No businesses found.

Try:
- increasing distance
- removing a filter
- searching another category
```

------------------------------------------------------------------------

# 153. Loading States

Use:

-   skeleton loaders
-   progress indicators
-   optimistic updates only where safe

Avoid blank screens.

------------------------------------------------------------------------

# 154. Error States

Example:

``` text
Couldn't load businesses.

Check your connection and try again.
[Retry]
```

Never show raw backend exceptions.

------------------------------------------------------------------------

# 155. Accessibility

Support:

-   readable text
-   adequate contrast
-   semantic labels
-   scalable fonts
-   screen readers where practical
-   touch targets
-   meaningful icons with labels

------------------------------------------------------------------------

# 156. Localization

Initial language:

English.

Future:

-   Marathi
-   Hindi

All user-facing strings should be externalized rather than hardcoded
throughout the UI.

------------------------------------------------------------------------

# 157. Database Constraints

Use:

-   foreign keys
-   unique constraints
-   check constraints
-   not-null where appropriate
-   indexes
-   composite indexes

Examples:

``` text
users.email UNIQUE

favorites(user_id, business_id) UNIQUE

review rating BETWEEN 1 AND 5

service price >= 0
```

------------------------------------------------------------------------

# 158. Important Indexes

Likely indexes:

``` text
users.email
students.college_id
businesses.campus_id
businesses.status
businesses.verification_status
businesses.latitude/longitude via PostGIS
reviews.business_id
reviews.user_id
reviews.created_at
offers.business_id
offers.status
notifications.user_id
audit_logs.entity_id
```

Use actual query plans to optimize further.

------------------------------------------------------------------------

# 159. Data Integrity

Do not allow:

-   review for nonexistent business
-   review from nonexistent user
-   offer for nonexistent business
-   service for nonexistent business
-   student assigned to nonexistent college
-   owner editing another owner's business

Use both:

-   database constraints
-   application authorization

------------------------------------------------------------------------

# 160. Soft Delete

For important records, prefer soft deletion where historical integrity
matters.

Examples:

-   businesses
-   reviews
-   users

Possible:

``` text
deleted_at
```

Do not permanently delete records when doing so would destroy audit or
transaction integrity unless required.

------------------------------------------------------------------------

# 161. Admin Permission Granularity --- Future

Instead of all admins having identical power:

``` text
SUPER_ADMIN
MODERATOR
BUSINESS_REVIEWER
SUPPORT_AGENT
FINANCE_ADMIN
```

This is future scope.

MVP may use a single admin role, but the architecture should not assume
permanent unrestricted admin access.

------------------------------------------------------------------------

# 162. Business Verification Audit

Store:

-   submitted_at
-   reviewed_at
-   reviewed_by
-   decision
-   reason
-   evidence

This allows:

``` text
Who approved this business?
When?
Why?
```

------------------------------------------------------------------------

# 163. Review Moderation Audit

Store:

-   report
-   moderator
-   decision
-   reason
-   timestamp
-   evidence

Never silently delete moderation history.

------------------------------------------------------------------------

# 164. Notification Preferences

Future:

Students:

``` text
Offers
Reviews
Bookings
System
```

Owners:

``` text
Reviews
Offers
Analytics
Verification
System
```

Users can disable non-essential notifications.

------------------------------------------------------------------------

# 165. Search Ranking Fairness

The ranking algorithm should not silently prioritize businesses solely
because they pay.

If sponsored:

``` text
Sponsored
```

must be visible.

Organic ranking should use product-relevant evidence.

------------------------------------------------------------------------

# 166. Fraud and Abuse

Potential abuse:

-   Fake student accounts
-   Fake businesses
-   Fake reviews
-   Review manipulation
-   Coupon abuse
-   Referral abuse
-   Payment fraud
-   Owner impersonation
-   Admin abuse

Design security progressively.

------------------------------------------------------------------------

# 167. Student Account Risk Signals

Potential signals:

-   email verification
-   account age
-   repeated failed verification
-   unusual review velocity
-   suspicious device behavior
-   repeated offer redemption attempts

Do not automatically ban based on a single signal.

------------------------------------------------------------------------

# 168. Owner Risk Signals

Potential:

-   duplicate businesses
-   repeated reports
-   misleading pricing
-   repeated verification failures
-   suspicious review patterns
-   refund/dispute rate

Use for review and investigation.

------------------------------------------------------------------------

# 169. Business Information Source

Initial data can come from:

-   owner submissions
-   manual campus research
-   verified student reports
-   public business information where legally permitted
-   direct business confirmation

Never represent unverified data as verified fact.

------------------------------------------------------------------------

# 170. Manual Admin Tools

Admin should be able to quickly correct:

-   business name
-   category
-   location
-   hours
-   phone
-   services
-   price
-   photos
-   status

Every manual modification should be logged.

------------------------------------------------------------------------

# 171. Data Import

Future admin tool:

CSV import:

``` text
name
category
address
phone
latitude
longitude
hours
```

Useful for bootstrapping a campus.

Validate imported data before publishing.

------------------------------------------------------------------------

# 172. Business Onboarding Workflow

``` text
Owner registers
      ↓
Creates listing
      ↓
Adds required information
      ↓
Uploads evidence
      ↓
Submits
      ↓
Admin review
      ↓
Approved
      ↓
Business becomes public
```

------------------------------------------------------------------------

# 173. Student Review Workflow

``` text
Student opens business
      ↓
Write Review
      ↓
Overall rating
      ↓
Category ratings
      ↓
Text
      ↓
Optional photos
      ↓
Submit
      ↓
Validation/moderation
      ↓
Published
```

------------------------------------------------------------------------

# 174. Student Report Workflow

``` text
Business/Review
      ↓
Report
      ↓
Select reason
      ↓
Optional evidence
      ↓
Submit
      ↓
Admin queue
      ↓
Investigation
      ↓
Decision
      ↓
Student notified
```

------------------------------------------------------------------------

# 175. Future Booking Architecture

Potential tables:

``` text
bookings
booking_services
availability_slots
booking_status_history
```

Do not implement until required.

------------------------------------------------------------------------

# 176. Future Payment Architecture

Potential:

``` text
payment_intents
payments
refunds
settlements
disputes
```

Do not directly build an internal wallet without a well-defined
financial architecture.

------------------------------------------------------------------------

# 177. Future Transaction Verification

Transaction can become:

``` text
BOOKED
PAID
SERVICE_STARTED
SERVICE_COMPLETED
STUDENT_CONFIRMED
SETTLED
```

This enables Verified Transaction reviews.

------------------------------------------------------------------------

# 178. Future Money-Back Guarantee

Possible eligibility:

-   transaction completed through AAS PAAS
-   service not delivered / materially different
-   dispute submitted within defined window
-   evidence provided
-   case qualifies under policy

Never advertise an unconditional guarantee.

------------------------------------------------------------------------

# 179. Future Merchant Settlement

Potential:

``` text
Customer payment
       ↓
Payment provider
       ↓
AAS PAAS transaction ledger
       ↓
Service completion
       ↓
Settlement eligibility
       ↓
Merchant settlement
```

This requires compliance review before real-money deployment.

------------------------------------------------------------------------

# 180. Future Business CRM

Business can eventually see:

-   customer acquisition
-   repeat users
-   offers
-   reviews
-   retention
-   service popularity

Do not expose personally identifiable student information without a
valid reason and appropriate permissions.

------------------------------------------------------------------------

# 181. Product Roadmap

## Phase 0 --- Specification

-   Product definition
-   Roles
-   Screens
-   Database
-   APIs
-   Architecture

## Phase 1 --- MVP

-   Authentication
-   Student verification
-   Businesses
-   Search
-   Reviews
-   Maps
-   Offers
-   Owner dashboard
-   Admin dashboard

## Phase 2 --- Validation

-   One campus
-   Business onboarding
-   Student acquisition
-   Review acquisition
-   Data freshness

## Phase 3 --- Marketplace

-   Bookings
-   Transaction tracking
-   Payments
-   Offer redemption

## Phase 4 --- Trust

-   Visit verification
-   Transaction verification
-   Advanced fraud detection
-   Verified pricing

## Phase 5 --- Expansion

-   More colleges
-   More campuses
-   More cities

## Phase 6 --- Intelligence

-   AI search
-   Recommendations
-   Review summaries
-   Predictive analytics

------------------------------------------------------------------------

# 182. First Pilot

Recommended initial geography:

**MIT Academy of Engineering, Alandi, Pune**

Scope:

``` text
Campus
+
3 km radius
```

Initial target:

``` text
100–200 businesses
500+ verified students
300+ reviews
```

------------------------------------------------------------------------

# 183. Pilot Categories

Start with:

``` text
Food
Mess
Cafe
Laundry
Medical
Grocery
Stationery
Printing
Salon
Gym
Repair
```

------------------------------------------------------------------------

# 184. What NOT to Measure First

Do not obsess over:

-   Downloads
-   Instagram followers
-   App impressions
-   Number of categories
-   Number of screens
-   Code volume

Measure:

-   Verified students
-   Active businesses
-   Searches
-   Business views
-   Direction requests
-   Offer redemptions
-   Genuine reviews
-   Repeat users
-   Merchant-generated customer value

------------------------------------------------------------------------

# 185. Product-Market Fit Signal

Potential signal:

Students stop asking:

> "Do you know a good laundry near college?"

and instead open:

> AAS PAAS.

That behavior is more meaningful than vanity metrics.

------------------------------------------------------------------------

# 186. Brand

Name:

**AAS PAAS**

Concept:

Everything students need around their college.

Possible tagline:

**Everything You Need, Aas Paas.**

Alternative positioning:

**Your Campus. Your Local Market. Your Trust Layer.**

The brand should feel:

-   student-focused
-   local
-   modern
-   trustworthy
-   practical

Avoid making it look like a generic delivery app.

------------------------------------------------------------------------

# 187. Brand Trust Rules

Do not:

-   buy fake reviews
-   fabricate ratings
-   hide legitimate complaints
-   sell verification
-   secretly manipulate rankings
-   advertise businesses as "best" without evidence

If trust is the product, trust cannot be a marketing gimmick.

------------------------------------------------------------------------

# 188. Master Development Philosophy

The product should be developed in controlled increments.

Never ask the coding agent to:

> "Build everything."

Instead:

``` text
Specification
→ Architecture
→ Database
→ Backend
→ Authentication
→ Student
→ Business
→ Reviews
→ Admin
→ Testing
→ Deployment
```

Each phase must remain functional.

------------------------------------------------------------------------

# 189. Claude Code Operating Rules

Claude Code should:

1.  Read `PROJECT_SPEC.md` before modifying code.
2.  Read relevant architecture documentation.
3.  Inspect the current repository.
4.  Never overwrite working code without reason.
5.  Never invent new architecture without documenting it.
6.  Ask only when a genuinely blocking ambiguity exists.
7.  Prefer small changes.
8.  Run tests after implementation.
9.  Run formatting/linting.
10. Report files changed.
11. Report tests executed.
12. Report unresolved issues.
13. Never expose secrets.
14. Never commit `.env`.
15. Never use fake production credentials.
16. Never silently remove existing functionality.
17. Keep migrations versioned.
18. Keep API contracts consistent.
19. Keep authorization server-side.
20. Treat the specification as the source of product truth.

------------------------------------------------------------------------

# 190. Coding Quality Rules

Backend:

-   Type hints
-   Pydantic schemas
-   SQLAlchemy models
-   Service layer
-   Repository/data access layer where useful
-   Dependency injection
-   Structured errors
-   Tests

Flutter:

-   Feature-based organization
-   Typed models
-   API service abstraction
-   Repository pattern where appropriate
-   State management chosen consistently
-   Reusable components
-   Centralized theme
-   Centralized strings

Admin:

-   TypeScript
-   Typed API clients
-   Reusable components
-   Protected routes
-   Role-aware UI

------------------------------------------------------------------------

# 191. Git Strategy

Use:

``` text
main
develop
feature/*
fix/*
```

Commit frequently.

Example:

``` text
feat(auth): add student registration
feat(review): add structured ratings
fix(business): prevent unauthorized edits
```

Do not commit massive unrelated changes under one message.

------------------------------------------------------------------------

# 192. Documentation

Maintain:

``` text
README.md
PROJECT_SPEC.md
ARCHITECTURE.md
DATABASE.md
API.md
SECURITY.md
DEPLOYMENT.md
```

The specification should be updated when major architectural decisions
change.

------------------------------------------------------------------------

# 193. Final Product Architecture

``` text
                         AAS PAAS
                            │
              ┌─────────────┴─────────────┐
              │                           │
        Flutter Mobile              Next.js Admin
              │                           │
              └─────────────┬─────────────┘
                            │
                         HTTPS
                            │
                         FastAPI
                            │
       ┌────────────────────┼────────────────────┐
       │                    │                    │
 Authentication          Services            Admin
       │                    │                    │
       ├───────────┬────────┼──────────┬─────────┤
       │           │        │          │         │
    Students   Businesses Reviews    Offers   Reports
       │           │        │          │         │
       └───────────┴────────┴──────────┴─────────┘
                            │
                     PostgreSQL
                       + PostGIS
                            │
              ┌─────────────┴─────────────┐
              │                           │
        Object Storage              Notifications
              │                           │
           Images                        FCM
```

------------------------------------------------------------------------

# 194. Final MVP Definition

AAS PAAS MVP is successful when a verified student can:

``` text
Register
   ↓
Verify college
   ↓
Open AAS PAAS
   ↓
Search for a service
   ↓
See nearby businesses
   ↓
Compare:
   - rating
   - reviews
   - price
   - distance
   - hours
   - student discount
   ↓
Open business
   ↓
Get directions
   ↓
Use the service
   ↓
Return to AAS PAAS
   ↓
Leave a structured review
```

And a business owner can:

``` text
Register
   ↓
Create business
   ↓
Submit verification
   ↓
Get approved
   ↓
Manage:
   - services
   - prices
   - hours
   - photos
   - offers
   ↓
Receive student traffic
   ↓
Respond to reviews
   ↓
See analytics
```

And an admin can:

``` text
Manage users
Manage businesses
Verify businesses
Moderate reviews
Handle reports
Manage colleges
Manage categories
Audit sensitive actions
```

That is the minimum coherent marketplace.

------------------------------------------------------------------------

# 195. Non-Negotiable Product Rules

1.  Verified does not mean paid.
2.  Paid does not mean highly rated.
3.  Businesses cannot delete legitimate criticism.
4.  Students cannot manipulate ratings without consequences.
5.  Admin actions are auditable.
6.  Prices have timestamps.
7.  Reviews have verification context.
8.  Public profiles protect student privacy.
9.  Search results are not secretly pay-to-win.
10. Unverified information is clearly distinguished from verified
    information.
11. The MVP remains narrow.
12. One campus is the first battlefield.
13. Data quality matters more than listing quantity.
14. Trust is earned through evidence.
15. Payment/escrow is a later phase, not an MVP shortcut.
16. AI assists the product; it does not fabricate facts.
17. No feature is added merely because it sounds impressive.
18. Every feature must improve discovery, trust, transaction, or
    retention.
19. Server-side authorization is mandatory.
20. The specification must evolve through deliberate decisions, not
    accidental code behavior.

------------------------------------------------------------------------

# 196. Immediate Next Engineering Deliverables

Before implementation, the following documents should be finalized:

1.  `PROJECT_SPEC.md` --- this document
2.  `ARCHITECTURE.md`
3.  `DATABASE.md`
4.  `API_SPEC.md`
5.  `SECURITY.md`
6.  `CLAUDE_CODE_RULES.md`

Then create the repository.

Then implement:

``` text
Repository
↓
Backend skeleton
↓
PostgreSQL
↓
Alembic
↓
Core models
↓
Authentication
↓
Student verification
↓
Business module
↓
Reviews
↓
Search
↓
Maps
↓
Offers
↓
Owner dashboard
↓
Admin dashboard
```

------------------------------------------------------------------------

# 197. Final Strategic Position

AAS PAAS should not try to become another Google Maps.

It should not try to become another Zomato.

It should not try to become another Justdial.

It should become:

> **The trusted local operating layer for students around their
> campus.**

The fundamental loop is:

``` text
DISCOVER
   ↓
COMPARE
   ↓
TRUST
   ↓
ACT
   ↓
VERIFY
   ↓
REVIEW
   ↓
IMPROVE
```

The strongest long-term asset is not the UI.

It is the structured dataset created by verified student-business
interactions:

``` text
College
+
Campus
+
Business
+
Services
+
Prices
+
Reviews
+
Verification
+
Offers
+
Transactions
+
Behavior
```

That dataset can eventually power better search, recommendations,
merchant analytics, and campus intelligence.

But the first objective remains simple:

> **Make one campus genuinely useful before trying to own many
> campuses.**

------------------------------------------------------------------------

# 198. Current Locked Decisions

  Area                      Decision
  ------------------------- --------------------------------------------
  Product                   AAS PAAS
  Core audience             College students
  Business audience         Local campus-area businesses
  Initial model             Campus marketplace
  Initial pilot             MIT AOE / Alandi
  Initial radius            \~3 km
  Mobile                    Flutter
  Backend                   FastAPI / Python
  Database                  PostgreSQL
  Geospatial                PostGIS
  ORM                       SQLAlchemy
  Migrations                Alembic
  Admin                     Next.js / TypeScript
  Notifications             Firebase Cloud Messaging
  Images                    Object storage
  Maps                      Google Maps or Mapbox
  Authentication            Email/college verification
  Primary trust mechanism   Verified student/business/interaction
  Review model              Structured category-specific reviews
  Owner review power        Respond/report, not arbitrary deletion
  Admin                     Full platform moderation with audit logs
  MVP payment               Not required
  Escrow                    Future
  AI                        Future
  Multi-campus              Future after pilot
  Student pricing           Free initially
  Merchant monetization     Value-added services, not trust-selling
  Core principle            Trust + local relevance + measurable value

------------------------------------------------------------------------

# 199. Document Status

This document represents the **product and architecture baseline before
coding**.

Any future change to a major decision should be explicit.

Examples of major decisions:

-   Changing mobile framework
-   Changing backend
-   Changing database
-   Changing authentication
-   Changing review verification
-   Introducing payments
-   Changing business monetization
-   Changing role permissions
-   Changing the pilot strategy

Do not let these decisions change accidentally through implementation.

**Next engineering document: `API_SPEC.md` + `ARCHITECTURE.md`, followed
by the Claude Code master implementation prompt.**
