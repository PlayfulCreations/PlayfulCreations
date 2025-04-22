import pytest
import httpx
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')

class TestNotionToWebsiteAPI:
    def setup_method(self):
        """Setup test client and base URL"""
        self.base_url = BACKEND_URL
        self.client = httpx.Client(base_url=self.base_url)
        self.test_notion_url = "https://www.notion.so/myworkspace/My-Page-123456789"
        self.test_template_id = "landing-page"

    def test_root_endpoint(self):
        """Test the root endpoint"""
        response = self.client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()

    def test_get_templates(self):
        """Test getting available templates"""
        response = self.client.get("/api/templates")
        assert response.status_code == 200
        data = response.json()
        assert "templates" in data
        templates = data["templates"]
        assert len(templates) > 0
        assert all(key in templates[0] for key in ["id", "name", "description", "preview_url", "type"])

    def test_convert_notion_page(self):
        """Test converting a Notion page to website"""
        payload = {
            "page_id": self.test_notion_url,
            "template_id": self.test_template_id,
            "notion_token": None
        }
        response = self.client.post("/api/convert", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "website_id" in data
        assert "status" in data
        assert "preview_url" in data
        assert data["status"] == "created"
        
        # Store website_id for other tests
        self.website_id = data["website_id"]

    def test_preview_website(self):
        """Test getting website preview"""
        # First create a website
        payload = {
            "page_id": self.test_notion_url,
            "template_id": self.test_template_id
        }
        create_response = self.client.post("/api/convert", json=payload)
        website_id = create_response.json()["website_id"]

        # Then get its preview
        response = self.client.get(f"/api/preview/{website_id}")
        assert response.status_code == 200
        data = response.json()
        assert "website_id" in data
        assert "template_id" in data
        assert "content" in data
        assert data["template_id"] == self.test_template_id

    def test_ai_customization(self):
        """Test AI customization feature"""
        # First create a website
        payload = {
            "page_id": self.test_notion_url,
            "template_id": self.test_template_id
        }
        create_response = self.client.post("/api/convert", json=payload)
        website_id = create_response.json()["website_id"]

        # Then test customization
        customize_payload = {
            "website_id": website_id,
            "prompt": "Make the header larger and change background to blue"
        }
        response = self.client.post("/api/customize", json=customize_payload)
        assert response.status_code == 200
        data = response.json()
        assert "website_id" in data
        assert "message" in data
        assert "status" in data
        assert data["status"] == "updated"

    def test_invalid_template_id(self):
        """Test error handling for invalid template ID"""
        payload = {
            "page_id": self.test_notion_url,
            "template_id": "invalid-template"
        }
        response = self.client.post("/api/convert", json=payload)
        assert response.status_code == 500  # Should return error

    def test_invalid_website_id_preview(self):
        """Test error handling for invalid website ID in preview"""
        response = self.client.get("/api/preview/invalid-id")
        assert response.status_code == 404  # Should return not found

    def teardown_method(self):
        """Cleanup after tests"""
        self.client.close()
