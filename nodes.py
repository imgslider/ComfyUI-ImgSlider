import torch
import numpy as np
from PIL import Image
import io
import base64
import requests
import os
import random
import folder_paths
from typing import Dict, Any


class ImgSliderNode:
    """
    ComfyUI node for creating before/after image comparison sliders with imgslider.com
    """

    def __init__(self):
        self.output_dir = folder_paths.get_temp_directory()
        self.type = "temp"
        self.prefix_append = "_imgslider_" + ''.join(random.choice("abcdefghijklmnopqrstupvxyz") for x in range(5))
        self.compress_level = 1

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image_a": ("IMAGE",),
                "image_b": ("IMAGE",),
            },
            "optional": {
                "title": ("STRING", {"default": ""}),
                "api_key": ("STRING", {"default": ""}),
                "publish": ("BOOLEAN", {"default": False, "label_on": "YES", "label_off": "NO"}),
            }
        }

    DESCRIPTION = "Create before/after image comparison sliders. Publish to imgslider.com for shareable links. Works without API key (anonymous, expires in 30 days) or with API key (permanent, editable)."

    RETURN_TYPES = ()
    FUNCTION = "process"
    CATEGORY = "ImgSlider"
    OUTPUT_NODE = True

    # Alternative search terms for discoverability
    SEARCH_ALIASES = ["comparison", "compare", "before after", "diff", "side by side", "image diff"]

    @classmethod
    def VALIDATE_INPUTS(cls, image_a, image_b, **kwargs):
        """Validate inputs before execution"""
        if image_a is None:
            return "Image A is required"
        if image_b is None:
            return "Image B is required"
        return True

    def tensor_to_pil(self, image_tensor: torch.Tensor) -> Image.Image:
        """Convert a ComfyUI tensor to PIL Image"""
        if image_tensor.dim() == 4:
            image = image_tensor[0]
        else:
            image = image_tensor

        numpy_image = image.cpu().numpy()
        numpy_image = np.clip(numpy_image * 255, 0, 255).astype(np.uint8)
        return Image.fromarray(numpy_image, mode='RGB')

    def pil_to_base64(self, pil_image: Image.Image, quality: int = 85) -> str:
        """Convert PIL Image to base64 data URL (WebP for smaller size)"""
        buffer = io.BytesIO()
        # Use WebP for much smaller file sizes (typically 30-50% smaller than PNG)
        pil_image.save(buffer, format='WEBP', quality=quality)
        buffer.seek(0)
        b64 = base64.b64encode(buffer.read()).decode('utf-8')
        return f"data:image/webp;base64,{b64}"

    def save_image(self, pil_image: Image.Image, prefix: str) -> dict:
        """Save image to temp directory and return file info"""
        counter = random.randint(0, 99999)
        file = f"{prefix}{self.prefix_append}_{counter:05}_.png"
        filepath = os.path.join(self.output_dir, file)
        pil_image.save(filepath, compress_level=self.compress_level)

        return {
            "filename": file,
            "subfolder": "",
            "type": self.type
        }

    def create_slider_api(self, before_b64: str, after_b64: str,
                         title: str, api_key: str = "") -> Dict[str, Any]:
        """Create a slider via imgslider.com API. Works with or without API key."""
        api_url = "https://api.imgslider.com/v1/sliders/external"

        payload = {
            "before_image": before_b64,
            "after_image": after_b64,
            "title": title or "ComfyUI Slider",
            "before_label": "Before",
            "after_label": "After",
        }

        headers = {
            "Content-Type": "application/json"
        }

        # Add auth header only if API key provided
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        response = requests.post(api_url, json=payload, headers=headers, timeout=60)

        if response.status_code == 201:
            return response.json()
        elif response.status_code == 429:
            raise Exception("Rate limit exceeded. Anonymous users can create 20 sliders per day.")
        else:
            raise Exception(f"API Error {response.status_code}: {response.text}")

    def process(self, image_a: torch.Tensor, image_b: torch.Tensor,
                title: str = "",
                api_key: str = "",
                publish: bool = False) -> Dict[str, Any]:
        """Process images and optionally publish to imgslider.com"""

        print(f"[ImgSlider] publish={publish}, api_key={'set' if api_key else 'empty'}")

        # Ensure images are the same size
        if image_a.shape != image_b.shape:
            image_b = torch.nn.functional.interpolate(
                image_b.permute(0, 3, 1, 2),
                size=(image_a.shape[1], image_a.shape[2]),
                mode='bilinear',
                align_corners=False
            ).permute(0, 2, 3, 1)

        # Convert to PIL
        image_a_pil = self.tensor_to_pil(image_a)
        image_b_pil = self.tensor_to_pil(image_b)

        # Save to temp files for preview (swap order: B first, then A for correct slider display)
        image_b_info = self.save_image(image_b_pil, "image_b")
        image_a_info = self.save_image(image_a_pil, "image_a")

        # Handle API if enabled
        slider_url = ""
        api_error = ""

        if publish:
            try:
                image_a_b64 = self.pil_to_base64(image_a_pil)
                image_b_b64 = self.pil_to_base64(image_b_pil)
                result = self.create_slider_api(
                    image_a_b64, image_b_b64,
                    title,
                    api_key
                )
                slider_url = result.get("url", "")
                if api_key:
                    print(f"\n🔗 ImgSlider URL: {slider_url}\n")
                else:
                    print(f"\n🔗 ImgSlider URL: {slider_url} (anonymous - expires in 30 days)\n")
            except Exception as e:
                api_error = str(e)
                print(f"\n❌ ImgSlider API Error: {api_error}\n")

        return {
            "ui": {
                "slider_images": [image_b_info, image_a_info],
                "slider_url": [slider_url],
                "slider_error": [api_error],
            }
        }


# Node registration
NODE_CLASS_MAPPINGS = {
    "ImgSlider": ImgSliderNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImgSlider": "Image Compare (ImgSlider)",
}
