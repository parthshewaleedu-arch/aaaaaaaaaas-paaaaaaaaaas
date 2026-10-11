"""Category endpoints"""

from typing import Optional, Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user
from app.core.database import get_db
from app.models.user import User, UserRole
from app.schemas.category import (
    CategoryCreate,
    CategoryResponse,
    CategoryTreeResponse,
    CategoryUpdate,
)
from app.services.category_service import CategoryService

router = APIRouter()


@router.get(
    "",
    response_model=Union[list[CategoryTreeResponse], list[CategoryResponse]],
    summary="List categories",
)
async def list_categories(
    tree: bool = Query(False, description="Return as hierarchical tree"),
    parent_id: Optional[UUID] = Query(None, description="Filter by parent category ID"),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    root_only: bool = Query(False, description="Return only top-level categories"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """
    List categories.
    If tree=true, returns full hierarchical category tree with nested children.
    Otherwise returns flat list of categories matching filters.
    Public endpoint.
    """
    if tree:
        return CategoryService.get_category_tree(
            db=db, active_only=is_active if is_active is not None else True
        )

    return CategoryService.list_categories(
        db=db,
        parent_id=parent_id,
        is_active=is_active,
        root_only=root_only,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{category_id}",
    response_model=CategoryTreeResponse,
    summary="Get category details",
)
async def get_category(
    category_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get a category by ID including its children subcategories.
    Public endpoint.
    """
    category = CategoryService.get_category_by_id(category_id, db)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    # Convert children
    children = CategoryService.list_categories(
        db=db, parent_id=category.id, is_active=True
    )
    return CategoryTreeResponse(
        id=category.id,
        name=category.name,
        slug=category.slug,
        description=category.description,
        icon=category.icon,
        parent_id=category.parent_id,
        is_active=category.is_active,
        display_order=category.display_order,
        children=[CategoryTreeResponse.model_validate(c) for c in children],
    )


@router.get(
    "/slug/{slug}",
    response_model=CategoryTreeResponse,
    summary="Get category by slug",
)
async def get_category_by_slug(
    slug: str,
    db: Session = Depends(get_db),
):
    """
    Get a category by its slug including its children.
    Public endpoint.
    """
    category = CategoryService.get_category_by_slug(slug, db)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with slug '{slug}' not found",
        )

    children = CategoryService.list_categories(
        db=db, parent_id=category.id, is_active=True
    )
    return CategoryTreeResponse(
        id=category.id,
        name=category.name,
        slug=category.slug,
        description=category.description,
        icon=category.icon,
        parent_id=category.parent_id,
        is_active=category.is_active,
        display_order=category.display_order,
        children=[CategoryTreeResponse.model_validate(c) for c in children],
    )


# Admin endpoints


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create category (admin)",
)
async def create_category(
    category_data: CategoryCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Create a new category.
    Requires ADMIN role.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    try:
        category = CategoryService.create_category(category_data, db)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return category


@router.patch(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Update category (admin)",
)
async def update_category(
    category_id: UUID,
    category_data: CategoryUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Update category details or hierarchy.
    Requires ADMIN role.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    try:
        updated = CategoryService.update_category(category_id, category_data, db)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    return updated


@router.delete(
    "/{category_id}",
    summary="Delete or deactivate category (admin)",
)
async def delete_category(
    category_id: UUID,
    hard: bool = Query(False, description="Hard delete instead of deactivating"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Deactivate or permanently delete a category.
    Requires ADMIN role.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    deleted = CategoryService.delete_category(category_id, db, soft=not hard)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    return {
        "success": True,
        "message": f"Category {'deleted' if hard else 'deactivated'} successfully",
    }
