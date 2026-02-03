import asyncio
from datetime import datetime
from celery import Task
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.celery_app import celery_app
from backend.core.config import settings
from backend.services.model_service import model_service
from backend.services.s3_service import s3_service
from backend.models.models import Job, Analysis, Image

# Create sync database session for Celery tasks
sync_db_url = settings.DATABASE_URL.replace("+asyncpg", "")
sync_engine = create_engine(sync_db_url)
SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)


class JobTask(Task):
    """Base task class with job status tracking."""
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure."""
        db = SyncSessionLocal()
        try:
            job = db.query(Job).filter(Job.celery_task_id == task_id).first()
            if job:
                job.status = "failed"
                job.error = str(exc)
                job.completed_at = datetime.utcnow()
                db.commit()
        finally:
            db.close()
    
    def on_success(self, retval, task_id, args, kwargs):
        """Handle task success."""
        db = SyncSessionLocal()
        try:
            job = db.query(Job).filter(Job.celery_task_id == task_id).first()
            if job:
                job.status = "completed"
                job.progress = 100
                job.result = retval
                job.completed_at = datetime.utcnow()
                db.commit()
        finally:
            db.close()


@celery_app.task(base=JobTask, bind=True)
def analyze_image_task(self, image_id: int, job_id: int):
    """Celery task for image analysis."""
    db = SyncSessionLocal()
    
    try:
        # Update job status
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        job.status = "processing"
        job.progress = 10
        db.commit()
        
        # Get image
        image = db.query(Image).filter(Image.id == image_id).first()
        if not image:
            raise ValueError(f"Image {image_id} not found")
        
        job.progress = 20
        db.commit()
        
        # Download image from S3
        image_bytes = asyncio.run(s3_service.download_file(image.s3_key))
        
        job.progress = 40
        db.commit()
        
        # Analyze image
        analysis_result = model_service.analyze_image(image_bytes)
        
        job.progress = 80
        db.commit()
        
        # Create analysis record
        analysis = Analysis(
            image_id=image_id,
            job_id=job_id,
            model_type=analysis_result['model_type'],
            model_version=analysis_result.get('model_version'),
            detections=analysis_result['detections'],
            labels=analysis_result['labels'],
            confidence_scores=analysis_result['confidence_scores'],
            processing_time=analysis_result['processing_time']
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        
        job.progress = 100
        db.commit()
        
        return {
            "analysis_id": analysis.id,
            "labels": analysis.labels,
            "detections": analysis.detections,
            "confidence_scores": analysis.confidence_scores,
            "processing_time": analysis.processing_time
        }
    
    except Exception as e:
        job.status = "failed"
        job.error = str(e)
        db.commit()
        raise
    
    finally:
        db.close()


@celery_app.task(bind=True)
def test_celery_task(self):
    """Simple test task to verify Celery is working."""
    return {"status": "success", "message": "Celery is working!"}
