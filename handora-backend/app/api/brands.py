from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.product import Brand, Product
from app.schemas.product import BrandResponse, ProductResponse

router = APIRouter(prefix="/brands", tags=["Brands"])

@router.get("", response_model=List[BrandResponse])
def get_brands(db: Session = Depends(get_db)):
    return db.query(Brand).all()

@router.get("/{brand_id}/products", response_model=List[ProductResponse])
def get_brand_products(
    brand_id: int,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    return db.query(Product).filter(Product.brand_id == brand_id).offset(skip).limit(limit).all()