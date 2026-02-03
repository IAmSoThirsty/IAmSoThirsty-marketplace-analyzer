from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from typing import Dict, Set
from backend.core.config import settings
from backend.api import auth, images, analysis, marketplace
from backend.database.session import engine, Base
from sqlalchemy import select
from backend.models.models import Job
from backend.database.session import AsyncSessionLocal


class ConnectionManager:
    """Manage WebSocket connections."""
    
    def __init__(self):
        self.active_connections: Dict[int, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, job_id: int):
        """Connect a WebSocket to a job."""
        await websocket.accept()
        if job_id not in self.active_connections:
            self.active_connections[job_id] = set()
        self.active_connections[job_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, job_id: int):
        """Disconnect a WebSocket from a job."""
        if job_id in self.active_connections:
            self.active_connections[job_id].discard(websocket)
            if not self.active_connections[job_id]:
                del self.active_connections[job_id]
    
    async def send_job_update(self, job_id: int, message: dict):
        """Send update to all connections for a job."""
        if job_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[job_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.add(connection)
            
            # Remove disconnected connections
            for connection in disconnected:
                self.active_connections[job_id].discard(connection)
    
    async def broadcast(self, message: dict):
        """Broadcast to all connections."""
        for job_connections in self.active_connections.values():
            for connection in job_connections:
                try:
                    await connection.send_json(message)
                except Exception:
                    pass


manager = ConnectionManager()


async def job_status_monitor():
    """Background task to monitor job status and send updates via WebSocket."""
    while True:
        try:
            async with AsyncSessionLocal() as db:
                # Get all active jobs
                result = await db.execute(
                    select(Job).where(Job.status.in_(["pending", "processing"]))
                )
                jobs = result.scalars().all()
                
                for job in jobs:
                    # Send update to connected clients
                    await manager.send_job_update(job.id, {
                        "type": "job_update",
                        "job_id": job.id,
                        "status": job.status,
                        "progress": job.progress,
                        "result": job.result
                    })
        except Exception as e:
            print(f"Error in job monitor: {e}")
        
        await asyncio.sleep(2)  # Check every 2 seconds


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    async with engine.begin() as conn:
        # Create tables
        await conn.run_sync(Base.metadata.create_all)
    
    # Start background job monitor
    task = asyncio.create_task(job_status_monitor())
    
    yield
    
    # Shutdown
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


# Create FastAPI app
app = FastAPI(
    title="Marketplace Analyzer",
    description="Production-grade image analysis and marketplace value resolution service",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS + ["*"],  # Allow all for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(images.router)
app.include_router(analysis.router)
app.include_router(marketplace.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Marketplace Analyzer API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.websocket("/ws/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: int):
    """WebSocket endpoint for real-time job updates."""
    await manager.connect(websocket, job_id)
    
    try:
        # Send initial connection message
        await websocket.send_json({
            "type": "connected",
            "job_id": job_id,
            "message": "Connected to job updates"
        })
        
        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_text()
            # Echo back for ping/pong
            await websocket.send_json({
                "type": "pong",
                "message": "pong"
            })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, job_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket, job_id)


@app.websocket("/ws")
async def websocket_all(websocket: WebSocket):
    """WebSocket endpoint for all updates."""
    await websocket.accept()
    
    try:
        # Send initial connection message
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to all updates"
        })
        
        # Keep connection alive
        while True:
            await websocket.receive_text()
            await websocket.send_json({
                "type": "pong",
                "message": "pong"
            })
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")
