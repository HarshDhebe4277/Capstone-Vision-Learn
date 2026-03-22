import uuid
from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    TIMESTAMP,
    ForeignKey,
    Float,
    Table,
    Boolean,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


lecture_tags = Table(
    "lecture_tags",
    Base.metadata,
    Column("lecture_id", PGUUID(as_uuid=True), ForeignKey("lectures.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", PGUUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255))
    role = Column(String(32), default="uploader")
    password_hash = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default="now()")


class Lecture(Base):
    __tablename__ = "lectures"
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(512))
    description = Column(Text)
    source_type = Column(String(32))
    source_url = Column(Text, index=True)
    uploaded_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    language = Column(String(16))
    duration_seconds = Column(Integer)
    status = Column(String(32), index=True)
    metadata_ = Column(JSONB)
    created_at = Column(TIMESTAMP(timezone=True), server_default="now()")

    uploader = relationship("User", backref="lectures")
    media = relationship("MediaFile", cascade="all, delete-orphan", backref="lecture")
    transcripts = relationship("Transcript", cascade="all, delete-orphan", backref="lecture")
    frames = relationship("Frame", cascade="all, delete-orphan", backref="lecture")
    scripts = relationship("PedagogicalScript", cascade="all, delete-orphan", backref="lecture")
    audio_lectures = relationship("AudioLecture", cascade="all, delete-orphan", backref="lecture")
    tags = relationship("Tag", secondary=lecture_tags, back_populates="lectures")


class MediaFile(Base):
    __tablename__ = "media_files"
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lecture_id = Column(PGUUID(as_uuid=True), ForeignKey("lectures.id", ondelete="CASCADE"), nullable=False, index=True)
    file_type = Column(String(32))
    storage_path = Column(Text)
    checksum = Column(String(128))
    size_bytes = Column(Integer)
    created_at = Column(TIMESTAMP(timezone=True), server_default="now()")


class ProcessingJob(Base):
    __tablename__ = "processing_jobs"
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lecture_id = Column(PGUUID(as_uuid=True), ForeignKey("lectures.id", ondelete="CASCADE"), nullable=False, index=True)
    job_type = Column(String(64))
    status = Column(String(32), index=True)
    started_at = Column(TIMESTAMP(timezone=True))
    finished_at = Column(TIMESTAMP(timezone=True))
    attempts = Column(Integer, default=0)
    result = Column(JSONB)
    worker_info = Column(JSONB)


class Transcript(Base):
    __tablename__ = "transcripts"
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lecture_id = Column(PGUUID(as_uuid=True), ForeignKey("lectures.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text)
    segments = Column(JSONB)
    model_info = Column(JSONB)
    created_at = Column(TIMESTAMP(timezone=True), server_default="now()")


class Frame(Base):
    __tablename__ = "frames"
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lecture_id = Column(PGUUID(as_uuid=True), ForeignKey("lectures.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp_seconds = Column(Float)
    image_path = Column(Text)
    ocr_text = Column(Text)
    features = Column(JSONB)
    created_at = Column(TIMESTAMP(timezone=True), server_default="now()")

    visual_elements = relationship("VisualElement", cascade="all, delete-orphan", backref="frame")


class VisualElement(Base):
    __tablename__ = "visual_elements"
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    frame_id = Column(PGUUID(as_uuid=True), ForeignKey("frames.id", ondelete="CASCADE"), nullable=False, index=True)
    element_type = Column(String(64))
    bbox = Column(JSONB)
    extracted_text = Column(Text)
    semantic_description = Column(Text)
    confidence = Column(Float)
    extra = Column(JSONB)


class PedagogicalScript(Base):
    __tablename__ = "pedagogical_scripts"
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lecture_id = Column(PGUUID(as_uuid=True), ForeignKey("lectures.id", ondelete="CASCADE"), nullable=False, index=True)
    version = Column(Integer, default=1)
    content = Column(Text)
    sections = Column(JSONB)
    generated_by = Column(JSONB)
    created_at = Column(TIMESTAMP(timezone=True), server_default="now()")


class AudioLecture(Base):
    __tablename__ = "audio_lectures"
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lecture_id = Column(PGUUID(as_uuid=True), ForeignKey("lectures.id", ondelete="CASCADE"), nullable=False, index=True)
    script_id = Column(PGUUID(as_uuid=True), ForeignKey("pedagogical_scripts.id", ondelete="SET NULL"))
    tts_voice = Column(String(128))
    audio_path = Column(Text)
    duration_seconds = Column(Float)
    created_at = Column(TIMESTAMP(timezone=True), server_default="now()")


class Tag(Base):
    __tablename__ = "tags"
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(128), unique=True, nullable=False)
    lectures = relationship("Lecture", secondary=lecture_tags, back_populates="tags")


class ModelResource(Base):
    __tablename__ = "model_resources"
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(256))
    type = Column(String(64))
    version = Column(String(64))
    config = Column(JSONB)
    created_at = Column(TIMESTAMP(timezone=True), server_default="now()")


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actor_id = Column(PGUUID(as_uuid=True))
    action = Column(String(256))
    details = Column(JSONB)
    created_at = Column(TIMESTAMP(timezone=True), server_default="now()")


class Annotation(Base):
    __tablename__ = "annotations"
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lecture_id = Column(PGUUID(as_uuid=True), ForeignKey("lectures.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    target_type = Column(String(64))
    target_id = Column(PGUUID(as_uuid=True))
    note = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default="now()")
