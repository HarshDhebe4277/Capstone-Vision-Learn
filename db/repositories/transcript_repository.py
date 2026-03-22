"""TranscriptRepository — DB operations for transcripts."""
from typing import Optional
from sqlalchemy.orm import Session
from db.models.transcript import Transcript


class TranscriptRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_lecture(self, lecture_id: str) -> Optional[Transcript]:
        return self.db.query(Transcript).filter(Transcript.lecture_id == lecture_id).first()

    def save(self, lecture_id: str, content: str, segments: list, model_info: dict) -> Transcript:
        # Remove old transcript for this lecture (one per lecture for now)
        existing = self.get_by_lecture(lecture_id)
        if existing:
            self.db.delete(existing)
            self.db.commit()

        transcript = Transcript(
            lecture_id=lecture_id,
            content=content,
            segments=segments,
            model_info=model_info,
        )
        self.db.add(transcript)
        self.db.commit()
        self.db.refresh(transcript)
        return transcript
