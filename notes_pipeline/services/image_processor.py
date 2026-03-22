from PIL import Image
from pathlib import Path

def process_single_image(image_path: str, output_dir: Path) -> list:
    """Copy and normalize a single image for the pipeline."""
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "page_1.jpg"
    
    with Image.open(image_path) as img:
        img = img.convert('RGB')
        img.save(str(out_path), "JPEG", quality=85)
        
    return [str(out_path)]
