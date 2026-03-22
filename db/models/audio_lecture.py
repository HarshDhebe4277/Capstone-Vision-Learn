"""AudioLecture model — Edge TTS output audio files."""
import uuid
from sqlalchemy import Column, String, Text, Float, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from db.base import Base


class AudioLecture(Base):
    __tablename__ = "audio_lectures"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lecture_id = Column(PGUUID(as_uuid=True), ForeignKey("lectures.id", ondelete="CASCADE"), nullable=False, index=True)
    script_id = Column(PGUUID(as_uuid=True), ForeignKey("pedagogical_scripts.id", ondelete="SET NULL"))
    tts_voice = Column(String(128))       # e.g. "en-US-GuyNeural"
    audio_path = Column(Text)            # local storage path to .mp3
    duration_seconds = Column(Float)
    created_at = Column(TIMESTAMP(timezone=True), server_default="now()")
