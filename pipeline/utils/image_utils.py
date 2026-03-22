"""Image utilities — base64 encoding helpers for Vision API."""
import base64
from pathlib import Path


def encode_image_to_base64(image_path: str) -> str:
    """Read an image file and return its base64-encoded content string."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def image_path_to_data_url(image_path: str, mime_type: str = "image/jpeg") -> str:
    """Convert an image file path to a base64 data URL for Vision API payloads."""
    b64 = encode_image_to_base64(image_path)
    return f"data:{mime_type};base64,{b64}"
