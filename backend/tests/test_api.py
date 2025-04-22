import pytest
import requests
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get the backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')

class TestNotionToWebsiteAPI:
    def setup_method(self):
        self.base_url = BACKEND_URL
        logger.info(f"Testing against backend URL: {self.base_url}")

    def test_get_templates(self):
        """Test retrieving templates"""
        response = requests.get(f"{self.base_url}/api/templates")
        assert response.status_code == 200
        data = response.json()
        assert "templates" in data
        templates = data["templates"]
        assert len(templates) > 0
        assert all(key in templates[0] for key in ["id", "name", "description", "preview_url", "type"])
        logger.info("✅ Templates API test passed")

    def test_convert_notion_page(self):
        """Test converting a Notion page"""
        test_data = {
            "page_id": "test-page-123",
            "template_id": "landing-page",
            "notion_token": "test-token"
        }
        response = requests.post(f"{self.base_url}/api/convert", json=test_data)
        assert response.status_code == 200
        data = response.json()
        assert "website_id" in data
        assert "status" in data
        assert "preview_url" in data
        assert data["status"] == "created"
        logger.info("✅ Convert API test passed")
        return data["website_id"]

    def test_ai_customization(self):
        """Test AI customization"""
        # First create a website
        website_id = self.test_convert_notion_page()
        
        test_data = {
            "website_id": website_id,
            "prompt": "Make the design more modern"
        }
        response = requests.post(f"{self.base_url}/api/customize", json=test_data)
        assert response.status_code == 200
        data = response.json()
        assert data["website_id"] == website_id
        assert "status" in data
        assert data["status"] == "updated"
        logger.info("✅ AI Customization API test passed")

    def test_website_preview(self):
        """Test website preview"""
        # First create a website
        website_id = self.test_convert_notion_page()
        
        response = requests.get(f"{self.base_url}/api/preview/{website_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["website_id"] == website_id
        assert "template_id" in data
        assert "content" in data
        assert "status" in data
        logger.info("✅ Preview API test passed")

    def test_invalid_website_preview(self):
        """Test invalid website preview"""
        response = requests.get(f"{self.base_url}/api/preview/nonexistent-id")
        assert response.status_code == 404
        logger.info("✅ Invalid preview API test passed")

if __name__ == "__main__":
    # Create test instance
    tester = TestNotionToWebsiteAPI()
    tester.setup_method()

    # Run all tests
    try:
        tester.test_get_templates()
        tester.test_convert_notion_page()
        tester.test_ai_customization()
        tester.test_website_preview()
        tester.test_invalid_website_preview()
        logger.info("🎉 All API tests passed successfully!")
    except Exception as e:
        logger.error(f"❌ Tests failed: {str(e)}")
        raise
