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
        # In a real implementation, we would:
        # 1. Authenticate with Notion API using the token
        # 2. Fetch the page content
        # 3. Convert to website format
        # 4. Save to database
        # 5. Return website ID
        
        # For now, we'll mock the response
        website_id = f"website_{request.page_id[:8]}"
        
        # Save request to database
        await db.websites.insert_one({
            "website_id": website_id,
            "notion_page_id": request.page_id,
            "template_id": request.template_id,
            "status": "created"
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
