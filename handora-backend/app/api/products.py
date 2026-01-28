from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.product import Product, Category, Brand
from app.schemas.product import ProductResponse, ProductDetail, CategoryResponse, BrandResponse

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("", response_model=List[ProductResponse])
def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category_id: Optional[int] = None,
    brand_id: Optional[int] = None,
    is_sale: Optional[bool] = None,
    is_new: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Product)
    
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if brand_id:
        query = query.filter(Product.brand_id == brand_id)
    if is_sale is not None:
        query = query.filter(Product.is_sale == is_sale)
    if is_new is not None:
        query = query.filter(Product.is_new == is_new)
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Product.name_az.ilike(search_filter)) |
            (Product.name_en.ilike(search_filter)) |
            (Product.name_ru.ilike(search_filter))
        )
    
    return query.offset(skip).limit(limit).all()

@router.get("/{product_id}", response_model=ProductDetail)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Məhsul tapılmadı")
    return product

@router.get("/search", response_model=List[ProductResponse])
def search_products(q: str, db: Session = Depends(get_db)):
    search_filter = f"%{q}%"
    return db.query(Product).filter(
        (Product.name_az.ilike(search_filter)) |
        (Product.name_en.ilike(search_filter)) |
        (Product.name_ru.ilike(search_filter)) |
        (Product.description_az.ilike(search_filter))
    ).limit(20).all()
