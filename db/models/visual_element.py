"""VisualElement model — individual elements detected in a frame."""
import uuid
from sqlalchemy import Column, Text, Float, String, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from db.base import Base


class VisualElement(Base):
    __tablename__ = "visual_elements"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    frame_id = Column(PGUUID(as_uuid=True), ForeignKey("frames.id", ondelete="CASCADE"), nullable=False, index=True)
    element_type = Column(String(64))     # "equation" | "diagram" | "text" | "graph"
    bbox = Column(JSONB)                  # {x, y, w, h}
    extracted_text = Column(Text)
    semantic_description = Column(Text)
    confidence = Column(Float)
    extra = Column(JSONB)
