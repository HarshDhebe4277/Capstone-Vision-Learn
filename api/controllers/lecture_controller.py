"""LectureController — CRUD endpoints for lecture management."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.session import get_db
from db.repositories.lecture_repository import LectureRepository
from api.schemas.lecture_schema import LectureCreate, LectureResponse

router = APIRouter(prefix="/api/lectures", tags=["Lectures"])


@router.get("/", response_model=List[LectureResponse], summary="List all lectures")
def list_lectures(db: Session = Depends(get_db)):
    return LectureRepository(db).get_all()


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
