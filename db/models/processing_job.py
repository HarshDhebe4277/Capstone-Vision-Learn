"""ProcessingJob model — tracks pipeline run status."""
import uuid
from sqlalchemy import Column, String, Integer, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from db.base import Base


class ProcessingJob(Base):
    __tablename__ = "processing_jobs"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lecture_id = Column(PGUUID(as_uuid=True), ForeignKey("lectures.id", ondelete="CASCADE"), nullable=False, index=True)
    job_type = Column(String(64))     # "full_pipeline" | "transcription" | "tts" ...
    status = Column(String(32), index=True)   # pending | running | done | failed
    started_at = Column(TIMESTAMP(timezone=True))
    finished_at = Column(TIMESTAMP(timezone=True))
    attempts = Column(Integer, default=0)
    result = Column(JSONB)
    worker_info = Column(JSONB)
