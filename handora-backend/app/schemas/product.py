# from pydantic import BaseModel,field_validator,Field
# from typing import Optional, List
# from datetime import datetime


# # ==================== CATEGORY SCHEMAS ====================
# class CategoryBase(BaseModel):
#     name_az: str
#     name_en: str
#     name_ru: str
#     slug: str
#     parent_id: Optional[int] = None
    
#     @field_validator('parent_id')
#     @classmethod
#     def normalize_parent_id(cls, v):
#         """Convert 0 or negative values to None"""
#         if v is not None and v <= 0:
#             return None
#         return v

# class CategoryCreate(CategoryBase):
#     """Schema for creating a new category"""
#     pass

# class CategoryUpdate(BaseModel):
#     """Schema for updating a category (partial update)"""
#     name_az: Optional[str] = None
#     name_en: Optional[str] = None
#     name_ru: Optional[str] = None
#     slug: Optional[str] = None
#     parent_id: Optional[int] = None
    
#     @field_validator('parent_id')
#     @classmethod
#     def normalize_parent_id(cls, v):
#         """Convert 0 or negative values to None"""
#         if v is not None and v <= 0:
#             return None
#         return v

# class CategoryResponse(CategoryBase):
#     id: int
#     created_at: datetime
    
#     class Config:
#         from_attributes = True

# # ==================== BRAND SCHEMAS ====================

# class BrandBase(BaseModel):
#     name: str = Field(..., description="Brendin adı")
#     description: Optional[str] = Field(None, description="Brend haqqında təsvir")
#     logo_url: Optional[str] = Field(None, description="Brend loqosu URL")


# class BrandCreate(BrandBase):
#     """Schema for creating a new brand"""
#     pass

# class BrandUpdate(BaseModel):
#     """Schema for updating a brand (partial update)"""
#     name: Optional[str] = None
#     description: Optional[str] = None
#     logo_url: Optional[str] = None

# class BrandResponse(BrandBase):
#     id: int
#     created_at: datetime

#     class Config:
#         from_attributes = True


# # ==================== PRODUCT SCHEMAS ====================
# class ProductBase(BaseModel):
#     name_az: str
#     name_en: str
#     name_ru: str
#     price: float
#     discount_price: Optional[float] = None



# class ProductCreate(ProductBase):
#     description_az: str
#     description_en: str
#     description_ru: str
#     category_id: int
#     brand_id: int
#     stock: int
#     image_urls: List[str]

# class ProductResponse(ProductBase):
#     id: int
#     is_new: bool
#     is_sale: bool
#     stock: int
#     image_urls: Optional[List[str]] = None
#     brand: Optional[BrandResponse] = None
    
#     class Config:
#         from_attributes = True

# class ProductDetail(ProductResponse):
#     description_az: str
#     description_en: str
#     description_ru: str
#     category: Optional[CategoryResponse] = None
#     created_at: datetime
#     updated_at: datetime

from pydantic import BaseModel, field_validator, Field
from typing import Optional, List
from datetime import datetime


# ==================== PARENT CATEGORY SCHEMAS ====================
class ParentCategoryBase(BaseModel):
    name_az: str = Field(..., description="Kateqoriyanın Azərbaycan dilində adı")
    name_en: str = Field(..., description="Kateqoriyanın İngilis dilində adı")
    name_ru: str = Field(..., description="Kateqoriyanın Rus dilində adı")
    slug: str = Field(..., description="URL-friendly slug")


class ParentCategoryCreate(ParentCategoryBase):
    """Schema for creating a parent category"""
    pass


class ParentCategoryUpdate(BaseModel):
    """Schema for updating a parent category (partial update)"""
    name_az: Optional[str] = None
    name_en: Optional[str] = None
    name_ru: Optional[str] = None
    slug: Optional[str] = None


