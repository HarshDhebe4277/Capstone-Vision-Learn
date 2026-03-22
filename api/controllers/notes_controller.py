import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
from notes_pipeline.notes_orchestrator import run_notes_pipeline

router = APIRouter(prefix="/api/notes", tags=["Notes"])

TEMP_DIR = Path("./storage/temp_notes")
TEMP_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/process")
async def upload_and_process_notes(file: UploadFile = File(...)):
    """Upload a PDF or Image note to process into an audio narration."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
        
    ext = Path(file.filename).suffix.lower()
    if ext not in [".pdf", ".jpg", ".jpeg", ".png"]:
        raise HTTPException(status_code=400, detail="Only PDF, JPG, and PNG files are supported")
        
    temp_path = TEMP_DIR / file.filename
    with temp_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        # Run pipeline
        result = await run_notes_pipeline(str(temp_path))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Notes processing failed: {str(e)}")
    finally:
        # Cleanup temp file
        if temp_path.exists():
            temp_path.unlink()
