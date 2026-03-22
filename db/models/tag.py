"""Tag model."""
import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from db.base import Base
from db.models.associations import lecture_tags


class Tag(Base):
    __tablename__ = "tags"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(128), unique=True, nullable=False)

    lectures = relationship("Lecture", secondary=lecture_tags, back_populates="tags")
