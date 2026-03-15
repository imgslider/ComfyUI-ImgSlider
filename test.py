"""
Unit tests for ComfyUI-ImgSlider node
Run with: python test.py
"""

import unittest
from unittest.mock import patch, MagicMock
import base64
import io
from PIL import Image


def create_test_image(width=100, height=100, color=(255, 0, 0)):
    """Create a simple test image and return as base64 data URL."""
    img = Image.new('RGB', (width, height), color)
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    b64 = base64.b64encode(buffer.read()).decode('utf-8')
    return f"data:image/png;base64,{b64}"


class TestAPIPayload(unittest.TestCase):
    """Test API payload construction (mocked, no real API calls)."""

    API_URL = "https://api.imgslider.com/v1/sliders/external"

    @patch('requests.post')
    def test_anonymous_payload_structure(self, mock_post):
        """Test that anonymous request has correct payload structure."""
        import requests

        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": "test-uuid",
            "url": "https://imgslider.com/test-uuid"
        }
        mock_post.return_value = mock_response

        before_image = create_test_image(100, 100, (255, 0, 0))
        after_image = create_test_image(100, 100, (0, 255, 0))

        payload = {
            "before_image": before_image,
            "after_image": after_image,
            "title": "Test Slider",
        }

        response = requests.post(
            self.API_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )

        # Verify request was made correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(call_args[0][0], self.API_URL)
        self.assertIn("before_image", call_args[1]["json"])
        self.assertIn("after_image", call_args[1]["json"])
        self.assertNotIn("Authorization", call_args[1]["headers"])

        # Verify response handling
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertIn("id", data)
        self.assertIn("url", data)

    @patch('requests.post')
    def test_authenticated_payload_structure(self, mock_post):
        """Test that authenticated request includes Authorization header."""
        import requests

        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": "test-uuid",
            "url": "https://imgslider.com/test-uuid"
        }
        mock_post.return_value = mock_response

        before_image = create_test_image(100, 100, (255, 0, 0))
        after_image = create_test_image(100, 100, (0, 255, 0))
        api_key = "imgslider_test_key_123"

        payload = {
            "before_image": before_image,
            "after_image": after_image,
            "title": "Test Slider",
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        response = requests.post(
            self.API_URL,
            json=payload,
            headers=headers,
            timeout=60
        )

        # Verify auth header was included
        call_args = mock_post.call_args
        self.assertIn("Authorization", call_args[1]["headers"])
        self.assertEqual(call_args[1]["headers"]["Authorization"], f"Bearer {api_key}")


class TestImageProcessing(unittest.TestCase):
    """Test image processing functions."""

    def test_create_test_image(self):
        """Test that we can create valid test images."""
        data_url = create_test_image(50, 50, (128, 128, 128))

        self.assertTrue(data_url.startswith("data:image/png;base64,"))

        # Decode and verify
        b64_data = data_url.split(",")[1]
        img_data = base64.b64decode(b64_data)
        img = Image.open(io.BytesIO(img_data))

        self.assertEqual(img.size, (50, 50))
        self.assertEqual(img.mode, "RGB")


if __name__ == "__main__":
    print("Running ImgSlider node tests...\n")
    unittest.main(verbosity=2)
