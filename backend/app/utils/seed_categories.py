"""Seed Categories Utility

Populate initial hierarchical categories for campus businesses.
"""

from sqlalchemy.orm import Session
from app.models.category import Category
from app.services.category_service import CategoryService
from app.schemas.category import CategoryCreate


INITIAL_TAXONOMY = [
    {
        "name": "Food & Dining",
        "slug": "food-dining",
        "description": "Student messes, cafes, restaurants, and snack points",
        "icon": "restaurant",
        "display_order": 1,
        "children": [
            {
                "name": "Mess",
                "slug": "mess",
                "description": "Daily student dining mess services",
            },
            {
                "name": "Cafe",
                "slug": "cafe",
                "description": "Coffee shops and casual hangouts",
            },
            {
                "name": "Restaurant",
                "slug": "restaurant",
                "description": "Dine-in family and student restaurants",
            },
            {
                "name": "Bakery & Desserts",
                "slug": "bakery",
                "description": "Cakes, breads, pastries, and ice creams",
            },
            {
                "name": "Fast Food & Snacks",
                "slug": "fast-food",
                "description": "Quick bites, wraps, and street food",
            },
            {
                "name": "Tea & Juice",
                "slug": "tea-juice",
                "description": "Chai tapris and fresh juice centers",
            },
        ],
    },
    {
        "name": "Academics & Printing",
        "slug": "academics-printing",
        "description": "Printing, stationery, study materials, and technical services",
        "icon": "school",
        "display_order": 2,
        "children": [
            {
                "name": "Stationery & Xerox",
                "slug": "stationery-xerox",
                "description": "Printing, photocopying, and stationery",
            },
            {
                "name": "Book Store",
                "slug": "book-store",
                "description": "Engineering textbooks and reference materials",
            },
            {
                "name": "Laptop & Mobile Repair",
                "slug": "tech-repair",
                "description": "Computer hardware, smartphone service and accessories",
            },
        ],
    },
    {
        "name": "Daily Essentials",
        "slug": "daily-essentials",
        "description": "Everyday services and general utility shops",
        "icon": "storefront",
        "display_order": 3,
        "children": [
            {
                "name": "Laundry & Ironing",
                "slug": "laundry",
                "description": "Clothes washing, dry cleaning, and pressing",
            },
            {
                "name": "Salon & Barber",
                "slug": "salon-barber",
                "description": "Haircuts, grooming, and styling for students",
            },
            {
                "name": "Grocery & General Store",
                "slug": "grocery",
                "description": "Packaged goods, toiletries, and supplies",
            },
            {
                "name": "Tailor",
                "slug": "tailor",
                "description": "Alterations and stitching",
            },
        ],
    },
    {
        "name": "Health & Medical",
        "slug": "health-medical",
        "description": "Pharmacies, clinics, and medical practitioners",
        "icon": "local_hospital",
        "display_order": 4,
        "children": [
            {
                "name": "Pharmacy / Medical",
                "slug": "pharmacy",
                "description": "Medicines and first-aid supplies",
            },
            {
                "name": "Doctor Clinic",
                "slug": "clinic",
                "description": "General physicians and emergency consulting",
            },
            {
                "name": "Dental Clinic",
                "slug": "dental",
                "description": "Dentists and oral healthcare",
            },
        ],
    },
    {
        "name": "Fitness & Sports",
        "slug": "fitness-sports",
        "description": "Gyms, yoga centres, and sports grounds",
        "icon": "fitness_center",
        "display_order": 5,
        "children": [
            {
                "name": "Gym & Fitness",
                "slug": "gym",
                "description": "Strength training and cardio gyms",
            },
            {
                "name": "Sports Turf",
                "slug": "sports-turf",
                "description": "Cricket, football turf rentals",
            },
        ],
    },
    {
        "name": "Housing & Stay",
        "slug": "housing-stay",
        "description": "Student accommodations near campus",
        "icon": "home",
        "display_order": 6,
        "children": [
            {
                "name": "Hostel & PG",
                "slug": "hostel-pg",
                "description": "Paying guest accommodation for college students",
            },
            {
                "name": "Room Rental",
                "slug": "room-rental",
                "description": "Flats and rooms for rent near campus",
            },
        ],
    },
]


def seed_categories(db: Session) -> int:
    """Seed initial categories if not already present.

    Args:
        db: Database session

    Returns:
        Number of categories created
    """
    created_count = 0

    for root_data in INITIAL_TAXONOMY:
        root = db.query(Category).filter(Category.slug == root_data["slug"]).first()
        if not root:
            root_create = CategoryCreate(
                name=root_data["name"],
                slug=root_data["slug"],
                description=root_data["description"],
                icon=root_data.get("icon"),
                display_order=root_data.get("display_order", 0),
                is_active=True,
            )
            root = CategoryService.create_category(root_create, db)
            created_count += 1

        for child_data in root_data.get("children", []):
            child = (
                db.query(Category).filter(Category.slug == child_data["slug"]).first()
            )
            if not child:
                child_create = CategoryCreate(
                    name=child_data["name"],
                    slug=child_data["slug"],
                    description=child_data["description"],
                    parent_id=root.id,
                    display_order=0,
                    is_active=True,
                )
                CategoryService.create_category(child_create, db)
                created_count += 1

    return created_count
