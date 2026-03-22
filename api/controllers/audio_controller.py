"""AudioController — endpoints to stream narration audio and retrieve scripts."""
import os
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(prefix="/api/audio", tags=["Audio"])

STORAGE = Path(os.getenv("STORAGE_PATH", "./storage")).resolve()


@router.get("/{video_id}/narration", summary="Stream the narration MP3")
def stream_narration(video_id: str):
    """Download or stream the Edge TTS narration audio for a processed lecture."""
    audio_path = STORAGE / video_id / "narration.mp3"
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Narration not found. Run /api/pipeline/process first.")
    return FileResponse(str(audio_path), media_type="audio/mpeg", filename=f"{video_id}_narration.mp3")


@router.get("/{video_id}/script", summary="Get the narration script text")
def get_narration_script(video_id: str):
    """Return the pedagogical narration script as plain text."""
    script_path = STORAGE / video_id / "script.txt"
    if not script_path.exists():
        raise HTTPException(status_code=404, detail="Script not found. Run /api/pipeline/process first.")
    return {"video_id": video_id, "script": script_path.read_text(encoding="utf-8")}


@router.get("/{video_id}/transcript", summary="Get the timestamped transcript")
def get_transcript(video_id: str):
    """Return the Voxtral transcript JSON with all timestamped segments."""
    import json
    transcript_path = STORAGE / video_id / "transcript" / "transcript.json"
    if not transcript_path.exists():
        raise HTTPException(status_code=404, detail="Transcript not found.")
    return json.loads(transcript_path.read_text(encoding="utf-8"))
