from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name_az = Column(String(255), nullable=False)
    name_en = Column(String(255), nullable=False)
    name_ru = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    products = relationship("Product", back_populates="category")
    parent = relationship("Category", remote_side=[id])

class Brand(Base):
    __tablename__ = "brands"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    logo_url = Column(String(500))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    products = relationship("Product", back_populates="brand")

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name_az = Column(String(500), nullable=False)
    name_en = Column(String(500), nullable=False)
    name_ru = Column(String(500), nullable=False)
    description_az = Column(Text)
    description_en = Column(Text)
    description_ru = Column(Text)
    price = Column(Float, nullable=False)
    discount_price = Column(Float, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    brand_id = Column(Integer, ForeignKey("brands.id"))
    image_urls = Column(ARRAY(String), nullable=True)
    stock = Column(Integer, default=0)
    is_new = Column(Boolean, default=True)
    is_sale = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    category = relationship("Category", back_populates="products")
    brand = relationship("Brand", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")
