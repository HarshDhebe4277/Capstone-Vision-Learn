"""ModelResource model — registry of AI models used in the pipeline."""
import uuid
from sqlalchemy import Column, String, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from db.base import Base


class ModelResource(Base):
    __tablename__ = "model_resources"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(256))     # e.g. "voxtral-mini-latest"
    type = Column(String(64))      # "transcription" | "vision" | "text" | "tts"
    version = Column(String(64))
    config = Column(JSONB)
    created_at = Column(TIMESTAMP(timezone=True), server_default="now()")
