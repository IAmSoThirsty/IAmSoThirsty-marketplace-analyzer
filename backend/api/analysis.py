from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from backend.database.session import get_db
from backend.schemas.schemas import AnalysisRequest, AnalysisResponse, JobResponse
from backend.models.models import Analysis, Job, Image, User
from backend.tasks.analysis_tasks import analyze_image_task

router = APIRouter(prefix="/analysis", tags=["Analysis"])


@router.post("/", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def analyze_image(
    request: AnalysisRequest,
    db: AsyncSession = Depends(get_db)
):
    """Start image analysis job."""
    # Check if image exists
    result = await db.execute(select(Image).where(Image.id == request.image_id))
    image = result.scalar_one_or_none()
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    # Get user
    result = await db.execute(select(User).where(User.id == image.user_id))
    user = result.scalar_one_or_none()
    
    # Create job
    job = Job(
        user_id=user.id,
        job_type="analysis",
        status="pending"
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    
    # Start Celery task
    task = analyze_image_task.delay(request.image_id, job.id)
    
    # Update job with task ID
    job.celery_task_id = task.id
    await db.commit()
    await db.refresh(job)
    
    return job


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_analysis_job(job_id: int, db: AsyncSession = Depends(get_db)):
    """Get analysis job status."""
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    return job


@router.get("/image/{image_id}", response_model=List[AnalysisResponse])
async def get_image_analyses(image_id: int, db: AsyncSession = Depends(get_db)):
    """Get all analyses for an image."""
    result = await db.execute(
        select(Analysis).where(Analysis.image_id == image_id).order_by(Analysis.created_at.desc())
    )
    analyses = result.scalars().all()
    
    return analyses


@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(analysis_id: int, db: AsyncSession = Depends(get_db)):
    """Get analysis by ID."""
    result = await db.execute(select(Analysis).where(Analysis.id == analysis_id))
    analysis = result.scalar_one_or_none()
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )
    
    return analysis
