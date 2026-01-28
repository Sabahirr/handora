from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CategoryBase(BaseModel):
    name_az: str
    name_en: str
    name_ru: str
    slug: str

class CategoryResponse(CategoryBase):
    id: int
    parent_id: Optional[int]
    
    class Config:
        from_attributes = True

class BrandBase(BaseModel):
    name: str
    logo_url: Optional[str]

class BrandResponse(BrandBase):
    id: int
    
    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    name_az: str
    name_en: str
    name_ru: str
    price: float
    discount_price: Optional[float]

class ProductCreate(ProductBase):
    description_az: str
    description_en: str
    description_ru: str
    category_id: int
    brand_id: int
    stock: int
    image_urls: List[str]

class ProductResponse(ProductBase):
    id: int
    is_new: bool
    is_sale: bool
    stock: int
    image_urls: Optional[List[str]]
    brand: Optional[BrandResponse]
    
    class Config:
        from_attributes = True

class ProductDetail(ProductResponse):
    description_az: str
    description_en: str
    description_ru: str
    category: Optional[CategoryResponse]
    created_at: datetime