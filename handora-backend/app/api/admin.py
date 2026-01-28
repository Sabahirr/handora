from fastapi import APIRouter

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

@router.get("/ping")
def ping():
    return {"message": "Admin router is working"}


# ==================== app/api/admin.py ====================
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.product import Product, Category, Brand
from app.models.order import Order
from app.schemas.product import (
    ProductResponse, ProductDetail, CategoryResponse, BrandResponse,
    CategoryCreate, CategoryUpdate, BrandCreate, BrandUpdate
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
    Admin - Yeni məhsul əlavə et
    
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
    Admin - Məhsulu redaktə et
    
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
    Admin - Məhsulu sil
    
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
    """Admin - Bütün məhsulları gör"""
    return db.query(Product).offset(skip).limit(limit).all()

# ============================================
# CATEGORY MANAGEMENT
# ============================================

@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def admin_create_category(
    category_data: CategoryCreate,
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Admin - Yeni kateqoriya əlavə et"""
    
    # Check if slug exists
    existing = db.query(Category).filter(Category.slug == category_data.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bu slug artıq mövcuddur")
    
    # If parent_id provided, check if it exists
    if category_data.parent_id:
        parent = db.query(Category).filter(Category.id == category_data.parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Ana kateqoriya tapılmadı")
    
    new_category = Category(
        name_az=category_data.name_az,
        name_en=category_data.name_en,
        name_ru=category_data.name_ru,
        slug=category_data.slug,
        parent_id=category_data.parent_id
    )
    
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    
    return new_category

@router.put("/categories/{category_id}", response_model=CategoryResponse)
def admin_update_category(
    category_id: int,
    category_data: CategoryUpdate,
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Admin - Kateqoriyanı redaktə et (partial update)"""
    
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Kateqoriya tapılmadı")
    
    # Update only provided fields
    if category_data.name_az is not None:
        category.name_az = category_data.name_az
    if category_data.name_en is not None:
        category.name_en = category_data.name_en
    if category_data.name_ru is not None:
        category.name_ru = category_data.name_ru
    
    # Check slug
    if category_data.slug is not None and category_data.slug != category.slug:
        existing = db.query(Category).filter(
            Category.slug == category_data.slug,
            Category.id != category_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Bu slug artıq istifadə olunur")
        category.slug = category_data.slug
    
    # Update parent_id
    if category_data.parent_id is not None:
        # Prevent self-referencing
        if category_data.parent_id == category_id:
            raise HTTPException(status_code=400, detail="Kateqoriya özünə ana kateqoriya ola bilməz")
        
        if category_data.parent_id > 0:
            parent = db.query(Category).filter(Category.id == category_data.parent_id).first()
            if not parent:
                raise HTTPException(status_code=404, detail="Ana kateqoriya tapılmadı")
        
        category.parent_id = category_data.parent_id if category_data.parent_id > 0 else None
    
    db.commit()
    db.refresh(category)
    
    return category

@router.delete("/categories/{category_id}")
def admin_delete_category(
    category_id: int,
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Admin - Kateqoriyanı sil"""
    
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Kateqoriya tapılmadı")
    
    # Check if category has products
    products_count = db.query(Product).filter(Product.category_id == category_id).count()
    if products_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Bu kateqoriyada {products_count} məhsul var. Əvvəlcə məhsulları silin və ya başqa kateqoriyaya köçürün"
        )
    
    # Check if category has subcategories
    subcategories = db.query(Category).filter(Category.parent_id == category_id).count()
    if subcategories > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Bu kateqoriyanın {subcategories} alt kateqoriyası var. Əvvəlcə onları silin"
        )
    
    db.delete(category)
    db.commit()
    
    return {"message": "Kateqoriya silindi", "category_id": category_id}

# ============================================
# # BRAND MANAGEMENT
# # ============================================

@router.post("/brands/json", response_model=BrandResponse, status_code=status.HTTP_201_CREATED)
def admin_create_brand_json(
    brand_data: BrandCreate,
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Admin - Yeni brend əlavə et (JSON body)"""
    
    # Check if brand exists
    existing = db.query(Brand).filter(Brand.name == brand_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bu brend artıq mövcuddur")
    
    new_brand = Brand(
        name=brand_data.name,
        description=brand_data.description,
        logo_url=None  # Logo sonra yükləyə bilər
    )
    
    db.add(new_brand)
    db.commit()
    db.refresh(new_brand)
    
    return new_brand

@router.put("/brands/{brand_id}/json", response_model=BrandResponse)
def admin_update_brand_json(
    brand_id: int,
    brand_data: BrandUpdate,
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Admin - Brendi redaktə et (JSON body)"""
    
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
    
    db.commit()
    db.refresh(brand)
    
    return brand

@router.delete("/brands/{brand_id}")
def admin_delete_brand(
    brand_id: int,
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Admin - Brendi sil"""
    
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
# ORDER MANAGEMENT
# ============================================

@router.get("/orders")
def admin_get_all_orders(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Admin - Bütün sifarişləri gör"""
    
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
    """Admin - Sifariş statusunu yenilə"""
    
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
    """Admin - Dashboard statistikaları"""
    
    from app.models.user import User
    from app.models.newsletter import Newsletter
    
    total_products = db.query(Product).count()
    total_categories = db.query(Category).count()
    total_brands = db.query(Brand).count()
    total_orders = db.query(Order).count()
    total_users = db.query(User).count()
    total_subscribers = db.query(Newsletter).count()
    
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
        "users": total_users,
        "newsletter_subscribers": total_subscribers
    }