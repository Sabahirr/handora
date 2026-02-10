from fastapi import APIRouter

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

@router.get("/ping")
def ping():
    return {"message": "Admin router is working"}

"""
ADMIN API - Yalnız admin istifadəçilər üçün
Create, Update, Delete əməliyyatları
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.product import Product, Category, Brand
from app.models.order import Order
from app.schemas.product import (
    ProductResponse, ProductDetail, 
    ParentCategoryCreate, ParentCategoryUpdate, ParentCategoryResponse,
    SubCategoryCreate, SubCategoryUpdate, SubCategoryResponse,
    BrandCreate, BrandUpdate, BrandResponse
)
from app.core.security import get_current_admin
from app.core.utils import save_product_image, delete_file

router = APIRouter(prefix="/admin", tags=["Admin Panel"])

# ============================================
# PRODUCT MANAGEMENT
# ============================================

@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def admin_create_product(
    # Multilingual fields
    name_az: str = Form(..., description="Məhsulun adı (Azərbaycan)"),
    name_en: str = Form(..., description="Product name (English)"),
    name_ru: str = Form(..., description="Название продукта (Русский)"),
    description_az: str = Form(..., description="Təsvir (Azərbaycan)"),
    description_en: str = Form(..., description="Description (English)"),
    description_ru: str = Form(..., description="Описание (Русский)"),
    
    # Pricing
    price: float = Form(..., gt=0, description="Qiymət"),
    discount_price: Optional[float] = Form(None, ge=0, description="Endirimli qiymət"),
    
    # Categorization
    category_id: int = Form(..., description="Kateqoriya ID"),
    brand_id: int = Form(..., description="Brend ID"),
    
    # Inventory
    stock: int = Form(0, ge=0, description="Stok miqdarı"),
    
    # Flags
    is_new: bool = Form(True, description="Yeni məhsul"),
    is_sale: bool = Form(False, description="Endirimdə"),
    
    # Images
    images: List[UploadFile] = File(..., description="Məhsul şəkilləri (minimum 1)"),
    
    # Dependencies
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    ADMIN - Yeni məhsul əlavə et
    
    Tələblər:
    - Minimum 1 şəkil
    - Şəkil formatı: JPG, JPEG, PNG
    - Maksimum fayl ölçüsü: 5MB
    """
    
    # Validate category exists
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail=f"Kateqoriya ID {category_id} tapılmadı")
    
    # Validate brand exists
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail=f"Brend ID {brand_id} tapılmadı")
    
    # Validate discount price
    if discount_price and discount_price >= price:
        raise HTTPException(
            status_code=400,
            detail="Endirimli qiymət əsas qiymətdən az olmalıdır"
        )
    
    # Validate images
    if not images or len(images) == 0:
        raise HTTPException(status_code=400, detail="Ən azı 1 şəkil yükləməlisiniz")
    
    if len(images) > 10:
        raise HTTPException(status_code=400, detail="Maksimum 10 şəkil yükləyə bilərsiniz")
    
    # Upload images
    image_urls = []
    uploaded_files = []
    
    try:
        for image in images:
            image_url = await save_product_image(image)
            image_urls.append(image_url)
            uploaded_files.append(image_url)
    except Exception as e:
        # Rollback: delete uploaded images
        for url in uploaded_files:
            delete_file(url)
        raise e
    
    # Create product
    try:
        new_product = Product(
            name_az=name_az,
            name_en=name_en,
            name_ru=name_ru,
            description_az=description_az,
            description_en=description_en,
            description_ru=description_ru,
            price=price,
            discount_price=discount_price,
            category_id=category_id,
            brand_id=brand_id,
            stock=stock,
            is_new=is_new,
            is_sale=is_sale or (discount_price is not None),  # Auto-set is_sale if discount exists
            image_urls=image_urls
        )
        
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        
        return new_product
        
    except Exception as e:
        # Rollback: delete uploaded images
        for url in image_urls:
            delete_file(url)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Məhsul yaradılmadı: {str(e)}")


