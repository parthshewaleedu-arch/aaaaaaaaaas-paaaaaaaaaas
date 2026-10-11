"""Unit tests for CategoryService and category taxonomy."""

from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.services.category_service import CategoryService


def test_slugify():
    """Test string slugification logic."""
    assert CategoryService.slugify("Food & Dining") == "food-dining"
    assert CategoryService.slugify("Mess (Alandi)") == "mess-alandi"
    assert CategoryService.slugify("Special-Tea & Snacks!") == "special-tea-snacks"
    assert CategoryService.slugify("   Spaces   ") == "spaces"
    assert CategoryService.slugify("") == "category"


def test_generate_unique_slug_no_collision():
    """Test generating a slug when no conflict exists."""
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    slug = CategoryService.generate_unique_slug("Food & Dining", mock_db)
    assert slug == "food-dining"


def test_generate_unique_slug_with_collision():
    """Test generating an incremented slug when conflict exists."""
    mock_db = MagicMock()
    # First call returns existing, second call returns None
    existing = Category(name="Food", slug="food")
    mock_db.query.return_value.filter.return_value.first.side_effect = [existing, None]

    slug = CategoryService.generate_unique_slug("Food", mock_db)
    assert slug == "food-1"


def test_create_category_success():
    """Test creating a category successfully."""
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    data = CategoryCreate(
        name="Student Mess",
        description="Mess dining for students",
        icon="restaurant",
        display_order=1,
    )

    cat = CategoryService.create_category(data, mock_db)
    assert cat.name == "Student Mess"
    assert cat.slug == "student-mess"
    assert cat.is_active is True
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


def test_create_category_invalid_parent():
    """Test creating a category with non-existent parent raises ValueError."""
    mock_db = MagicMock()
    # Parent lookup returns None
    mock_db.query.return_value.filter.return_value.first.return_value = None

    data = CategoryCreate(
        name="Fast Food",
        parent_id=uuid4(),
    )

    with pytest.raises(ValueError, match="Parent category not found"):
        CategoryService.create_category(data, mock_db)


def test_create_category_duplicate_slug_raises():
    """Test creating a category with explicit duplicate slug raises ValueError."""
    mock_db = MagicMock()
    existing = Category(name="Old Category", slug="custom-slug")
    mock_db.query.return_value.filter.return_value.first.return_value = existing

    data = CategoryCreate(
        name="New Category",
        slug="custom-slug",
    )

    with pytest.raises(ValueError, match="already exists"):
        CategoryService.create_category(data, mock_db)


def test_get_category_tree():
    """Test hierarchical tree generation."""
    mock_db = MagicMock()

    root1_id = uuid4()
    child1_id = uuid4()
    root2_id = uuid4()

    cat_root1 = Category(
        id=root1_id,
        name="Food",
        slug="food",
        parent_id=None,
        is_active=True,
        display_order=1,
    )
    cat_child1 = Category(
        id=child1_id,
        name="Mess",
        slug="mess",
        parent_id=root1_id,
        is_active=True,
        display_order=1,
    )
    cat_root2 = Category(
        id=root2_id,
        name="Health",
        slug="health",
        parent_id=None,
        is_active=True,
        display_order=2,
    )

    mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
        cat_root1,
        cat_child1,
        cat_root2,
    ]

    tree = CategoryService.get_category_tree(mock_db, active_only=True)
    assert len(tree) == 2
    assert tree[0]["name"] == "Food"
    assert len(tree[0]["children"]) == 1
    assert tree[0]["children"][0]["name"] == "Mess"
    assert tree[1]["name"] == "Health"
    assert len(tree[1]["children"]) == 0


def test_update_category_self_parent_raises():
    """Test setting category as its own parent raises ValueError."""
    mock_db = MagicMock()
    cat_id = uuid4()
    existing = Category(id=cat_id, name="Food", slug="food")
    mock_db.query.return_value.filter.return_value.first.return_value = existing

    update_data = CategoryUpdate(parent_id=cat_id)
    with pytest.raises(ValueError, match="Category cannot be its own parent"):
        CategoryService.update_category(cat_id, update_data, mock_db)


def test_update_category_circular_dependency_raises():
    """Test circular hierarchy raises ValueError."""
    mock_db = MagicMock()
    cat_a_id = uuid4()
    cat_b_id = uuid4()

    # Category A currently parent of Category B
    cat_a = Category(id=cat_a_id, name="A", slug="a", parent_id=None)
    cat_b = Category(id=cat_b_id, name="B", slug="b", parent_id=cat_a_id)

    # When trying to set A's parent to B:
    # 1. query for cat_a returns cat_a
    # 2. query for parent (cat_b) returns cat_b
    # 3. check ancestors of cat_b: cat_b's parent is cat_a, which equals cat_a_id -> cycle!
    mock_db.query.return_value.filter.return_value.first.side_effect = [
        cat_a,  # finding target category
        cat_b,  # finding new parent
        cat_a,  # finding parent of cat_b in ancestor loop
    ]

    update_data = CategoryUpdate(parent_id=cat_b_id)
    with pytest.raises(ValueError, match="Circular dependency detected"):
        CategoryService.update_category(cat_a_id, update_data, mock_db)


def test_delete_category_soft():
    """Test soft deleting a category sets is_active to False on parent and children."""
    mock_db = MagicMock()
    cat_id = uuid4()
    parent = Category(id=cat_id, name="Food", is_active=True)
    child = Category(id=uuid4(), name="Mess", parent_id=cat_id, is_active=True)

    mock_db.query.return_value.filter.return_value.first.return_value = parent
    mock_db.query.return_value.filter.return_value.all.return_value = [child]

    result = CategoryService.delete_category(cat_id, mock_db, soft=True)
    assert result is True
    assert parent.is_active is False
    assert child.is_active is False
    mock_db.commit.assert_called_once()
