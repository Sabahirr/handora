from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserResponse, PasswordUpdate
from app.models.user import User
from app.core.security import get_current_user, verify_password, hash_password

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Cari istifadəçinin profil məlumatlarını qaytarır
    
    **Authentication required**: Bearer token
    
    Returns:
    - User məlumatları (id, email, full_name, phone, created_at)
    """
    return current_user


@router.put("/me/password", status_code=status.HTTP_200_OK)
def update_user_password(
    password_data: PasswordUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cari istifadəçinin şifrəsini yeniləyir
    
    **Authentication required**: Bearer token
    
    Request Body:
    - **current_password**: Mövcud şifrə (təsdiq üçün)
    - **new_password**: Yeni şifrə
    
    Returns:
    - Uğur mesajı
    
    Errors:
    - 400: Mövcud şifrə səhvdir
    - 401: Token yoxdur və ya düzgün deyil
    """
    # Mövcud şifrəni yoxla
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mövcud şifrə səhvdir"
        )
    
    # Yeni şifrəni hash-lə və yadda saxla
    current_user.password_hash = hash_password(password_data.new_password)
    db.commit()
    db.refresh(current_user)
    
    return {
        "message": "Şifrə uğurla yeniləndi",
        "success": True
    }