@router.put("/products/{product_id}", response_model=ProductResponse)
async def admin_update_product(
    product_id: int,
    
    # Optional multilingual fields
    name_az: Optional[str] = Form(None),
    name_en: Optional[str] = Form(None),
    name_ru: Optional[str] = Form(None),
    description_az: Optional[str] = Form(None),
    description_en: Optional[str] = Form(None),
    description_ru: Optional[str] = Form(None),
    
    # Optional pricing
    price: Optional[float] = Form(None, gt=0),
    discount_price: Optional[float] = Form(None),
    
    # Optional categorization
    category_id: Optional[int] = Form(None),
    brand_id: Optional[int] = Form(None),
    
    # Optional inventory
    stock: Optional[int] = Form(None, ge=0),
    
    # Optional flags
    is_new: Optional[bool] = Form(None),
    is_sale: Optional[bool] = Form(None),
    
    # Optional images (if provided, replaces all existing images)
    images: Optional[List[UploadFile]] = File(None),
    
    # Dependencies
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    ADMIN - Məhsulu redaktə et
    
    Qeyd: Yalnız göndərdiyiniz field-lər yenilənəcək
    """
    
    # Find product
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Məhsul tapılmadı")
    
    # Update multilingual fields
    if name_az: product.name_az = name_az
    if name_en: product.name_en = name_en
    if name_ru: product.name_ru = name_ru
    if description_az: product.description_az = description_az
    if description_en: product.description_en = description_en
    if description_ru: product.description_ru = description_ru
    
    # Update pricing
    if price is not None:
        product.price = price
    
    if discount_price is not None:
        if discount_price > 0 and discount_price >= product.price:
            raise HTTPException(
                status_code=400,
                detail="Endirimli qiymət əsas qiymətdən az olmalıdır"
            )
        product.discount_price = discount_price if discount_price > 0 else None
        # Auto-update is_sale
        if discount_price > 0:
            product.is_sale = True
    
    # Update categorization
    if category_id:
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Kateqoriya tapılmadı")
        product.category_id = category_id
    
    if brand_id:
        brand = db.query(Brand).filter(Brand.id == brand_id).first()
        if not brand:
            raise HTTPException(status_code=404, detail="Brend tapılmadı")
        product.brand_id = brand_id
    
    # Update inventory
    if stock is not None:
        product.stock = stock
    
    # Update flags
    if is_new is not None:
        product.is_new = is_new
    if is_sale is not None:
        product.is_sale = is_sale
    
    # Update images if provided
    if images and len(images) > 0:
        if len(images) > 10:
            raise HTTPException(status_code=400, detail="Maksimum 10 şəkil yükləyə bilərsiniz")
        
        old_images = product.image_urls or []
        new_image_urls = []
        uploaded_files = []
        
        try:
            # Upload new images
            for image in images:
                image_url = await save_product_image(image)
                new_image_urls.append(image_url)
                uploaded_files.append(image_url)
            
            # Update product
            product.image_urls = new_image_urls
            db.commit()
            
            # Delete old images after successful update
            for old_url in old_images:
                delete_file(old_url)
                
        except Exception as e:
            # Rollback: delete newly uploaded images
            for url in uploaded_files:
                delete_file(url)
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Şəkillər yenilənmədi: {str(e)}")
    else:
        # No images update, just commit other changes
        db.commit()
    
    db.refresh(product)
    return product


@router.delete("/products/{product_id}", status_code=status.HTTP_200_OK)
def admin_delete_product(
    product_id: int,
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    ADMIN - Məhsulu sil
    
    Şəkillər də silinəcək
    """
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Məhsul tapılmadı")
    
    # Delete all images
    if product.image_urls:
        for image_url in product.image_urls:
            delete_file(image_url)
    
    # Delete product
    db.delete(product)
    db.commit()
    
    return {
        "message": "Məhsul uğurla silindi",
        "product_id": product_id,
        "deleted_images": len(product.image_urls) if product.image_urls else 0
    }


@router.get("/products", response_model=List[ProductResponse])
def admin_get_all_products(
    skip: int = 0,
    limit: int = 50,
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """ADMIN - Bütün məhsulları gör"""
    return db.query(Product).offset(skip).limit(limit).all()


# ============================================
# PARENT CATEGORY MANAGEMENT (ADMIN)
# ============================================

@router.post(
    "/categories",
    response_model=ParentCategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="[ADMIN] Yeni əsas kateqoriya yarat"
)
def admin_create_parent_category(
    category: ParentCategoryCreate,
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    ADMIN - Yeni əsas kateqoriya yaradır (parent_id = NULL).
    """
    # Check if slug already exists
    existing = db.query(Category).filter(Category.slug == category.slug).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Slug '{category.slug}' artıq mövcuddur"
        )
    
    db_category = Category(
        name_az=category.name_az,
        name_en=category.name_en,
        name_ru=category.name_ru,
        slug=category.slug,
        parent_id=None  # Əsas kateqoriya
    )
    
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    
    return db_category


@router.get(
    "/categories",
    response_model=List[ParentCategoryResponse],
    summary="[ADMIN] Bütün əsas kateqoriyaları gətir"
)
def admin_get_parent_categories(
    skip: int = 0,
    limit: int = 100,
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """ADMIN - Bütün əsas kateqoriyaları qaytarır"""
    categories = db.query(Category)\
        .filter(Category.parent_id == None)\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return categories


@router.put(
    "/categories/{category_id}",
    response_model=ParentCategoryResponse,
    summary="[ADMIN] Əsas kateqoriyanı yenilə"
)
def admin_update_parent_category(
    category_id: int,
    category_update: ParentCategoryUpdate,
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    ADMIN - Mövcud əsas kateqoriyanı yeniləyir.
    """
    db_category = db.query(Category)\
        .filter(Category.id == category_id, Category.parent_id == None)\
        .first()
    
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID {category_id} ilə əsas kateqoriya tapılmadı"
        )
    
    # Update only provided fields
    update_data = category_update.model_dump(exclude_unset=True)
    
    # Check slug uniqueness if being updated
    if "slug" in update_data:
        existing = db.query(Category)\
            .filter(Category.slug == update_data["slug"], Category.id != category_id)\
            .first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Slug '{update_data['slug']}' artıq mövcuddur"
            )
    
    for field, value in update_data.items():
        setattr(db_category, field, value)
    
    db.commit()
    db.refresh(db_category)
    
    return db_category


@router.delete(
    "/categories/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="[ADMIN] Əsas kateqoriyanı sil"
)
def admin_delete_parent_category(
    category_id: int,
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    ADMIN - Əsas kateqoriyanı silir.
    Əgər alt kateqoriyalar varsa, xəta qaytarır.
    """
    db_category = db.query(Category)\
        .filter(Category.id == category_id, Category.parent_id == None)\
        .first()
    
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID {category_id} ilə əsas kateqoriya tapılmadı"
        )
    
    # Check if has subcategories
    subcategories_count = db.query(Category)\
        .filter(Category.parent_id == category_id)\
        .count()
    
    if subcategories_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bu kateqoriyanın {subcategories_count} alt kateqoriyası var. Əvvəlcə onları silin."
        )
    
    db.delete(db_category)
    db.commit()
    
    return None


# ============================================
# SUBCATEGORY MANAGEMENT (ADMIN)
# ============================================

@router.post(
    "/subcategories",
    response_model=SubCategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="[ADMIN] Yeni alt kateqoriya yarat"
)
def admin_create_subcategory(
    subcategory: SubCategoryCreate,
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    ADMIN - Yeni alt kateqoriya yaradır.
    parent_id məcburidir və mövcud əsas kateqoriya olmalıdır.
    """
    # Verify parent category exists and is a parent (not a subcategory)
    parent = db.query(Category)\
        .filter(Category.id == subcategory.parent_id, Category.parent_id == None)\
        .first()
    
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID {subcategory.parent_id} ilə əsas kateqoriya tapılmadı"
        )
    
    # Check if slug already exists
    existing = db.query(Category).filter(Category.slug == subcategory.slug).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Slug '{subcategory.slug}' artıq mövcuddur"
        )
    
    db_subcategory = Category(
        name_az=subcategory.name_az,
        name_en=subcategory.name_en,
        name_ru=subcategory.name_ru,
        slug=subcategory.slug,
        parent_id=subcategory.parent_id
    )
    
    db.add(db_subcategory)
    db.commit()
    db.refresh(db_subcategory)
    
    return db_subcategory


