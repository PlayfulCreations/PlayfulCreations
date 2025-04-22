from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
import httpx
import json
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

# /backend 
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'notion_to_website')]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Models
class NotionPageRequest(BaseModel):
    page_id: str
    template_id: str
    notion_token: Optional[str] = None

class AICustomizationRequest(BaseModel):
    website_id: str
    prompt: str

class Template(BaseModel):
    id: str
    name: str
    description: str
    preview_url: str
    type: str

# Templates
TEMPLATES = [
    {
        "id": "landing-page",
        "name": "Landing Page",
        "description": "A sleek single-page website perfect for showcasing your product or service",
        "preview_url": "/templates/landing-page.png",
        "type": "landing"
    },
    {
        "id": "multi-page",
        "name": "Multi-Page Website",
        "description": "A complete website with navigation menu and multiple pages",
        "preview_url": "/templates/multi-page.png",
        "type": "multi-page"
    },
    {
        "id": "portfolio",
        "name": "Portfolio",
        "description": "Showcase your work with this elegant portfolio template",
        "preview_url": "/templates/portfolio.png",
        "type": "portfolio"
    },
    {
        "id": "blog",
        "name": "Blog",
        "description": "Share your thoughts with a clean, reader-friendly blog design",
        "preview_url": "/templates/blog.png",
        "type": "blog"
    },
    {
        "id": "dashboard",
        "name": "Dashboard",
        "description": "Data-focused layout ideal for analytics and reporting",
        "preview_url": "/templates/dashboard.png",
        "type": "dashboard"
    }
]

@app.get("/")
async def root():
    return {"message": "Notion to Website API"}

@app.get("/api/templates")
async def get_templates():
    return {"templates": TEMPLATES}

@app.post("/api/convert")
async def convert_notion_page(request: NotionPageRequest):
    try:
        # Extract page ID from URL if needed
        page_id = request.page_id
        if "notion.so/" in page_id:
            # Extract the actual page ID from the URL
            # Example URL: https://www.notion.so/myworkspace/My-Page-123456789
            parts = page_id.split("notion.so/")
            if len(parts) > 1:
                page_id = parts[1].split("/")[-1].split("-")[-1]
        
        logger.info(f"Converting Notion page: {page_id}")
        
        # In a real implementation, we would use the Notion API with token
        if request.notion_token:
            logger.info("Using provided Notion token for authentication")
            # This would be where we authenticate with the token
        
        # Generate a unique website ID
        import uuid
        website_id = f"website_{uuid.uuid4().hex[:8]}"
        
        # Mock content fetching - in real implementation, we would fetch from Notion API
        mock_content = {
            "title": "My Notion Page",
            "blocks": [
                {"type": "heading", "content": "Welcome to my website"},
                {"type": "paragraph", "content": "This website was generated from a Notion page"},
                {"type": "image", "url": "https://images.unsplash.com/photo-1499750310107-5fef28a66643"}
            ]
        }
        
        # Save request and mock content to database
        await db.websites.insert_one({
            "website_id": website_id,
            "notion_page_id": page_id,
            "template_id": request.template_id,
            "status": "created",
            "content": mock_content
        })
        
        return {
            "website_id": website_id,
            "status": "created",
            "preview_url": f"/preview/{website_id}"
        }
    except Exception as e:
        logger.error(f"Error converting Notion page: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/customize")
async def customize_with_ai(request: AICustomizationRequest):
    try:
        # In a real implementation, we would:
        # 1. Fetch the website details
        # 2. Process the AI prompt
        # 3. Update the website
        # 4. Return updated website details
        
        # For now, we'll mock the response
        return {
            "website_id": request.website_id,
            "message": f"Applied changes: {request.prompt}",
            "status": "updated"
        }
    except Exception as e:
        logger.error(f"Error customizing website: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/preview/{website_id}")
async def get_website_preview(website_id: str):
    website = await db.websites.find_one({"website_id": website_id})
    if not website:
        raise HTTPException(status_code=404, detail="Website not found")
    
    # In a real implementation, we would generate and return the full website HTML
    # For now, we'll return the basic info
    return {
        "website_id": website_id,
        "template_id": website.get("template_id"),
        "notion_page_id": website.get("notion_page_id"),
        "status": website.get("status")
    }

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
