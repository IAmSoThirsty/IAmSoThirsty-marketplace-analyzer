from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database.session import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    images = relationship("Image", back_populates="user", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="user", cascade="all, delete-orphan")


class Image(Base):
    __tablename__ = "images"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    s3_key = Column(String, nullable=False, unique=True)
    content_type = Column(String)
    size = Column(Integer)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="images")
    analyses = relationship("Analysis", back_populates="image", cascade="all, delete-orphan")


class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    celery_task_id = Column(String, unique=True, index=True)
    job_type = Column(String, nullable=False)  # 'analysis', 'marketplace'
    status = Column(String, default="pending")  # pending, processing, completed, failed
    progress = Column(Integer, default=0)
    result = Column(JSON)
    error = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="jobs")


class Analysis(Base):
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("images.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    model_type = Column(String, nullable=False)
    model_version = Column(String)
    detections = Column(JSON)  # List of detected objects with bounding boxes
    labels = Column(JSON)  # List of detected labels
    confidence_scores = Column(JSON)  # Confidence scores for detections
    processing_time = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    image = relationship("Image", back_populates="analyses")
    marketplace_items = relationship("MarketplaceItem", back_populates="analysis", cascade="all, delete-orphan")


class MarketplaceItem(Base):
    __tablename__ = "marketplace_items"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    provider = Column(String, nullable=False)  # ebay, amazon, stockx, grailed
    item_name = Column(String, nullable=False)
    item_url = Column(String)
    price = Column(Float)
    currency = Column(String, default="USD")
    condition = Column(String)
    availability = Column(String)
    image_url = Column(String)
    relevance_score = Column(Float)  # Our calculated relevance score
    metadata = Column(JSON)  # Additional provider-specific data
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    analysis = relationship("Analysis", back_populates="marketplace_items")