@router.get(
    "/subcategories",
    response_model=List[SubCategoryResponse],
    summary="[ADMIN] Bütün alt kateqoriyaları gətir"
)
def admin_get_subcategories(
    parent_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """ADMIN - Bütün alt kateqoriyaları qaytarır"""
    query = db.query(Category).filter(Category.parent_id != None)
    
    if parent_id:
        query = query.filter(Category.parent_id == parent_id)
    
    return query.offset(skip).limit(limit).all()


@router.put(
    "/subcategories/{subcategory_id}",
    response_model=SubCategoryResponse,
    summary="[ADMIN] Alt kateqoriyanı yenilə"
)
def admin_update_subcategory(
    subcategory_id: int,
    subcategory_update: SubCategoryUpdate,
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    ADMIN - Mövcud alt kateqoriyanı yeniləyir.
    """
    db_subcategory = db.query(Category)\
        .filter(Category.id == subcategory_id, Category.parent_id != None)\
        .first()
    
    if not db_subcategory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID {subcategory_id} ilə alt kateqoriya tapılmadı"
        )
    
    update_data = subcategory_update.model_dump(exclude_unset=True)
    
    # Verify new parent_id if being updated
    if "parent_id" in update_data:
        parent = db.query(Category)\
            .filter(Category.id == update_data["parent_id"], Category.parent_id == None)\
            .first()
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ID {update_data['parent_id']} ilə əsas kateqoriya tapılmadı"
            )
    
    # Check slug uniqueness if being updated
    if "slug" in update_data:
        existing = db.query(Category)\
            .filter(Category.slug == update_data["slug"], Category.id != subcategory_id)\
            .first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Slug '{update_data['slug']}' artıq mövcuddur"
            )
    
    for field, value in update_data.items():
        setattr(db_subcategory, field, value)
    
    db.commit()
    db.refresh(db_subcategory)
    
    return db_subcategory


@router.delete(
    "/subcategories/{subcategory_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="[ADMIN] Alt kateqoriyanı sil"
)
def admin_delete_subcategory(
    subcategory_id: int,
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    ADMIN - Alt kateqoriyanı silir.
    """
    db_subcategory = db.query(Category)\
        .filter(Category.id == subcategory_id, Category.parent_id != None)\
        .first()
    
    if not db_subcategory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID {subcategory_id} ilə alt kateqoriya tapılmadı"
        )
    
    db.delete(db_subcategory)
    db.commit()
    
    return None


# ============================================
# BRAND MANAGEMENT (ADMIN)
# ============================================

@router.post("/brands", response_model=BrandResponse, status_code=status.HTTP_201_CREATED)
def admin_create_brand(
    brand_data: BrandCreate,
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """ADMIN - Yeni brend əlavə et"""
    
    # Check if brand exists
    existing = db.query(Brand).filter(Brand.name == brand_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bu brend artıq mövcuddur")
    
    new_brand = Brand(
        name=brand_data.name,
        description=brand_data.description,
        logo_url=brand_data.logo_url
    )
    
    db.add(new_brand)
    db.commit()
    db.refresh(new_brand)
    
    return new_brand


@router.get("/brands", response_model=List[BrandResponse])
def admin_get_brands(
    skip: int = 0,
    limit: int = 100,
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """ADMIN - Bütün brendləri gətir"""
    return db.query(Brand).offset(skip).limit(limit).all()


@router.put("/brands/{brand_id}", response_model=BrandResponse)
def admin_update_brand(
    brand_id: int,
    brand_data: BrandUpdate,
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """ADMIN - Brendi redaktə et"""
    
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brend tapılmadı")
    
    # Update name
    if brand_data.name:
        # Check if new name already exists
        existing = db.query(Brand).filter(
            Brand.name == brand_data.name,
            Brand.id != brand_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Bu brend adı artıq istifadə olunur")
        brand.name = brand_data.name
    
    # Update description
    if brand_data.description is not None:
        brand.description = brand_data.description
    
    # Update logo_url
    if brand_data.logo_url is not None:
        brand.logo_url = brand_data.logo_url
    
    db.commit()
    db.refresh(brand)
    
    return brand


@router.delete("/brands/{brand_id}")
def admin_delete_brand(
    brand_id: int,
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """ADMIN - Brendi sil"""
    
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brend tapılmadı")
    
    # Check if brand has products
    products_count = db.query(Product).filter(Product.brand_id == brand_id).count()
    if products_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Bu brenddə {products_count} məhsul var. Əvvəlcə məhsulları silin və ya başqa brendə köçürün"
        )
    
    # Delete logo
    if brand.logo_url:
        delete_file(brand.logo_url)
    
    db.delete(brand)
    db.commit()
    
    return {"message": "Brend silindi", "brand_id": brand_id}


# ============================================
# ORDER MANAGEMENT (ADMIN)
# ============================================

@router.get("/orders")
def admin_get_all_orders(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """ADMIN - Bütün sifarişləri gör"""
    
    query = db.query(Order)
    
    if status:
        query = query.filter(Order.status == status)
    
    orders = query.offset(skip).limit(limit).all()
    return orders


@router.put("/orders/{order_id}/status")
def admin_update_order_status(
    order_id: int,
    status: str,
    tracking_number: Optional[str] = None,
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """ADMIN - Sifariş statusunu yenilə"""
    
    valid_statuses = ["pending", "confirmed", "shipped", "delivered", "cancelled"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Status yalnız bunlardan biri ola bilər: {', '.join(valid_statuses)}"
        )
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Sifariş tapılmadı")
    
    order.status = status
    if tracking_number:
        order.tracking_number = tracking_number
    
    db.commit()
    
    return {
        "message": f"Sifariş statusu '{status}' olaraq yeniləndi",
        "order_id": order_id,
        "status": status,
        "tracking_number": tracking_number
    }


# ============================================
# STATISTICS & DASHBOARD
# ============================================

@router.get("/stats")
def admin_get_statistics(
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """ADMIN - Dashboard statistikaları"""
    
    from app.models.user import User
    
    total_products = db.query(Product).count()
    total_categories = db.query(Category).count()
    total_brands = db.query(Brand).count()
    total_orders = db.query(Order).count()
    total_users = db.query(User).count()
    
    # Orders by status
    orders_pending = db.query(Order).filter(Order.status == "pending").count()
    orders_confirmed = db.query(Order).filter(Order.status == "confirmed").count()
    orders_shipped = db.query(Order).filter(Order.status == "shipped").count()
    orders_delivered = db.query(Order).filter(Order.status == "delivered").count()
    
    # Low stock products
    low_stock = db.query(Product).filter(Product.stock < 5).count()
    
    return {
        "products": {
            "total": total_products,
            "low_stock": low_stock
        },
        "categories": total_categories,
        "brands": total_brands,
        "orders": {
            "total": total_orders,
            "pending": orders_pending,
            "confirmed": orders_confirmed,
            "shipped": orders_shipped,
            "delivered": orders_delivered
        },
        "users": total_users
    }