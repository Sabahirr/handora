"""
İlk admin istifadəçi yaratmaq üçün skript
İstifadə: python scripts/create_admin.py
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.user import User, UserRole
from app.core.security import hash_password

def create_admin():
    db = SessionLocal()
    
    try:
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if existing_admin:
            print(f"Admin artıq mövcuddur: {existing_admin.email}")
            return
        
        # Get admin details
        email = input("Admin email: ")
        password = input("Şifrə: ")
        full_name = input("Ad Soyad: ")
        phone = input("Telefon: ")
        
        # Create admin user
        admin = User(
            email=email,
            password_hash=hash_password(password),
            full_name=full_name,
            phone=phone,
            role=UserRole.ADMIN,
            is_active=True
        )
        
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        print(f"\n✅ Admin uğurla yaradıldı!")
        print(f"Email: {admin.email}")
        print(f"ID: {admin.id}")
        
    except Exception as e:
        print(f"❌ Xəta: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()