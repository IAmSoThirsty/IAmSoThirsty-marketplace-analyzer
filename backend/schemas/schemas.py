from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Image schemas
class ImageUpload(BaseModel):
    filename: str
    content_type: str


class ImageResponse(BaseModel):
    id: int
    filename: str
    s3_key: str
    content_type: Optional[str]
    size: Optional[int]
    uploaded_at: datetime
    user_id: int
    
    class Config:
        from_attributes = True


# Job schemas
class JobCreate(BaseModel):
    job_type: str = Field(..., pattern="^(analysis|marketplace)$")


class JobResponse(BaseModel):
    id: int
    celery_task_id: Optional[str]
    job_type: str
    status: str
    progress: int
    result: Optional[Dict[str, Any]]
    error: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Analysis schemas
class Detection(BaseModel):
    label: str
    confidence: float
    bbox: Optional[List[float]] = None  # [x1, y1, x2, y2]


class AnalysisResponse(BaseModel):
    id: int
    image_id: int
    job_id: Optional[int]
    model_type: str
    model_version: Optional[str]
    detections: List[Detection]
    labels: List[str]
    confidence_scores: Dict[str, float]
    processing_time: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Marketplace schemas
class MarketplaceItemResponse(BaseModel):
    id: int
    analysis_id: int
    job_id: Optional[int]
    provider: str
    item_name: str
    item_url: Optional[str]
    price: Optional[float]
    currency: str = "USD"
    condition: Optional[str]
    availability: Optional[str]
    image_url: Optional[str]
    relevance_score: Optional[float]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    
    class Config:
        from_attributes = True


class MarketplaceQuery(BaseModel):
    analysis_id: int
    providers: Optional[List[str]] = ["ebay", "amazon", "stockx", "grailed"]


# WebSocket messages
class WSMessage(BaseModel):
    type: str
    job_id: Optional[int]
    data: Dict[str, Any]


class AnalysisRequest(BaseModel):
    image_id: int


class MarketplaceRequest(BaseModel):
    analysis_id: int
    providers: Optional[List[str]] = None
