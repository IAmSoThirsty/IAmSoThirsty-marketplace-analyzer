import pytest
import asyncio
from backend.models.models import User, Image, Job, Analysis, MarketplaceItem
from backend.database.session import engine, Base, AsyncSessionLocal
from sqlalchemy import select


@pytest.fixture
async def db_session():
    """Create a test database session."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_create_user(db_session):
    """Test creating a user."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.username == "testuser"


@pytest.mark.asyncio
async def test_create_image(db_session):
    """Test creating an image."""
    # Create user first
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # Create image
    image = Image(
        user_id=user.id,
        filename="test.jpg",
        s3_key="images/test.jpg",
        content_type="image/jpeg",
        size=1024
    )
    db_session.add(image)
    await db_session.commit()
    await db_session.refresh(image)
    
    assert image.id is not None
    assert image.user_id == user.id
    assert image.filename == "test.jpg"


@pytest.mark.asyncio
async def test_create_job(db_session):
    """Test creating a job."""
    # Create user
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # Create job
    job = Job(
        user_id=user.id,
        job_type="analysis",
        status="pending"
    )
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)
    
    assert job.id is not None
    assert job.user_id == user.id
    assert job.job_type == "analysis"
    assert job.status == "pending"


@pytest.mark.asyncio
async def test_create_analysis(db_session):
    """Test creating an analysis."""
    # Create user
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # Create image
    image = Image(
        user_id=user.id,
        filename="test.jpg",
        s3_key="images/test.jpg",
        content_type="image/jpeg",
        size=1024
    )
    db_session.add(image)
    await db_session.commit()
    await db_session.refresh(image)
    
    # Create analysis
    analysis = Analysis(
        image_id=image.id,
        model_type="yolov8",
        detections=[{"label": "person", "confidence": 0.95}],
        labels=["person"],
        confidence_scores={"person": 0.95}
    )
    db_session.add(analysis)
    await db_session.commit()
    await db_session.refresh(analysis)
    
    assert analysis.id is not None
    assert analysis.image_id == image.id
    assert analysis.model_type == "yolov8"
    assert len(analysis.detections) == 1
