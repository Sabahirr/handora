from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.order import WishlistItem
from app.models.product import Product
from app.schemas.product import ProductResponse
from app.core.security import get_current_user

router = APIRouter(prefix="/wishlist", tags=["Wishlist"])

@router.post("")
def add_to_wishlist(
    product_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    existing = db.query(WishlistItem).filter(
        WishlistItem.user_id == current_user.id,
        WishlistItem.product_id == product_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Məhsul artıq istək siyahısındadır")
    
    wishlist_item = WishlistItem(user_id=current_user.id, product_id=product_id)
    db.add(wishlist_item)
    db.commit()
    return {"message": "İstək siyahısına əlavə edildi"}

@router.delete("/{product_id}")
def remove_from_wishlist(
    product_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    item = db.query(WishlistItem).filter(
        WishlistItem.user_id == current_user.id,
        WishlistItem.product_id == product_id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Məhsul tapılmadı")
    
    db.delete(item)
    db.commit()
    return {"message": "Silindi"}

@router.get("", response_model=List[ProductResponse])
def get_my_wishlist(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    wishlist_items = db.query(WishlistItem).filter(
        WishlistItem.user_id == current_user.id
    ).all()
    product_ids = [item.product_id for item in wishlist_items]
    return db.query(Product).filter(Product.id.in_(product_ids)).all()