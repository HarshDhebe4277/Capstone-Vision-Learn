"""AudioRepository — DB operations for generated audio lecture files."""
from typing import Optional
from sqlalchemy.orm import Session
from db.models.audio_lecture import AudioLecture


class AudioRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_lecture(self, lecture_id: str) -> Optional[AudioLecture]:
        return (
            self.db.query(AudioLecture)
            .filter(AudioLecture.lecture_id == lecture_id)
            .order_by(AudioLecture.created_at.desc())
            .first()
        )

    def save(self, lecture_id: str, audio_path: str, voice: str, script_id: str = None) -> AudioLecture:
        audio = AudioLecture(
            lecture_id=lecture_id,
            script_id=script_id,
            tts_voice=voice,
            audio_path=audio_path,
        )
        self.db.add(audio)
        self.db.commit()
        self.db.refresh(audio)
        return audio
