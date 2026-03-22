"""PedagogicalScript model — AI-generated teacher narration scripts."""
import uuid
from sqlalchemy import Column, Text, Integer, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from db.base import Base


class PedagogicalScript(Base):
    __tablename__ = "pedagogical_scripts"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lecture_id = Column(PGUUID(as_uuid=True), ForeignKey("lectures.id", ondelete="CASCADE"), nullable=False, index=True)
    version = Column(Integer, default=1)
    content = Column(Text)       # full narration script (plain text)
    sections = Column(JSONB)     # [{timestamp, text}, ...]
    generated_by = Column(JSONB) # model name, version, params
    created_at = Column(TIMESTAMP(timezone=True), server_default="now()")
