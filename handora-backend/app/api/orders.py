from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.schemas.order import OrderCreate, OrderResponse
from app.core.security import get_current_user

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("", response_model=OrderResponse)
def create_order(
    order_data: OrderCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    total = 0
    order_items = []
    
    for item in order_data.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Məhsul ID {item.product_id} tapılmadı")
        if product.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"{product.name_az} stokda yoxdur")
        
        price = product.discount_price if product.discount_price else product.price
        total += price * item.quantity
        order_items.append({
            "product_id": product.id,
            "quantity": item.quantity,
            "price": price
        })
        product.stock -= item.quantity
    
    new_order = Order(
        user_id=current_user.id,
        total_amount=total,
        shipping_address=order_data.shipping_address
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    
    for item_data in order_items:
        order_item = OrderItem(order_id=new_order.id, **item_data)
        db.add(order_item)
    
    db.commit()
    db.refresh(new_order)
    return new_order

@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Sifariş tapılmadı")
    return order

@router.get("", response_model=List[OrderResponse])
def get_my_orders(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Order).filter(Order.user_id == current_user.id).all()