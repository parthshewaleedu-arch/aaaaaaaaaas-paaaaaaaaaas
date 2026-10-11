"""Integration tests for CategoryService."""

from sqlalchemy.orm import Session

from app.schemas.category import CategoryCreate, CategoryUpdate
from app.services.category_service import CategoryService


def test_create_category_db(db: Session):
    """Test creating a category in database."""
    category_data = CategoryCreate(
        name="Food & Dining",
        description="All food services",
        icon="restaurant",
        display_order=1,
    )
    category = CategoryService.create_category(category_data, db)

    assert category.id is not None
    assert category.name == "Food & Dining"
    assert category.slug == "food-dining"
    assert category.is_active is True
    assert category.parent_id is None


def test_create_child_category_db(db: Session):
    """Test creating child category linked to parent."""
    parent_data = CategoryCreate(name="Health", slug="health")
    parent = CategoryService.create_category(parent_data, db)

    child_data = CategoryCreate(
        name="Pharmacy",
        parent_id=parent.id,
    )
    child = CategoryService.create_category(child_data, db)

    assert child.parent_id == parent.id
    assert child.slug == "pharmacy"


def test_get_category_by_id_db(db: Session):
    """Test retrieving category by ID."""
    cat = CategoryService.create_category(CategoryCreate(name="Books"), db)
    fetched = CategoryService.get_category_by_id(cat.id, db)

    assert fetched is not None
    assert fetched.name == "Books"


def test_get_category_by_slug_db(db: Session):
    """Test retrieving category by slug."""
    cat = CategoryService.create_category(CategoryCreate(name="Hostel"), db)
    fetched = CategoryService.get_category_by_slug("hostel", db)

    assert fetched is not None
    assert fetched.id == cat.id


def test_list_categories_db(db: Session):
    """Test listing categories."""
    CategoryService.create_category(CategoryCreate(name="Cat 1", display_order=2), db)
    CategoryService.create_category(CategoryCreate(name="Cat 2", display_order=1), db)

    all_cats = CategoryService.list_categories(db)
    assert len(all_cats) >= 2


def test_update_category_db(db: Session):
    """Test updating category."""
    cat = CategoryService.create_category(CategoryCreate(name="Original Name"), db)
    updated = CategoryService.update_category(
        cat.id,
        CategoryUpdate(name="Updated Name", description="Updated Description"),
        db,
    )

    assert updated is not None
    assert updated.name == "Updated Name"
    assert updated.description == "Updated Description"


def test_delete_category_db(db: Session):
    """Test soft delete category."""
    cat = CategoryService.create_category(CategoryCreate(name="To Delete"), db)
    success = CategoryService.delete_category(cat.id, db, soft=True)

    assert success is True
    refetched = CategoryService.get_category_by_id(cat.id, db)
    assert refetched.is_active is False
