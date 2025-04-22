import pytest
import httpx
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the backend URL from environment variable
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')

class TestNotionToWebsiteAPI:
    def setup_method(self):
        """Setup test client"""
        self.base_url = BACKEND_URL
        self.client = httpx.Client(base_url=self.base_url)
        self.test_notion_url = "https://www.notion.so/myworkspace/My-Page-123456789"
        self.test_template_id = "landing-page"

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
            "template_id": self.test_template_id
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

    def test_customize_website(self):
        """Test AI customization of website"""
        # First create a website
        payload = {
            "page_id": self.test_notion_url,
            "template_id": self.test_template_id
        }
        response = self.client.post("/api/convert", json=payload)
        website_id = response.json()["website_id"]

        # Now test customization
        customize_payload = {
            "website_id": website_id,
            "prompt": "Make the header bigger"
        }
        response = self.client.post("/api/customize", json=customize_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["website_id"] == website_id
        assert "message" in data
        assert data["status"] == "updated"

    def test_get_website_preview(self):
        """Test getting website preview"""
        # First create a website
        payload = {
            "page_id": self.test_notion_url,
            "template_id": self.test_template_id
        }
        response = self.client.post("/api/convert", json=payload)
        website_id = response.json()["website_id"]

        # Now get preview
        response = self.client.get(f"/api/preview/{website_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["website_id"] == website_id
        assert data["template_id"] == self.test_template_id
        assert "content" in data
        assert "status" in data

    def test_get_website_preview_not_found(self):
        """Test getting preview for non-existent website"""
        response = self.client.get("/api/preview/nonexistent")
        assert response.status_code == 404

    def teardown_method(self):
        """Cleanup after tests"""
        self.client.close()

if __name__ == "__main__":
    pytest.main([__file__])