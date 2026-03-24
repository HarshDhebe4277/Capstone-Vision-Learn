"""LectureController — CRUD endpoints for lecture management."""
import os
from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.session import get_db
from db.repositories.lecture_repository import LectureRepository
from api.schemas.lecture_schema import LectureCreate, LectureResponse

router = APIRouter(prefix="/api/lectures", tags=["Lectures"])

STORAGE_DIR = Path(os.getenv("STORAGE_PATH", "./storage")).resolve()


@router.get("/", summary="List all lectures (Scanning Storage Folder)")
def list_lectures():
    lectures = []

    if not STORAGE_DIR.exists():
        return lectures
    
    # Loop through every folder inside /storage
    for folder in STORAGE_DIR.iterdir():
        # Ignore the temp folder and make sure it's an actual directory
        if folder.is_dir() and folder.name != "temp_notes":
            # Check if it actually finished processing (has an mp3)
            audio_file = folder / "narration.mp3"
            script_file = folder / "script.txt"
            
            if audio_file.exists():
                # Figure out a title (use the script's first few words if it exists)
                title = f"Lecture {folder.name[:6]}"
                if script_file.exists():
                    try:
                        first_line = script_file.read_text(encoding="utf-8").strip().split('.')[0]
                        title = first_line[:40] + "..." if len(first_line) > 40 else first_line
                    except:
                        pass

                # Build a fake database object for the frontend
                lectures.append({
                    "id": folder.name,
                    "title": title,
                    "source_type": "YouTube / Local",
                    "status": "Ready",
                })
                
    return lectures

# def list_lectures(db: Session = Depends(get_db)):
#     return LectureRepository(db).get_all()


@router.get("/{lecture_id}", response_model=LectureResponse, summary="Get a single lecture by ID")
def get_lecture(lecture_id: str, db: Session = Depends(get_db)):
    lecture = LectureRepository(db).get_by_id(lecture_id)
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")
    return lecture


@router.delete("/{lecture_id}", summary="Delete a lecture and all its data")
def delete_lecture(lecture_id: str, db: Session = Depends(get_db)):
    deleted = LectureRepository(db).delete(lecture_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Lecture not found")
    return {"message": "Lecture deleted"}
