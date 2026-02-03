import asyncio
from datetime import datetime
from backend.celery_app import celery_app
from backend.tasks.analysis_tasks import SyncSessionLocal, JobTask
from backend.services.marketplace_service import marketplace_service
from backend.models.models import Job, Analysis, MarketplaceItem


@celery_app.task(base=JobTask, bind=True)
def search_marketplace_task(self, analysis_id: int, job_id: int, providers: list = None):
    """Celery task for marketplace searches."""
    db = SyncSessionLocal()
    
    try:
        # Update job status
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        job.status = "processing"
        job.progress = 10
        db.commit()
        
        # Get analysis
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not analysis:
            raise ValueError(f"Analysis {analysis_id} not found")
        
        job.progress = 20
        db.commit()
        
        # Build search query from detected labels
        if not analysis.labels:
            raise ValueError("No labels found in analysis")
        
        # Use top labels for search query
        query = " ".join(analysis.labels[:3])
        
        job.progress = 30
        db.commit()
        
        # Search marketplaces
        marketplace_results = asyncio.run(
            marketplace_service.search_all_providers(
                query=query,
                provider_names=providers,
                max_results_per_provider=10
            )
        )
        
        job.progress = 70
        db.commit()
        
        # Store marketplace items
        stored_items = []
        for item_data in marketplace_results:
            item = MarketplaceItem(
                analysis_id=analysis_id,
                job_id=job_id,
                provider=item_data['provider'],
                item_name=item_data['item_name'],
                item_url=item_data.get('item_url'),
                price=item_data.get('price'),
                currency=item_data.get('currency', 'USD'),
                condition=item_data.get('condition'),
                availability=item_data.get('availability'),
                image_url=item_data.get('image_url'),
                relevance_score=item_data.get('relevance_score'),
                metadata=item_data.get('metadata')
            )
            db.add(item)
            stored_items.append({
                "provider": item.provider,
                "item_name": item.item_name,
                "price": item.price,
                "relevance_score": item.relevance_score
            })
        
        db.commit()
        
        job.progress = 100
        db.commit()
        
        return {
            "items_found": len(stored_items),
            "items": stored_items[:20],  # Return top 20
            "query": query
        }
    
    except Exception as e:
        job.status = "failed"
        job.error = str(e)
        db.commit()
        raise
    
    finally:
        db.close()
