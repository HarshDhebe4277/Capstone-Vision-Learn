"""MediaFile model — stores paths to video/audio files."""
import uuid
from sqlalchemy import Column, String, Text, Integer, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from db.base import Base


class MediaFile(Base):
    __tablename__ = "media_files"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lecture_id = Column(PGUUID(as_uuid=True), ForeignKey("lectures.id", ondelete="CASCADE"), nullable=False, index=True)
    file_type = Column(String(32))    # "video" | "audio"
    storage_path = Column(Text)
    checksum = Column(String(128))
    size_bytes = Column(Integer)
    created_at = Column(TIMESTAMP(timezone=True), server_default="now()")
