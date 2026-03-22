"""Pydantic schemas for lecture endpoints."""
import uuid
from typing import Optional
from pydantic import BaseModel, HttpUrl


class LectureCreate(BaseModel):
    title: str
    description: Optional[str] = None
    source_url: str
    source_type: str = "youtube"
    language: str = "en"


class LectureResponse(BaseModel):
    id: uuid.UUID
    title: Optional[str]
    description: Optional[str]
    source_url: str
    source_type: Optional[str]
    status: Optional[str]
    duration_seconds: Optional[int]
    language: Optional[str]

    class Config:
        from_attributes = True
