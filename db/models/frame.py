"""Frame model — key frames extracted from the lecture video."""
import uuid
from sqlalchemy import Column, Text, Float, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import relationship
from db.base import Base


class Frame(Base):
    __tablename__ = "frames"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lecture_id = Column(PGUUID(as_uuid=True), ForeignKey("lectures.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp_seconds = Column(Float)
    image_path = Column(Text)
    ocr_text = Column(Text)       # raw text found in frame (if any)
    features = Column(JSONB)      # reason, segment info, etc.
    created_at = Column(TIMESTAMP(timezone=True), server_default="now()")

    visual_elements = relationship("VisualElement", cascade="all, delete-orphan", backref="frame")
