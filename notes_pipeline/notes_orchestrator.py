import asyncio
import os
from pathlib import Path
from typing import Dict, Any

from pipeline.services.tts_service import synthesize_narration
from notes_pipeline.services.pdf_processor import extract_images_from_pdf
from notes_pipeline.services.image_processor import process_single_image
from notes_pipeline.chains.notes_narration_chain import generate_notes_script
import uuid

STORAGE = Path(os.getenv("STORAGE_PATH", "./storage")).resolve()

async def run_notes_pipeline(file_path: str) -> Dict[str, Any]:
    """
    Run the pipeline to convert notes (PDF or Image) to an audio narration.
    """
    source_path = Path(file_path).resolve()
    if not source_path.exists():
        raise FileNotFoundError(f"File not found: {source_path}")
        
    note_id = f"note_{uuid.uuid4().hex[:8]}"
    workdir = STORAGE / note_id
    workdir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n[Notes Orchestrator] Starting pipeline for {source_path.name} (id={note_id})")
    
    # Step 1: Extract Images
    pages_dir = workdir / "pages"
    ext = source_path.suffix.lower()
    
    print("[Step 1] Extracting content into viewable images...")
    if ext == ".pdf":
        image_paths = extract_images_from_pdf(str(source_path), pages_dir)
    elif ext in [".png", ".jpg", ".jpeg"]:
        image_paths = process_single_image(str(source_path), pages_dir)
    else:
        raise ValueError(f"Unsupported file format: {ext}")
        
    print(f"[Step 1] Extracted {len(image_paths)} pages.")
    
    # Step 2: Generate Script with Vision LLM
    vision_model_name = os.getenv("MISTRAL_VISION_MODEL", "pixtral-12b-latest")
    print(f"[Step 2] Generating pedagogical script via {vision_model_name} for {len(image_paths)} pages...")
    script_path = workdir / "script.txt"
    script = await generate_notes_script(image_paths)
    script_path.write_text(script, encoding="utf-8")
    print(f"[Step 2] Script generated ({len(script)} chars)")
    
    # Step 3: Synthesis
    print("[Step 3] Synthesising script with Edge TTS...")
    narration_path = workdir / "narration.mp3"
    await synthesize_narration(script, narration_path)
    print(f"[Step 3] Narration saved at {narration_path}")
    
    result = {
        "note_id": note_id,
        "workdir": str(workdir),
        "pages": image_paths,
        "page_count": len(image_paths),
        "script": str(script_path),
        "narration": str(narration_path),
        "source": str(source_path),
    }
    
    print(f"\n[Notes Orchestrator] Pipeline complete! All artifacts in {workdir}\n")
    return result
