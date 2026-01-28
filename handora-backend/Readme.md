"""
# 👨‍💼 Admin Panel İstifadə Təlimatı

## 🔐 İlk Admin Yaratmaq

```bash
python scripts/create_admin.py
```

Admin məlumatlarını daxil edin:
- Email: admin@made.az
- Şifrə: Admin123!
- Ad Soyad: Admin User
- Telefon: +994501234567

## 🚀 Admin API Endpointləri

### Authentication
Bütün admin endpointləri Bearer token tələb edir:
```bash
# Login
POST /api/auth/login
{
  "email": "admin@made.az",
  "password": "Admin123!"
}

# Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

Header-də istifadə:
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

---

### 📦 MƏHSUL İDARƏETMƏSİ

#### Yeni məhsul əlavə et
```bash
POST /api/admin/products
Content-Type: multipart/form-data

Form data:
- name_az: "Əl işi xalça"
- name_en: "Handmade Carpet"
- name_ru: "Ручной ковер"
- description_az: "Yerli ustalar tərəfindən toxunmuş"
- description_en: "Woven by local craftsmen"
- description_ru: "Сотканный местными мастерами"
- price: 350.00
- discount_price: 299.00 (optional)
- category_id: 1
- brand_id: 2
- stock: 10
- is_new: true
- is_sale: false
- images: [file1.jpg, file2.jpg] (multiple files)
```

**cURL nümunəsi:**
```bash
curl -X POST "http://localhost:8000/api/admin/products" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "name_az=Əl işi xalça" \
  -F "name_en=Handmade Carpet" \
  -F "name_ru=Ручной ковер" \
  -F "description_az=Yerli ustalar tərəfindən toxunmuş" \
  -F "description_en=Woven by local craftsmen" \
  -F "description_ru=Сотканный местными мастерами" \
  -F "price=350" \
  -F "discount_price=299" \
  -F "category_id=1" \
  -F "brand_id=2" \
  -F "stock=10" \
  -F "is_new=true" \
  -F "is_sale=false" \
  -F "images=@/path/to/image1.jpg" \
  -F "images=@/path/to/image2.jpg"
```

#### Məhsulu redaktə et
```bash
PUT /api/admin/products/{product_id}
Content-Type: multipart/form-data

# Yalnız dəyişdirmək istədiyiniz field-ləri göndərin
Form data:
- price: 320.00
- stock: 15
- images: [new_file.jpg] (optional - yeni şəkillər)
```

#### Məhsulu sil
```bash
DELETE /api/admin/products/{product_id}
```

---

### 📁 KATEQORİYA İDARƏETMƏSİ

#### Yeni kateqoriya
```bash
POST /api/admin/categories
Content-Type: application/json

{
  "name_az": "Ev tekstili",
  "name_en": "Home Textile",
  "name_ru": "Домашний текстиль",
  "slug": "ev-tekstili",
  "parent_id": null
}
```

#### Kateqoriyanı redaktə et
```bash
PUT /api/admin/categories/{category_id}
{
  "name_az": "Ev dekorasiyası"
}
```

#### Kateqoriyanı sil
```bash
DELETE /api/admin/categories/{category_id}
```

---

### 🏷️ BREND İDARƏETMƏSİ

#### Yeni brend
```bash
POST /api/admin/brands
Content-Type: multipart/form-data

Form data:
- name: "Leatherart"
- description: "Keyfiyyətli dəri məhsulları"
- logo: logo.png (optional)
```

#### Brendi redaktə et
```bash
PUT /api/admin/brands/{brand_id}
Content-Type: multipart/form-data

Form data:
- name: "LeatherArt Premium"
- logo: new_logo.png (optional)
```

#### Brendi sil
```bash
DELETE /api/admin/brands/{brand_id}
```

---

### 📦 SİFARİŞ İDARƏETMƏSİ

#### Bütün sifarişləri gör
```bash
GET /api/admin/orders?skip=0&limit=50&status=pending

Query params:
- skip: 0 (pagination)
- limit: 50 (pagination)
- status: pending/confirmed/shipped/delivered/cancelled (optional)
```

#### Sifariş statusunu yenilə
```bash
PUT /api/admin/orders/{order_id}/status
Content-Type: application/json

{
  "status": "shipped",
  "tracking_number": "TRK123456789" (optional)
}

Mövcud statuslar:
- pending: Gözləyir
- confirmed: Təsdiq edilib
- shipped: Göndərilib
- delivered: Çatdırılıb
- cancelled: Ləğv edilib
```

---

## 📝 Python-da istifadə nümunəsi

```python
import requests

BASE_URL = "http://localhost:8000/api"

# Login
response = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "admin@made.az",
    "password": "Admin123!"
})
token = response.json()["access_token"]

headers = {"Authorization": f"Bearer {token}"}

# Məhsul əlavə et
files = [
    ('images', open('image1.jpg', 'rb')),
    ('images', open('image2.jpg', 'rb'))
]

data = {
    'name_az': 'Test məhsul',
    'name_en': 'Test product',
    'name_ru': 'Тестовый продукт',
    'description_az': 'Test təsvir',
    'description_en': 'Test description',
    'description_ru': 'Тестовое описание',
    'price': 100,
    'category_id': 1,
    'brand_id': 1,
    'stock': 20
}

response = requests.post(
    f"{BASE_URL}/admin/products",
    headers=headers,
    files=files,
    data=data
)

print(response.json())
```

---

## 🔒 Təhlükəsizlik

1. **Token əldə et**: Login edin və access_token alın
2. **Header əlavə et**: Hər request-də `Authorization: Bearer {token}` göndərin
3. **Token müddəti**: 30 dəqiqə (settings-də dəyişə bilərsiniz)
4. **Admin hüquqları**: Yalnız `role="admin"` olan istifadəçilər admin API-yə daxil ola bilər

---

## 📊 Test üçün məlumat əlavə etmək

```bash
# Kateqoriya
POST /api/admin/categories
{
  "name_az": "Geyim",
  "name_en": "Clothing",
  "name_ru": "Одежда",
  "slug": "geyim"
}

# Brend
POST /api/admin/brands (multipart-form)
name: "Made.az"

# Məhsul
POST /api/admin/products (multipart-form)
name_az: "Kişi köynəyi"
price: 45
category_id: 1
brand_id: 1
stock: 50
images: [file1.jpg, file2.jpg]
```

---

## 🚀 QURAŞDIRMA ADDIMLAR

### 1. PostgreSQL Database
```bash
sudo -u postgres psql
CREATE DATABASE made_az;
CREATE USER postgres WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE made_az TO postgres;
\q
```

### 2. .env faylı
```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_DB=made_az

SECRET_KEY=your-super-secret-key-here
```

### 3. Python paketləri
```bash
pip install -r requirements.txt
```

### 4. İlk admin yarat
```bash
python scripts/create_admin.py
```

### 5. API-ni işə sal
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. API dokumentasiya
http://localhost:8000/docs

---

## 📂 LAYİHƏ STRUKTURU

```
made-az-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app
│   ├── database.py                # PostgreSQL connection
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # Settings
│   │   ├── security.py            # Auth & JWT
│   │   └── utils.py               # File upload utilities
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py                # User + Role enum
│   │   ├── product.py             # Product, Category, Brand
│   │   ├── order.py               # Order, OrderItem, Wishlist
│   │   └── newsletter.py          # Newsletter
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py                # Pydantic schemas
│   │   ├── product.py
│   │   └── order.py
│   │
│   └── api/
│       ├── __init__.py
│       ├── auth.py                # Login/Register
│       ├── products.py            # Public product API
│       ├── categories.py          # Categories
│       ├── brands.py              # Brands
│       ├── orders.py              # User orders
│       ├── wishlist.py            # Wishlist
│       └── admin.py               # 🔥 ADMIN PANEL API
│
├── scripts/
│   └── create_admin.py            # Admin yaratmaq
│
├── uploads/
│   └── products/                  # Şəkillər burada saxlanır
│
├── .env                           # Environment variables
├── requirements.txt
└── README_ADMIN.md               # Bu fyl
```

---

## 🐛 Troubleshooting

**Token yanlışdır:**
```json
{
  "detail": "Token yanlışdır və ya vaxtı keçib"
}
```
➡️ Yenidən login edin

**Admin hüququ yoxdur:**
```json
{
  "detail": "Bu əməliyyat üçün admin hüquqları lazımdır"
}
```
➡️ İstifadəçinin role="admin" olduğundan əmin olun

**Şəkil formatı yanlışdır:**
```json
{
  "detail": "Yalnız JPG və PNG formatları qəbul edilir"
}
```
➡️ JPEG və ya PNG şəkil yükləyin

**Kateqoriya silinmir:**
```json
{
  "detail": "Bu kateqoriyada 15 məhsul var..."
}
```
➡️ Əvvəlcə məhsulları silin və ya başqa kateqoriyaya köçürün
"""



POSTGRES_USER=postgres
POSTGRES_PASSWORD=Sebahir125385
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_DB=handora
