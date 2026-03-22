import fitz  # PyMuPDF
from pathlib import Path
from PIL import Image
import io

def extract_images_from_pdf(pdf_path: str, output_dir: Path) -> list:
    """Read a PDF and extract each page as a compressed JPEG image.
    
    Uses 100 DPI and JPEG quality=70 to keep images small enough
    for Mistral's vision API rate limits while remaining readable.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    images = []
    
    doc = fitz.open(pdf_path)
    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=100)  # lower DPI to reduce token usage
        img_path = output_dir / f"page_{i+1}.jpg"
        
        # Convert via PIL to apply JPEG compression
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))
        
        # Resize if still too large (max 1024px on longest side)
        max_dim = 1024
        if max(img.size) > max_dim:
            img.thumbnail((max_dim, max_dim), Image.LANCZOS)
        
        img.convert("RGB").save(str(img_path), "JPEG", quality=70, optimize=True)
        images.append(str(img_path))
    
    doc.close()
    return images
