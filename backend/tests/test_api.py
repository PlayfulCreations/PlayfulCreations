import pytest
from httpx import AsyncClient
from ..server import app, db
import json

@pytest.mark.asyncio
async def test_root():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Notion to Website API"}

@pytest.mark.asyncio
async def test_get_templates():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/templates")
    assert response.status_code == 200
    templates = response.json()["templates"]
    assert len(templates) > 0
    assert all(key in templates[0] for key in ["id", "name", "description", "preview_url", "type"])

@pytest.mark.asyncio
async def test_convert_notion_page():
    test_data = {
        "page_id": "test_page_123",
        "template_id": "landing-page",
        "notion_token": "test_token"
    }
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/convert", json=test_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "website_id" in data
    assert data["status"] == "created"
    assert "preview_url" in data

    # Verify data was saved to database
    website = await db.websites.find_one({"website_id": data["website_id"]})
    assert website is not None
    assert website["notion_page_id"] == test_data["page_id"]
    assert website["template_id"] == test_data["template_id"]

@pytest.mark.asyncio
async def test_customize_with_ai():
    test_data = {
        "website_id": "test_website_123",
        "prompt": "Make the header larger"
    }
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/customize", json=test_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["website_id"] == test_data["website_id"]
    assert "message" in data
    assert data["status"] == "updated"

@pytest.mark.asyncio
async def test_get_website_preview():
    # First create a website
    website_data = {
        "website_id": "test_preview_123",
        "notion_page_id": "test_page",
        "template_id": "landing-page",
        "status": "created"
    }
    await db.websites.insert_one(website_data)
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(f"/api/preview/{website_data['website_id']}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["website_id"] == website_data["website_id"]
    assert data["template_id"] == website_data["template_id"]
    assert data["notion_page_id"] == website_data["notion_page_id"]
    assert data["status"] == website_data["status"]

@pytest.mark.asyncio
async def test_get_nonexistent_preview():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/preview/nonexistent")
    assert response.status_code == 404
    assert response.json()["detail"] == "Website not found"

@pytest.mark.asyncio
async def test_cleanup():
    # Clean up test data after tests
    await db.websites.delete_many({
        "website_id": {"$in": ["test_preview_123", "test_website_123"]}
    })
