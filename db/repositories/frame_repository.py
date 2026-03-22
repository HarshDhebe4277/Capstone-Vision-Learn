"""FrameRepository — DB operations for extracted lecture frames."""
from typing import List
from sqlalchemy.orm import Session
from db.models.frame import Frame


class FrameRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_lecture(self, lecture_id: str) -> List[Frame]:
        return (
            self.db.query(Frame)
            .filter(Frame.lecture_id == lecture_id)
            .order_by(Frame.timestamp_seconds)
            .all()
        )

    def bulk_save(self, lecture_id: str, frames: list) -> List[Frame]:
        """Save a list of frame dicts [{timestamp, path, reason, ...}]."""
        # Clear old frames for this lecture first
        self.db.query(Frame).filter(Frame.lecture_id == lecture_id).delete()
        self.db.commit()

        saved = []
        for f in frames:
            frame = Frame(
                lecture_id=lecture_id,
                timestamp_seconds=f["timestamp"],
                image_path=f["path"],
                features={"reason": f.get("reason"), "segment_start": f.get("segment_start"), "segment_end": f.get("segment_end")},
            )
            self.db.add(frame)
            saved.append(frame)

        self.db.commit()
        return saved
