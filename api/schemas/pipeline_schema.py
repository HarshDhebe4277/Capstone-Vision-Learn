"""Pydantic schemas for the pipeline trigger and status endpoints."""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class PipelineRunRequest(BaseModel):
    youtube_url: str
    lecture_id: Optional[str] = None    # link pipeline output to an existing Lecture row


class LocalPathRequest(BaseModel):
    file_path: str                      # absolute or relative path to a local video/audio file
    lecture_id: Optional[str] = None



class FrameInfo(BaseModel):
    timestamp: float
    path: str
    reason: str


class PipelineRunResponse(BaseModel):
    video_id: str
    audio: str
    transcript: str
    script: str
    narration: str
    frame_count: int
    status: str = "completed"
