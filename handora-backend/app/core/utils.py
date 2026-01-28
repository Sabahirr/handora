# ==================== app/core/utils.py ====================
import os
import uuid
from fastapi import UploadFile, HTTPException
from PIL import Image
import aiofiles

UPLOAD_DIR = "uploads/products"
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def validate_image(file: UploadFile):
    """Validate uploaded image"""
    # Check file extension
    ext = file.filename.split('.')[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Yalnız {', '.join(ALLOWED_EXTENSIONS).upper()} formatları qəbul edilir"
        )
    
    # Check content type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Fayl şəkil formatında olmalıdır")

async def save_product_image(file: UploadFile) -> str:
    """Save product image and return URL"""
    validate_image(file)
    
    # Create upload directory
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    # Generate unique filename
    ext = file.filename.split('.')[-1].lower()
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    # Save file
    async with aiofiles.open(filepath, 'wb') as out_file:
        content = await file.read()
        
        # Check file size
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="Şəkil 5MB-dan böyük ola bilməz")
        
        await out_file.write(content)
    
    # Resize and optimize image
    try:
        img = Image.open(filepath)
        
        # Convert RGBA to RGB if necessary
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        
        # Resize if too large
        max_size = (1200, 1200)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Save optimized
        img.save(filepath, optimize=True, quality=85)
    except Exception as e:
        # If optimization fails, delete the file
        if os.path.exists(filepath):
            os.remove(filepath)
        raise HTTPException(status_code=400, detail=f"Şəkil emal edilmədi: {str(e)}")
    
    # Return URL path
    return f"/uploads/products/{filename}"

def delete_file(url: str):
    """Delete file from filesystem"""
    if not url:
        return
    
    # Remove leading slash and convert to filesystem path
    if url.startswith('/'):
        url = url[1:]
    
    filepath = url.replace('/', os.sep)
    
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
        except Exception as e:
            print(f"Could not delete file {filepath}: {e}")