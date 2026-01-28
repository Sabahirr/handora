from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.product import Category, Product
from app.schemas.product import CategoryResponse, ProductResponse

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.get("", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()

@router.get("/{category_id}/products", response_model=List[ProductResponse])
def get_category_products(
    category_id: int,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    return db.query(Product).filter(Product.category_id == category_id).offset(skip).limit(limit).all()