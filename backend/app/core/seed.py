"""Seed Data Script for Pilot Campus Deployment (MIT AOE / Alandi).

Populates initial administrative, institutional, category, rating dimension,
and sample business datasets to establish a production-ready pilot environment.
Idempotent: Safe to execute repeatedly without duplicating records.
"""

from datetime import time
from decimal import Decimal
import logging
from typing import Dict
from uuid import uuid4

from sqlalchemy.orm import Session

from app.auth.jwt_handler import get_password_hash
from app.core.database import SessionLocal
from app.models.business import (
    Business,
    BusinessStatus,
    BusinessVerificationStatus,
    PriceLevel,
    business_categories,
)
from app.models.business_hours import BusinessHours
from app.models.campus import Campus
from app.models.category import Category
from app.models.college import College, CollegeStatus
from app.models.rating_dimension import RatingDimension
from app.models.service import Service
from app.models.service_price_history import ServicePriceHistory
from app.models.user import User, UserRole, UserStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("aaspaas.seed")


def seed_database(db: Session) -> Dict[str, int]:
    """Execute all seeding routines within a transactional session."""
    stats = {
        "users": 0,
        "colleges": 0,
        "campuses": 0,
        "categories": 0,
        "dimensions": 0,
        "businesses": 0,
        "services": 0,
    }

    # -------------------------------------------------------------------------
    # 1. Platform Administrator
    # -------------------------------------------------------------------------
    admin_email = "admin@aaspaas.com"
    admin_user = db.query(User).filter(User.email == admin_email).first()
    if not admin_user:
        admin_user = User(
            id=uuid4(),
            email=admin_email,
            phone="+91 99999 00000",
            password_hash=get_password_hash("AdminPassword123!"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            is_email_verified=True,
            is_phone_verified=True,
        )
        db.add(admin_user)
        stats["users"] += 1
        logger.info(f"Created platform admin: {admin_email}")

    # -------------------------------------------------------------------------
    # 2. Pilot College: MIT AOE
    # -------------------------------------------------------------------------
    college_domain = "mitaoe.ac.in"
    college = db.query(College).filter(College.email_domain == college_domain).first()
    if not college:
        college = College(
            id=uuid4(),
            name="MIT Academy of Engineering",
            short_name="MIT AOE",
            email_domain=college_domain,
            website_url="https://mitaoe.ac.in",
            status=CollegeStatus.ACTIVE,
        )
        db.add(college)
        db.flush()
        stats["colleges"] += 1
        logger.info("Created pilot college: MIT Academy of Engineering")

    # -------------------------------------------------------------------------
    # 3. Pilot Campus: Alandi Campus
    # -------------------------------------------------------------------------
    campus = (
        db.query(Campus)
        .filter(Campus.college_id == college.id, Campus.name == "Alandi Campus")
        .first()
    )
    if not campus:
        campus = Campus(
            id=uuid4(),
            college_id=college.id,
            name="Alandi Campus",
            address="Alandi Road, Pune, Maharashtra 412105",
            latitude=Decimal("18.67560000"),
            longitude=Decimal("73.88900000"),
            radius_meters=3000,
        )
        db.add(campus)
        db.flush()
        stats["campuses"] += 1
        logger.info("Created pilot campus: Alandi Campus")

    # -------------------------------------------------------------------------
    # 4. Hierarchical Categories
    # -------------------------------------------------------------------------
    category_tree = [
        {
            "name": "Food & Dining",
            "slug": "food-dining",
            "description": "Student messes, tiffin, cafes, snacks, and restaurants",
            "order": 1,
            "children": [
                {
                    "name": "Mess & Tiffin Service",
                    "slug": "mess-tiffin",
                    "description": "Daily and monthly meal subscriptions for students",
                    "order": 1,
                    "dimensions": [
                        (
                            "Food Quality & Taste",
                            "food-quality",
                            "Taste, freshness, and quality",
                        ),
                        (
                            "Hygiene & Cleanliness",
                            "hygiene",
                            "Kitchen and dining hygiene",
                        ),
                        (
                            "Portion Size & Quantity",
                            "portion-size",
                            "Quantity and refill flexibility",
                        ),
                        (
                            "Value for Money",
                            "value-for-money",
                            "Affordability relative to quality",
                        ),
                    ],
                },
                {
                    "name": "Cafes & Fast Food",
                    "slug": "cafes-fast-food",
                    "description": "Tea, coffee, burgers, and student hangouts",
                    "order": 2,
                    "dimensions": [
                        ("Taste & Freshness", "taste", "Flavor and freshness"),
                        (
                            "Ambience & Seating",
                            "ambience",
                            "Comfortable study and hangout environment",
                        ),
                        (
                            "Service Speed",
                            "service-speed",
                            "Preparation and serving time",
                        ),
                    ],
                },
                {
                    "name": "Bakeries & Desserts",
                    "slug": "bakeries",
                    "description": "Cakes, pastries, bread, and birthday celebration treats",
                    "order": 3,
                    "dimensions": [
                        ("Freshness", "freshness", "Product freshness"),
                        ("Variety", "variety", "Product selection"),
                    ],
                },
            ],
        },
        {
            "name": "Academics & Printing",
            "slug": "academics-printing",
            "description": "Photocopy, spiral binding, stationery, and course materials",
            "order": 2,
            "children": [
                {
                    "name": "Xerox & Digital Printing",
                    "slug": "xerox-printing",
                    "description": "Assignment printouts, project binding, and photocopies",
                    "order": 1,
                    "dimensions": [
                        (
                            "Print Clarity & Quality",
                            "print-quality",
                            "Sharpness, paper grade, color fidelity",
                        ),
                        (
                            "Turnaround Speed",
                            "speed",
                            "Quick service during deadline rushes",
                        ),
                        (
                            "Pricing Fairness",
                            "pricing",
                            "Transparent per-page rates for students",
                        ),
                    ],
                },
                {
                    "name": "Stationery & Supplies",
                    "slug": "stationery",
                    "description": "Pens, drawing sheets, notebooks, and calculator supplies",
                    "order": 2,
                    "dimensions": [
                        (
                            "Stock Availability",
                            "availability",
                            "Availability of engineering supplies",
                        ),
                        ("Pricing", "pricing", "Fair student pricing"),
                    ],
                },
            ],
        },
        {
            "name": "Accommodation & Living",
            "slug": "accommodation",
            "description": "Student hostels, PG options, and flats",
            "order": 3,
            "children": [
                {
                    "name": "PG & Hostels",
                    "slug": "pg-hostels",
                    "description": "Paying guest accommodation and private student hostels",
                    "order": 1,
                    "dimensions": [
                        (
                            "Room Condition & Space",
                            "room-condition",
                            "Ventilation, space, furnishings",
                        ),
                        (
                            "Safety & Security",
                            "security",
                            "CCTV, wardens, gate timings",
                        ),
                        (
                            "Amenities & WiFi",
                            "amenities",
                            "Water, electricity, high-speed WiFi",
                        ),
                        (
                            "Owner / Warden Behavior",
                            "owner-behavior",
                            "Fairness and deposit refunds",
                        ),
                    ],
                },
            ],
        },
        {
            "name": "Daily Essentials & Laundry",
            "slug": "daily-essentials",
            "description": "Laundry, dry cleaning, supermarkets, and general stores",
            "order": 4,
            "children": [
                {
                    "name": "Laundry & Dry Cleaning",
                    "slug": "laundry",
                    "description": "Wash, fold, and iron services for hostelers",
                    "order": 1,
                    "dimensions": [
                        (
                            "Washing & Ironing Quality",
                            "wash-quality",
                            "Cleanliness, fabric safety, crisp iron",
                        ),
                        (
                            "Delivery Timeliness",
                            "punctuality",
                            "On-time delivery without lost clothes",
                        ),
                    ],
                },
            ],
        },
        {
            "name": "Repairs & Services",
            "slug": "repairs-services",
            "description": "Mobile, laptop, electronics, and vehicle maintenance",
            "order": 5,
            "children": [
                {
                    "name": "Mobile & Laptop Repair",
                    "slug": "mobile-laptop-repair",
                    "description": "Screen replacement, OS installation, and hardware repair",
                    "order": 1,
                    "dimensions": [
                        (
                            "Repair Reliability",
                            "reliability",
                            "Long-term fix without recurring defects",
                        ),
                        (
                            "Transparency & Honesty",
                            "honesty",
                            "Genuine parts and honest diagnostics",
                        ),
                    ],
                },
            ],
        },
    ]

    cat_map: Dict[str, Category] = {}

    for p_data in category_tree:
        parent = db.query(Category).filter(Category.slug == p_data["slug"]).first()
        if not parent:
            parent = Category(
                id=uuid4(),
                name=p_data["name"],
                slug=p_data["slug"],
                description=p_data.get("description"),
                display_order=p_data["order"],
                is_active=True,
            )
            db.add(parent)
            db.flush()
            stats["categories"] += 1
        cat_map[p_data["slug"]] = parent

        for c_data in p_data.get("children", []):
            child = db.query(Category).filter(Category.slug == c_data["slug"]).first()
            if not child:
                child = Category(
                    id=uuid4(),
                    name=c_data["name"],
                    slug=c_data["slug"],
                    description=c_data.get("description"),
                    parent_id=parent.id,
                    display_order=c_data["order"],
                    is_active=True,
                )
                db.add(child)
                db.flush()
                stats["categories"] += 1
            cat_map[c_data["slug"]] = child

            # Seed Rating Dimensions for child categories
            for dim_idx, (d_name, d_slug, d_desc) in enumerate(
                c_data.get("dimensions", [])
            ):
                existing_dim = (
                    db.query(RatingDimension)
                    .filter(
                        RatingDimension.category_id == child.id,
                        RatingDimension.slug == d_slug,
                    )
                    .first()
                )
                if not existing_dim:
                    dim = RatingDimension(
                        id=uuid4(),
                        category_id=child.id,
                        name=d_name,
                        slug=d_slug,
                        description=d_desc,
                        display_order=dim_idx + 1,
                    )
                    db.add(dim)
                    stats["dimensions"] += 1

    # -------------------------------------------------------------------------
    # 5. Pilot Businesses & Owners
    # -------------------------------------------------------------------------
    sample_merchants = [
        {
            "owner_email": "annapurna.mess@aaspaas.com",
            "owner_phone": "+91 98765 11111",
            "owner_name": "Ramesh Patil",
            "biz_name": "Annapurna Student Mess",
            "category_slug": "mess-tiffin",
            "description": "Clean, hygienic, homestyle vegetarian student meals with unlimited chapatis and rice.",
            "address": "Opposite MIT AOE Gate 2, Alandi",
            "lat": Decimal("18.67620000"),
            "lng": Decimal("73.88950000"),
            "price_level": PriceLevel.LEVEL_1,
            "student_discount": True,
            "discount_desc": "Flat 10% off on monthly prepaid mess membership for verified MIT AOE students.",
            "services": [
                (
                    "Monthly Unlimited Veg Mess",
                    Decimal("2800.00"),
                    "month",
                    "Two meals daily (lunch & dinner)",
                ),
                (
                    "Special Student Thali",
                    Decimal("90.00"),
                    "plate",
                    "Includes sweet, papad, paneer sabzi, unlimited dal-rice",
                ),
                (
                    "Regular Daily Thali",
                    Decimal("70.00"),
                    "plate",
                    "Unlimited chapatis, 2 vegetables, dal, rice",
                ),
            ],
            "hours": [
                (0, time(7, 30), time(22, 30), False),
                (1, time(7, 30), time(22, 30), False),
                (2, time(7, 30), time(22, 30), False),
                (3, time(7, 30), time(22, 30), False),
                (4, time(7, 30), time(22, 30), False),
                (5, time(7, 30), time(22, 30), False),
                (6, time(7, 30), time(22, 30), False),
            ],
        },
        {
            "owner_email": "campus.xerox@aaspaas.com",
            "owner_phone": "+91 98765 22222",
            "owner_name": "Sunil Shinde",
            "biz_name": "Alandi Campus Cyber & Xerox",
            "category_slug": "xerox-printing",
            "description": (
                "High-speed laser printing, assignment xerox, engineering drawing sheets, and soft/hard binding."
            ),
            "address": "Near MIT AOE Gate 1, Alandi",
            "lat": Decimal("18.67500000"),
            "lng": Decimal("73.88850000"),
            "price_level": PriceLevel.LEVEL_1,
            "student_discount": True,
            "discount_desc": "Free spiral binding on project reports exceeding 100 pages.",
            "services": [
                (
                    "B&W Photocopy / Print",
                    Decimal("1.50"),
                    "page",
                    "Single side 75 GSM paper",
                ),
                (
                    "Color Laser Print",
                    Decimal("5.00"),
                    "page",
                    "High-definition diagram print",
                ),
                (
                    "Project Spiral Binding",
                    Decimal("40.00"),
                    "report",
                    "Plastic cover with clear front",
                ),
            ],
            "hours": [
                (0, time(9, 0), time(20, 0), False),
                (1, time(8, 0), time(21, 0), False),
                (2, time(8, 0), time(21, 0), False),
                (3, time(8, 0), time(21, 0), False),
                (4, time(8, 0), time(21, 0), False),
                (5, time(8, 0), time(21, 0), False),
                (6, time(8, 0), time(21, 0), False),
            ],
        },
        {
            "owner_email": "chai.adda@aaspaas.com",
            "owner_phone": "+91 98765 33333",
            "owner_name": "Vikas Jadhav",
            "biz_name": "Engineering Chai Adda & Snacks",
            "category_slug": "cafes-fast-food",
            "description": "Special Adrak-Elaichi Chai, fresh bun maska, samosas, and evening study snacks.",
            "address": "Shree Nagar, 100m from MIT AOE, Alandi",
            "lat": Decimal("18.67580000"),
            "lng": Decimal("73.88920000"),
            "price_level": PriceLevel.LEVEL_1,
            "student_discount": True,
            "discount_desc": "Combo offer: Bun Maska + Special Chai for ₹35 (regular ₹40).",
            "services": [
                (
                    "Special Masala Chai",
                    Decimal("15.00"),
                    "cup",
                    "Freshly brewed kulhad ginger-cardamom tea",
                ),
                ("Bun Maska", Decimal("25.00"), "plate", "Fresh bun with Amul butter"),
                (
                    "Hot Samosa (2 pcs)",
                    Decimal("30.00"),
                    "plate",
                    "Served with sweet tamarind and green chutney",
                ),
            ],
            "hours": [
                (0, time(6, 30), time(23, 0), False),
                (1, time(6, 30), time(23, 0), False),
                (2, time(6, 30), time(23, 0), False),
                (3, time(6, 30), time(23, 0), False),
                (4, time(6, 30), time(23, 0), False),
                (5, time(6, 30), time(23, 0), False),
                (6, time(6, 30), time(23, 0), False),
            ],
        },
    ]

    for m in sample_merchants:
        # Create Owner User
        owner = db.query(User).filter(User.email == m["owner_email"]).first()
        if not owner:
            owner = User(
                id=uuid4(),
                email=m["owner_email"],
                phone=m["owner_phone"],
                password_hash=get_password_hash("OwnerPassword123!"),
                role=UserRole.OWNER,
                status=UserStatus.ACTIVE,
                is_email_verified=True,
                is_phone_verified=True,
            )
            db.add(owner)
            db.flush()
            stats["users"] += 1
            logger.info(f"Created merchant owner: {m['owner_email']}")

        # Create Business
        biz = (
            db.query(Business)
            .filter(Business.owner_id == owner.id, Business.deleted_at.is_(None))
            .first()
        )
        if not biz:
            biz = Business(
                id=uuid4(),
                owner_id=owner.id,
                campus_id=campus.id,
                name=m["biz_name"],
                description=m["description"],
                phone=m["owner_phone"],
                email=m["owner_email"],
                address=m["address"],
                latitude=m["lat"],
                longitude=m["lng"],
                status=BusinessStatus.ACTIVE,
                verification_status=BusinessVerificationStatus.VERIFIED,
                price_level=m["price_level"],
                student_discount=m["student_discount"],
                student_discount_description=m["discount_desc"],
            )
            db.add(biz)
            db.flush()
            stats["businesses"] += 1

            # Associate category
            target_category = cat_map.get(m["category_slug"])
            if target_category:
                db.execute(
                    business_categories.insert().values(
                        business_id=biz.id,
                        category_id=target_category.id,
                    )
                )

            # Operating hours
            for day_idx, o_time, c_time, is_c in m["hours"]:
                h_rec = BusinessHours(
                    id=uuid4(),
                    business_id=biz.id,
                    day_of_week=day_idx,
                    open_time=o_time,
                    close_time=c_time,
                    is_closed=is_c,
                )
                db.add(h_rec)

            # Services & initial price histories
            for s_name, s_price, s_unit, s_desc in m["services"]:
                svc = Service(
                    id=uuid4(),
                    business_id=biz.id,
                    name=s_name,
                    price=s_price,
                    currency="INR",
                    unit=s_unit,
                    description=s_desc,
                    is_active=True,
                )
                db.add(svc)
                db.flush()
                stats["services"] += 1

                # Record baseline price history
                ph = ServicePriceHistory(
                    id=uuid4(),
                    service_id=svc.id,
                    price=s_price,
                    currency="INR",
                    effective_from=svc.created_at,
                    effective_to=None,
                    changed_by=owner.id,
                )
                db.add(ph)

            logger.info(f"Seeded business: {m['biz_name']} with hours & services")

    db.commit()
    return stats


def run_seed_cli():
    """Command-line entrypoint for database seeding."""
    db = SessionLocal()
    try:
        logger.info("Starting AAS PAAS Pilot Campus Data Seeding...")
        results = seed_database(db)
        logger.info(f"Seeding completed successfully: {results}")
    except Exception as e:
        db.rollback()
        logger.error(f"Seeding failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_seed_cli()
