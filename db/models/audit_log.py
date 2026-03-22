"""AuditLog model — system-level event tracking."""
import uuid
from sqlalchemy import Column, Text, String, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from db.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actor_id = Column(PGUUID(as_uuid=True))    # user who triggered the action
    action = Column(String(256))               # e.g. "pipeline.started"
    details = Column(JSONB)
    created_at = Column(TIMESTAMP(timezone=True), server_default="now()")
