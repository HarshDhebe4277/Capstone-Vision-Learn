"""Transcript model — Voxtral output with timestamped segments."""
import uuid
from sqlalchemy import Column, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from db.base import Base


class Transcript(Base):
    __tablename__ = "transcripts"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lecture_id = Column(PGUUID(as_uuid=True), ForeignKey("lectures.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text)        # full plain-text transcript
    segments = Column(JSONB)      # [{start, end, text}, ...]
    model_info = Column(JSONB)    # which model version was used
    created_at = Column(TIMESTAMP(timezone=True), server_default="now()")
