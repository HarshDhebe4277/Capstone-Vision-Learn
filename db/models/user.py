"""User model."""
import uuid
from sqlalchemy import Column, String, Boolean, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255))
    role = Column(String(32), default="uploader")
    password_hash = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default="now()")
