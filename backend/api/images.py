from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from backend.database.session import get_db
from backend.schemas.schemas import ImageResponse
from backend.models.models import Image, User
from backend.services.s3_service import s3_service

router = APIRouter(prefix="/images", tags=["Images"])


@router.post("/upload", response_model=ImageResponse, status_code=status.HTTP_201_CREATED)
async def upload_image(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Upload an image to S3."""
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    # Get or create demo user
    result = await db.execute(select(User).limit(1))
    user = result.scalar_one_or_none()
    
    if not user:
        from backend.core.security import get_password_hash
        user = User(
            email="demo@example.com",
            username="demo",
            hashed_password=get_password_hash("demo123")
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    
    # Read file content
    file_content = await file.read()
    
    # Upload to S3
    s3_key = await s3_service.upload_file(
        file_content=file_content,
        filename=file.filename,
        content_type=file.content_type
    )
    
    # Create image record
    image = Image(
        user_id=user.id,
        filename=file.filename,
        s3_key=s3_key,
        content_type=file.content_type,
        size=len(file_content)
    )
    db.add(image)
    await db.commit()
    await db.refresh(image)
    
    return image


@router.get("/", response_model=List[ImageResponse])
async def list_images(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List all images."""
    result = await db.execute(
        select(Image).offset(skip).limit(limit).order_by(Image.uploaded_at.desc())
    )
    images = result.scalars().all()
    return images


@router.get("/{image_id}", response_model=ImageResponse)
async def get_image(image_id: int, db: AsyncSession = Depends(get_db)):
    """Get image by ID."""
    result = await db.execute(select(Image).where(Image.id == image_id))
    image = result.scalar_one_or_none()
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    return image


@router.get("/{image_id}/download-url")
async def get_image_download_url(image_id: int, db: AsyncSession = Depends(get_db)):
    """Get presigned URL for downloading an image."""
    result = await db.execute(select(Image).where(Image.id == image_id))
    image = result.scalar_one_or_none()
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    # Generate presigned URL
    url = await s3_service.get_presigned_url(image.s3_key)
    
    return {"url": url}


@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(image_id: int, db: AsyncSession = Depends(get_db)):
    """Delete an image."""
    result = await db.execute(select(Image).where(Image.id == image_id))
    image = result.scalar_one_or_none()
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    # Delete from S3
    await s3_service.delete_file(image.s3_key)
    
    # Delete from database
    await db.delete(image)
    await db.commit()
    
    return None
