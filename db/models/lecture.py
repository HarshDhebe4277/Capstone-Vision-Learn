"""Lecture model — core entity of the platform."""
import uuid
from sqlalchemy import Column, String, Text, Integer, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import relationship
from db.base import Base
from db.models.associations import lecture_tags


class Lecture(Base):
    __tablename__ = "lectures"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(512))
    description = Column(Text)
    source_type = Column(String(32))          # e.g. "youtube", "upload"
    source_url = Column(Text, index=True)
    uploaded_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    language = Column(String(16))
    duration_seconds = Column(Integer)
    status = Column(String(32), index=True)   # pending | processing | done | failed
    metadata_ = Column(JSONB)
    created_at = Column(TIMESTAMP(timezone=True), server_default="now()")

    # Relationships
    uploader = relationship("User", backref="lectures")
    media = relationship("MediaFile", cascade="all, delete-orphan", backref="lecture")
    transcripts = relationship("Transcript", cascade="all, delete-orphan", backref="lecture")
    frames = relationship("Frame", cascade="all, delete-orphan", backref="lecture")
    scripts = relationship("PedagogicalScript", cascade="all, delete-orphan", backref="lecture")
    audio_lectures = relationship("AudioLecture", cascade="all, delete-orphan", backref="lecture")
    tags = relationship("Tag", secondary=lecture_tags, back_populates="lectures")
