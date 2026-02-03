from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from backend.database.session import get_db
from backend.schemas.schemas import MarketplaceRequest, MarketplaceItemResponse, JobResponse
from backend.models.models import MarketplaceItem, Job, Analysis, User
from backend.tasks.marketplace_tasks import search_marketplace_task

router = APIRouter(prefix="/marketplace", tags=["Marketplace"])


@router.post("/search", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def search_marketplaces(
    request: MarketplaceRequest,
    db: AsyncSession = Depends(get_db)
):
    """Start marketplace search job."""
    # Check if analysis exists
    result = await db.execute(select(Analysis).where(Analysis.id == request.analysis_id))
    analysis = result.scalar_one_or_none()
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )
    
    # Get image and user
    result = await db.execute(
        select(User)
        .join(Image)
        .where(Image.id == analysis.image_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Create job
    job = Job(
        user_id=user.id,
        job_type="marketplace",
        status="pending"
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    
    # Start Celery task
    providers = request.providers or ["ebay", "amazon", "stockx", "grailed"]
    task = search_marketplace_task.delay(request.analysis_id, job.id, providers)
    
    # Update job with task ID
    job.celery_task_id = task.id
    await db.commit()
    await db.refresh(job)
    
    return job


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_marketplace_job(job_id: int, db: AsyncSession = Depends(get_db)):
    """Get marketplace job status."""
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    return job


@router.get("/analysis/{analysis_id}", response_model=List[MarketplaceItemResponse])
async def get_marketplace_items(
    analysis_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get marketplace items for an analysis."""
    result = await db.execute(
        select(MarketplaceItem)
        .where(MarketplaceItem.analysis_id == analysis_id)
        .order_by(MarketplaceItem.relevance_score.desc())
        .offset(skip)
        .limit(limit)
    )
    items = result.scalars().all()
    
    return items


@router.get("/item/{item_id}", response_model=MarketplaceItemResponse)
async def get_marketplace_item(item_id: int, db: AsyncSession = Depends(get_db)):
    """Get marketplace item by ID."""
    result = await db.execute(select(MarketplaceItem).where(MarketplaceItem.id == item_id))
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    return item
