from pydantic import BaseModel
from typing import List
from datetime import datetime

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]
    shipping_address: str

class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    price: float
    
    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id: int
    total_amount: float
    currency: str
    status: str
    shipping_address: str
    created_at: datetime
    items: List[OrderItemResponse]
    
    class Config:
        from_attributes = True