handora-backend/

├── app/

│   ├── __init__.py

│   ├── main.py                 # FastAPI app

│   ├── database.py             # PostgreSQL connection

│   │

│   ├── core/

│   │   ├── __init__.py

│   │   ├── config.py           # Konfiqurasiya

│   │   └── security.py         # Şifrə hash və JWT

│   │

│   ├── models/

│   │   ├── __init__.py

│   │   ├── user.py             # User model

│   │   ├── product.py          # Product, Category, Brand

│   │   ├── order.py            # Order, OrderItem, Wishlist

│   │   └── newsletter.py       # Newsletter

│   │

│   ├── schemas/

│   │   ├── __init__.py

│   │   ├── user.py             # User Pydantic schemas

│   │   ├── product.py          # Product schemas

│   │   └── order.py            # Order schemas

│   │

│   └── api/

│       ├── __init__.py

│       ├── auth.py             # Qeydiyyat/Giriş

│       ├── products.py         # Məhsul API

│       ├── categories.py       # Kateqoriya API

│       ├── brands.py           # Brend API

│       ├── orders.py           # Sifariş API

│       └── wishlist.py         # İstək siyahısı

│

├── .env                         # Environment variables

├── requirements.txt

└── README.md