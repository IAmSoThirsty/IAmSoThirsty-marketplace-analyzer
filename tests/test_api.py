import pytest
from httpx import AsyncClient
from backend.main import app


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test the root endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data


@pytest.mark.asyncio
async def test_health_endpoint():
    """Test the health check endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_list_images():
    """Test listing images."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/images/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
