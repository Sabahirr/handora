from pydantic import BaseModel,field_validator,Field
from typing import Optional, List
from datetime import datetime


# ==================== CATEGORY SCHEMAS ====================
class CategoryBase(BaseModel):
    name_az: str
    name_en: str
    name_ru: str
    slug: str
    parent_id: Optional[int] = None
    
    @field_validator('parent_id')
    @classmethod
    def normalize_parent_id(cls, v):
        """Convert 0 or negative values to None"""
        if v is not None and v <= 0:
            return None
        return v

class CategoryCreate(CategoryBase):
    """Schema for creating a new category"""
    pass

class CategoryUpdate(BaseModel):
    """Schema for updating a category (partial update)"""
    name_az: Optional[str] = None
    name_en: Optional[str] = None
    name_ru: Optional[str] = None
    slug: Optional[str] = None
    parent_id: Optional[int] = None
    
    @field_validator('parent_id')
    @classmethod
    def normalize_parent_id(cls, v):
        """Convert 0 or negative values to None"""
        if v is not None and v <= 0:
            return None
        return v

class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# ==================== BRAND SCHEMAS ====================

class BrandBase(BaseModel):
    name: str = Field(..., description="Brendin adı")
    description: Optional[str] = Field(None, description="Brend haqqında təsvir")
    logo_url: Optional[str] = Field(None, description="Brend loqosu URL")


class BrandCreate(BrandBase):
    """Schema for creating a new brand"""
    pass

class BrandUpdate(BaseModel):
    """Schema for updating a brand (partial update)"""
    name: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None

class BrandResponse(BrandBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== PRODUCT SCHEMAS ====================
class ProductBase(BaseModel):
    name_az: str
    name_en: str
    name_ru: str
    price: float
    discount_price: Optional[float] = None

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
    image_urls: Optional[List[str]] = None
    brand: Optional[BrandResponse] = None
    
    class Config:
        from_attributes = True

class ProductDetail(ProductResponse):
    description_az: str
    description_en: str
    description_ru: str
    category: Optional[CategoryResponse] = None
    created_at: datetime
    updated_at: datetime