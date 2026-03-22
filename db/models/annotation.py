"""Annotation model — user notes linked to a lecture or frame."""
import uuid
from sqlalchemy import Column, Text, String, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from db.base import Base


class Annotation(Base):
    __tablename__ = "annotations"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lecture_id = Column(PGUUID(as_uuid=True), ForeignKey("lectures.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    target_type = Column(String(64))   # "frame" | "segment" | "script"
    target_id = Column(PGUUID(as_uuid=True))
    note = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default="now()")
