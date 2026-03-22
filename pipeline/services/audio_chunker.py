"""AudioChunker service — splits audio into N equal-length chunks for parallel transcription.

Uses ffmpeg (-f segment -c copy) instead of pydub for dramatically faster splitting:
- pydub: decode entire MP3 → PCM → re-encode each chunk → ~60s for 2hr file
- ffmpeg copy: no decode/recode → ~2-3s for any file length

Returns a list of (chunk_path, start_seconds, end_seconds) tuples.
"""
import os
import subprocess
import json
from pathlib import Path
from typing import List, Tuple


def _get_audio_duration_seconds(audio_path: Path) -> float:
    """Get audio duration via ffprobe (fast metadata-only read)."""
    result = subprocess.run(
        [
            "ffprobe", "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            str(audio_path),
        ],
        capture_output=True,
        text=True,
    )
    data = json.loads(result.stdout)
    return float(data["format"]["duration"])


def split_audio_into_chunks(
    audio_path: Path,
    n_chunks: int = 12,
) -> List[Tuple[Path, float, float]]:
    """
    Split an MP3 audio file into N equal chunks using ffmpeg's segment muxer.
    Uses stream copy (-c copy) so no audio decode/recode occurs — very fast.

    Returns list of (chunk_path, start_seconds, end_seconds).
    """
    chunks_dir = audio_path.parent / "chunks"
    chunks_dir.mkdir(parents=True, exist_ok=True)

    # Get total duration first
    total_seconds = _get_audio_duration_seconds(audio_path)
    segment_duration = total_seconds / n_chunks

    # Use ffmpeg segment muxer to split without re-encoding
    chunk_pattern = str(chunks_dir / "chunk_%03d.mp3")
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", str(audio_path),
            "-f", "segment",
            "-segment_time", f"{segment_duration:.2f}",
            "-c", "copy",
            "-reset_timestamps", "1",
            chunk_pattern,
        ],
        capture_output=True,
        check=True,
    )

    # Collect the chunks ffmpeg created and compute their time ranges
    chunk_files = sorted(chunks_dir.glob("chunk_*.mp3"))
    results: List[Tuple[Path, float, float]] = []

    for i, chunk_file in enumerate(chunk_files):
        start_sec = i * segment_duration
        end_sec = min((i + 1) * segment_duration, total_seconds)
        results.append((chunk_file, start_sec, end_sec))

    return results
