from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, Field
from app.database import get_db
from app.models.product import Product
from app.schemas.product import ProductResponse

from app.core.config import SUGGESTION_PRODUCT_IDS

router = APIRouter(prefix="/suggestion", tags=["Suggestion"])

@router.get("/", response_model=List[ProductResponse])
def get_suggestions(db: Session = Depends(get_db)):
    """
    Backend-də saxlanan suggestion product list-ni qaytarır.
    """
    products = (
        db.query(Product)
        .filter(Product.id.in_(SUGGESTION_PRODUCT_IDS))
        .all()
    )

    # Config-dəki sıralamanı qoruyur
    product_map = {p.id: p for p in products}
    ordered_products = [
        product_map[pid]
        for pid in SUGGESTION_PRODUCT_IDS
        if pid in product_map
    ]

    return ordered_products

