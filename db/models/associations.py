"""Association / junction tables shared between models."""
from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from db.base import Base

# Many-to-many: lectures ↔ tags
lecture_tags = Table(
    "lecture_tags",
    Base.metadata,
    Column(
        "lecture_id",
        PGUUID(as_uuid=True),
        ForeignKey("lectures.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "tag_id",
        PGUUID(as_uuid=True),
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)
