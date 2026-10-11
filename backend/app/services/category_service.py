"""Category Service

Business logic for managing business categories and category hierarchies.
"""

import re
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    """Service for category operations and hierarchical taxonomy."""

    @staticmethod
    def slugify(text: str) -> str:
        """Convert a name to a URL-friendly slug.

        Args:
            text: Category name

        Returns:
            Normalized slug string
        """
        # Convert to lowercase
        slug = text.lower().strip()
        # Replace non-alphanumeric characters with hyphens
        slug = re.sub(r"[^\w\s-]", "", slug)
        slug = re.sub(r"[\s_-]+", "-", slug)
        slug = slug.strip("-")
        return slug or "category"

    @classmethod
    def generate_unique_slug(
        cls, name: str, db: Session, exclude_id: Optional[UUID] = None
    ) -> str:
        """Generate a unique slug for a category.

        Args:
            name: Category name
            db: Database session
            exclude_id: Category ID to exclude from uniqueness check (for updates)

        Returns:
            Unique slug string
        """
        base_slug = cls.slugify(name)
        slug = base_slug
        counter = 1

        while True:
            query = db.query(Category).filter(Category.slug == slug)
            if exclude_id:
                query = query.filter(Category.id != exclude_id)
            existing = query.first()
            if not existing:
                return slug
            slug = f"{base_slug}-{counter}"
            counter += 1

    @classmethod
    def create_category(cls, category_data: CategoryCreate, db: Session) -> Category:
        """Create a new category.

        Args:
            category_data: Category creation data
            db: Database session

        Returns:
            Created Category instance
        """
        # Validate parent category if provided
        if category_data.parent_id:
            parent = (
                db.query(Category)
                .filter(Category.id == category_data.parent_id)
                .first()
            )
            if not parent:
                raise ValueError("Parent category not found")

        # Determine slug
        if category_data.slug:
            slug = cls.slugify(category_data.slug)
            existing = db.query(Category).filter(Category.slug == slug).first()
            if existing:
                raise ValueError(f"Category with slug '{slug}' already exists")
        else:
            slug = cls.generate_unique_slug(category_data.name, db)

        category = Category(
            id=uuid4(),
            name=category_data.name,
            slug=slug,
            description=category_data.description,
            icon=category_data.icon,
            parent_id=category_data.parent_id,
            is_active=category_data.is_active,
            display_order=category_data.display_order,
        )

        db.add(category)
        db.commit()

        db.refresh(category)
        return category

    @staticmethod
    def get_category_by_id(category_id: UUID, db: Session) -> Optional[Category]:
        """Get category by ID.

        Args:
            category_id: Category UUID
            db: Database session

        Returns:
            Category instance or None
        """
        return db.query(Category).filter(Category.id == category_id).first()

    @staticmethod
    def get_category_by_slug(slug: str, db: Session) -> Optional[Category]:
        """Get category by slug.

        Args:
            slug: URL slug
            db: Database session

        Returns:
            Category instance or None
        """
        return db.query(Category).filter(Category.slug == slug).first()

    @staticmethod
    def list_categories(
        db: Session,
        parent_id: Optional[UUID] = None,
        is_active: Optional[bool] = None,
        root_only: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Category]:
        """List categories with optional filters.

        Args:
            db: Database session
            parent_id: Filter by direct parent
            is_active: Filter by active status
            root_only: Only return top-level categories (parent_id is None)
            skip: Offset
            limit: Limit

        Returns:
            List of Category instances
        """
        query = db.query(Category)

        if root_only:
            query = query.filter(Category.parent_id.is_(None))
        elif parent_id is not None:
            query = query.filter(Category.parent_id == parent_id)

        if is_active is not None:
            query = query.filter(Category.is_active == is_active)

        return (
            query.order_by(Category.display_order.asc(), Category.name.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def count_categories(
        db: Session,
        parent_id: Optional[UUID] = None,
        is_active: Optional[bool] = None,
        root_only: bool = False,
    ) -> int:
        """Count categories matching filters.

        Args:
            db: Database session
            parent_id: Filter by direct parent
            is_active: Filter by active status
            root_only: Only return top-level categories

        Returns:
            Count of categories
        """
        query = db.query(Category)

        if root_only:
            query = query.filter(Category.parent_id.is_(None))
        elif parent_id is not None:
            query = query.filter(Category.parent_id == parent_id)

        if is_active is not None:
            query = query.filter(Category.is_active == is_active)

        return query.count()

    @classmethod
    def get_category_tree(cls, db: Session, active_only: bool = True) -> list[dict]:
        """Retrieve full hierarchical category tree.

        Args:
            db: Database session
            active_only: If True, only include active categories

        Returns:
            List of root category dictionaries with nested children
        """
        query = db.query(Category)
        if active_only:
            query = query.filter(Category.is_active == True)  # noqa: E712
        categories = query.order_by(
            Category.display_order.asc(), Category.name.asc()
        ).all()

        # Build mapping of parent_id -> list of child dicts
        by_id = {}
        children_map = {}

        for cat in categories:
            cat_dict = {
                "id": cat.id,
                "name": cat.name,
                "slug": cat.slug,
                "description": cat.description,
                "icon": cat.icon,
                "parent_id": cat.parent_id,
                "is_active": cat.is_active,
                "display_order": cat.display_order,
                "created_at": cat.created_at,
                "updated_at": cat.updated_at,
                "children": [],
            }
            by_id[cat.id] = cat_dict
            children_map.setdefault(cat.parent_id, []).append(cat_dict)

        # Wire children into their parents
        for parent_id, children in children_map.items():
            if parent_id in by_id:
                by_id[parent_id]["children"] = children

        # Roots are items whose parent_id is None or not in by_id
        roots = children_map.get(None, [])
        return roots

    @classmethod
    def update_category(
        cls,
        category_id: UUID,
        category_data: CategoryUpdate,
        db: Session,
    ) -> Optional[Category]:
        """Update an existing category.

        Args:
            category_id: Category UUID
            category_data: Category update data
            db: Database session

        Returns:
            Updated Category instance or None
        """
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            return None

        update_data = category_data.model_dump(exclude_unset=True)

        # Validate parent_id changes
        if "parent_id" in update_data and update_data["parent_id"] is not None:
            new_parent_id = update_data["parent_id"]
            if new_parent_id == category_id:
                raise ValueError("Category cannot be its own parent")

            parent = db.query(Category).filter(Category.id == new_parent_id).first()
            if not parent:
                raise ValueError("Parent category not found")

            # Check for circular ancestry
            curr = parent
            while curr:
                if curr.id == category_id:
                    raise ValueError(
                        "Circular dependency detected in category hierarchy"
                    )
                if curr.parent_id:
                    curr = (
                        db.query(Category).filter(Category.id == curr.parent_id).first()
                    )
                else:
                    curr = None

        # Validate or normalize slug
        if "slug" in update_data and update_data["slug"]:
            slug = cls.slugify(update_data["slug"])
            existing = (
                db.query(Category)
                .filter(Category.slug == slug, Category.id != category_id)
                .first()
            )
            if existing:
                raise ValueError(f"Category with slug '{slug}' already exists")
            update_data["slug"] = slug

        for field, value in update_data.items():
            setattr(category, field, value)

        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def delete_category(category_id: UUID, db: Session, soft: bool = True) -> bool:
        """Delete or deactivate a category.

        Args:
            category_id: Category UUID
            db: Database session
            soft: If True, set is_active=False. If False, remove from DB.

        Returns:
            True if deleted, False if not found
        """
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            return False

        if soft:
            category.is_active = False
            # Also deactivate all direct and indirect children
            children = (
                db.query(Category).filter(Category.parent_id == category_id).all()
            )
            for child in children:
                child.is_active = False
            db.commit()
        else:
            db.delete(category)
            db.commit()

        return True
