"""LocalFileProcessor — handles local video/audio files instead of YouTube URLs.

Supports:
  - Local video files (mp4, mkv, avi, mov, webm): extracts audio + uses file path for frames
  - Local audio files (mp3, wav, m4a, aac): transcription only, no frame extraction
  - Uploaded files saved temporarily to storage/uploads/

Unlike the YouTube flow, there is no yt-dlp involved — all processing via ffmpeg.
"""
import hashlib
import mimetypes
import os
import subprocess
from pathlib import Path

STORAGE: Path = Path(os.getenv("STORAGE_PATH", "./storage")).resolve()

VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".flv", ".ts"}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac"}


def classify_file(file_path: Path) -> str:
    """Return 'video', 'audio', or raise ValueError."""
    ext = file_path.suffix.lower()
    if ext in VIDEO_EXTENSIONS:
        return "video"
    if ext in AUDIO_EXTENSIONS:
        return "audio"
    raise ValueError(
        f"Unsupported file type: {ext}. "
        f"Supported video: {VIDEO_EXTENSIONS}, audio: {AUDIO_EXTENSIONS}"
    )


def make_file_id(file_path: Path) -> str:
    """Generate a stable ID from the file path (first 12 chars of MD5)."""
    return hashlib.md5(str(file_path).encode()).hexdigest()[:12]


def extract_audio_from_video(video_path: Path, out_dir: Path) -> Path:
    """
    Extract audio from a local video file using ffmpeg.
    Much faster than real-time: ffmpeg processes a 2hr video in ~30s.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    audio_path = out_dir / "audio.mp3"

    if audio_path.exists():
        return audio_path

    result = subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-vn",                      # no video
            "-acodec", "libmp3lame",
            "-ar", "44100",
            "-ab", "128k",
            str(audio_path),
        ],
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"ffmpeg audio extraction failed: {result.stderr.decode()[:500]}"
        )
    return audio_path


def save_upload(file_bytes: bytes, filename: str) -> Path:
    """Save an uploaded file to the storage/uploads directory and return the path."""
    upload_dir = STORAGE / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    dest = upload_dir / filename
    dest.write_bytes(file_bytes)
    return dest