class ParentCategoryResponse(ParentCategoryBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== SUBCATEGORY SCHEMAS ====================
class SubCategoryBase(BaseModel):
    name_az: str = Field(..., description="Alt kateqoriyanın Azərbaycan dilində adı")
    name_en: str = Field(..., description="Alt kateqoriyanın İngilis dilində adı")
    name_ru: str = Field(..., description="Alt kateqoriyanın Rus dilində adı")
    slug: str = Field(..., description="URL-friendly slug")
    parent_id: Optional[int] = Field(..., gt=0, description="Əsas kateqoriyanın ID-si (məcburidir)")


class SubCategoryCreate(SubCategoryBase):
    """Schema for creating a subcategory"""
    pass


class SubCategoryUpdate(BaseModel):
    """Schema for updating a subcategory (partial update)"""
    name_az: Optional[str] = None
    name_en: Optional[str] = None
    name_ru: Optional[str] = None
    slug: Optional[str] = None
    parent_id: Optional[int] = Field(None, gt=0, description="Əsas kateqoriyanın ID-si")


class SubCategoryResponse(SubCategoryBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class SubCategoryWithParent(SubCategoryResponse):
    """Subcategory with parent category info"""
    parent: Optional[ParentCategoryResponse] = None


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
    name_az: str = Field(..., description="Məhsulun Azərbaycan dilində adı")
    name_en: str = Field(..., description="Məhsulun İngilis dilində adı")
    name_ru: str = Field(..., description="Məhsulun Rus dilində adı")
    price: float = Field(..., gt=0, description="Məhsulun qiyməti")
    discount_price: Optional[float] = Field(None, ge=0, description="Endirimli qiymət")
    
    @field_validator('discount_price')
    @classmethod
    def validate_discount_price(cls, v, info):
        if v is not None and 'price' in info.data and v >= info.data['price']:
            raise ValueError('Endirimli qiymət əsas qiymətdən az olmalıdır')
        return v


class ProductCreate(ProductBase):
    description_az: str = Field(..., description="Məhsulun təsviri (AZ)")
    description_en: str = Field(..., description="Məhsulun təsviri (EN)")
    description_ru: str = Field(..., description="Məhsulun təsviri (RU)")
    category_id: int = Field(..., gt=0, description="Kateqoriya ID-si")
    brand_id: int = Field(..., gt=0, description="Brend ID-si")
    stock: int = Field(0, ge=0, description="Stokdakı say")
    image_urls: List[str] = Field(default_factory=list, description="Şəkil URL-ləri")
    is_new: bool = Field(True, description="Yeni məhsuldur?")
    is_sale: bool = Field(False, description="Endirimdədir?")


class ProductUpdate(BaseModel):
    """Schema for updating a product (partial update)"""
    name_az: Optional[str] = None
    name_en: Optional[str] = None
    name_ru: Optional[str] = None
    description_az: Optional[str] = None
    description_en: Optional[str] = None
    description_ru: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    discount_price: Optional[float] = Field(None, ge=0)
    category_id: Optional[int] = Field(None, gt=0)
    brand_id: Optional[int] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    image_urls: Optional[List[str]] = None
    is_new: Optional[bool] = None
    is_sale: Optional[bool] = None


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
    category: Optional[SubCategoryResponse] = None  # Can be either parent or subcategory
    created_at: datetime
    updated_at: datetime


# ==================== FILTER SCHEMAS ====================
class ProductFilter(BaseModel):
    """Filter schema for product search"""
    category_id: Optional[int] = Field(None, description="Kateqoriya ID-si ilə filter")
    brand_id: Optional[int] = Field(None, description="Brend ID-si ilə filter")
    is_new: Optional[bool] = Field(None, description="Yeni məhsullar")
    is_sale: Optional[bool] = Field(None, description="Endirimli məhsullar")
    min_price: Optional[float] = Field(None, ge=0, description="Minimum qiymət")
    max_price: Optional[float] = Field(None, ge=0, description="Maksimum qiymət")
    search: Optional[str] = Field(None, description="Məhsul adında axtarış")