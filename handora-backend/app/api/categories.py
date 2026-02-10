

"""
PUBLIC API - Categories (Yalnız GET əməliyyatları)
Users can only VIEW categories, not modify them
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.product import Category, Product
from app.schemas.product import (
    ParentCategoryResponse,
    SubCategoryResponse,
    SubCategoryWithParent
)

router = APIRouter(prefix="/categories", tags=["Categories"])


# ==================== PARENT CATEGORY PUBLIC ENDPOINTS ====================

@router.get(
    "",
    response_model=List[ParentCategoryResponse],
    summary="Bütün əsas kateqoriyaları gətir"
)
def get_parent_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    PUBLIC - Bütün əsas kateqoriyaları qaytarır (parent_id = NULL olan).
    """
    categories = db.query(Category)\
        .filter(Category.parent_id == None)\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return categories


@router.get(
    "/{category_id}",
    response_model=ParentCategoryResponse,
    summary="ID-yə görə əsas kateqoriya gətir"
)
def get_parent_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """
    PUBLIC - Verilən ID-yə görə əsas kateqoriya qaytarır.
    """
    category = db.query(Category)\
        .filter(Category.id == category_id, Category.parent_id == None)\
        .first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID {category_id} ilə əsas kateqoriya tapılmadı"
        )
    
    return category


@router.get(
    "/{parent_id}/subcategories",
    response_model=List[SubCategoryResponse],
    summary="Əsas kateqoriyanın bütün alt kateqoriyalarını gətir"
)
def get_subcategories_by_parent(
    parent_id: int,
    db: Session = Depends(get_db)
):
    """
    PUBLIC - Verilən əsas kateqoriyanın bütün alt kateqoriyalarını qaytarır.
    """
    # Verify parent exists
    parent = db.query(Category)\
        .filter(Category.id == parent_id, Category.parent_id == None)\
        .first()
    
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID {parent_id} ilə əsas kateqoriya tapılmadı"
        )
    
    subcategories = db.query(Category)\
        .filter(Category.parent_id == parent_id)\
        .all()
    
    return subcategories


# ==================== SUBCATEGORY PUBLIC ENDPOINTS ====================

@router.get(
    "/subcategories/all",
    response_model=List[SubCategoryWithParent],
    summary="Bütün alt kateqoriyaları gətir"
)
def get_all_subcategories(
    parent_id: Optional[int] = Query(None, description="Əsas kateqoriya ID-si ilə filter"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    PUBLIC - Bütün alt kateqoriyaları qaytarır.
    parent_id parametri ilə müəyyən əsas kateqoriyanın alt kateqoriyalarını filtrləmək olar.
    """
    query = db.query(Category).filter(Category.parent_id != None)
    
    if parent_id:
        query = query.filter(Category.parent_id == parent_id)
    
    subcategories = query.offset(skip).limit(limit).all()
    
    return subcategories


@router.get(
    "/subcategories/{subcategory_id}",
    response_model=SubCategoryWithParent,
    summary="ID-yə görə alt kateqoriya gətir"
)
def get_subcategory(
    subcategory_id: int,
    db: Session = Depends(get_db)
):
    """
    PUBLIC - Verilən ID-yə görə alt kateqoriya qaytarır.
    """
    subcategory = db.query(Category)\
        .filter(Category.id == subcategory_id, Category.parent_id != None)\
        .first()
    
    if not subcategory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID {subcategory_id} ilə alt kateqoriya tapılmadı"
        )
    
    return subcategory


# ==================== TREE VIEW & STATISTICS ====================

@router.get(
    "/tree/all",
    summary="Bütün kateqoriyaları ağac strukturunda gətir"
)
def get_categories_tree(db: Session = Depends(get_db)):
    """
    PUBLIC - Bütün əsas kateqoriyaları və onların alt kateqoriyalarını
    ağac strukturunda qaytarır. Hər kateqoriya üçün məhsul sayını da əlavə edir.
    """
    # Get all parent categories
    parent_categories = db.query(Category)\
        .filter(Category.parent_id == None)\
        .all()
    
    result = []
    
    for parent in parent_categories:
        # Get subcategories for this parent
        subcategories = db.query(Category)\
            .filter(Category.parent_id == parent.id)\
            .all()
        
        # Build subcategory tree with product counts
        subcategory_tree = []
        total_products = 0
        
        for sub in subcategories:
            # Count products in this subcategory
            products_count = db.query(Product)\
                .filter(Product.category_id == sub.id)\
                .count()
            
            total_products += products_count
            
            subcategory_tree.append({
                "id": sub.id,
                "name_az": sub.name_az,
                "name_en": sub.name_en,
                "name_ru": sub.name_ru,
                "slug": sub.slug,
                "products_count": products_count
            })
        
        # Build parent category tree
        result.append({
            "id": parent.id,
            "name_az": parent.name_az,
            "name_en": parent.name_en,
            "name_ru": parent.name_ru,
            "slug": parent.slug,
            "subcategories": subcategory_tree,
            "total_products_count": total_products
        })
    
    return result