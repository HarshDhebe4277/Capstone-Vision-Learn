"""LectureRepository — all DB operations for the Lecture entity."""
import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from db.models.lecture import Lecture


class LectureRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Lecture]:
        return self.db.query(Lecture).order_by(Lecture.created_at.desc()).all()

    def get_by_id(self, lecture_id: str) -> Optional[Lecture]:
        return self.db.query(Lecture).filter(Lecture.id == lecture_id).first()

    def get_by_source_url(self, url: str) -> Optional[Lecture]:
        return self.db.query(Lecture).filter(Lecture.source_url == url).first()

    def create(self, data: dict) -> Lecture:
        lecture = Lecture(**data)
        self.db.add(lecture)
        self.db.commit()
        self.db.refresh(lecture)
        return lecture

    def update_status(self, lecture_id: str, status: str) -> Optional[Lecture]:
        lecture = self.get_by_id(lecture_id)
        if lecture:
            lecture.status = status
            self.db.commit()
            self.db.refresh(lecture)
        return lecture

    def delete(self, lecture_id: str) -> bool:
        lecture = self.get_by_id(lecture_id)
        if lecture:
            self.db.delete(lecture)
            self.db.commit()
            return True
        return False
