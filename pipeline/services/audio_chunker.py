"""AudioChunker service — splits audio into N equal-length chunks for parallel transcription.

Chunks are re-encoded to keep segment boundaries decodable by transcription APIs.
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


def _safe_duration_seconds(audio_path: Path) -> float:
    """Best-effort duration probe for a chunk; returns 0.0 on failure."""
    try:
        return _get_audio_duration_seconds(audio_path)
    except Exception:
        return 0.0


def split_audio_into_chunks(
    audio_path: Path,
    n_chunks: int = 12,
) -> List[Tuple[Path, float, float]]:
    """
    Split an MP3 audio file into N equal chunks using ffmpeg's segment muxer.
    Re-encodes output chunks to avoid undecodable boundary frames.

    Returns list of (chunk_path, start_seconds, end_seconds).
    """
    chunks_dir = audio_path.parent / "chunks"
    chunks_dir.mkdir(parents=True, exist_ok=True)

    # Remove stale chunks from previous runs so we don't transcribe old files.
    for old_chunk in chunks_dir.glob("chunk_*.mp3"):
        old_chunk.unlink(missing_ok=True)

    # Get total duration first
    total_seconds = _get_audio_duration_seconds(audio_path)
    segment_duration = total_seconds / n_chunks

    # Use ffmpeg segment muxer and re-encode chunks for robust decoding.
    chunk_pattern = str(chunks_dir / "chunk_%03d.mp3")
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", str(audio_path),
            "-f", "segment",
            "-segment_time", f"{segment_duration:.2f}",
            "-acodec", "libmp3lame",
            "-ar", "44100",
            "-ab", "128k",
            "-reset_timestamps", "1",
            chunk_pattern,
        ],
        capture_output=True,
        check=True,
    )

    # Collect the chunks ffmpeg created and compute their time ranges
    chunk_files = sorted(chunks_dir.glob("chunk_*.mp3"))

    # ffmpeg segmenter may produce an extra tiny tail chunk due timestamp rounding.
    # Keep at most the requested number of chunks.
    if len(chunk_files) > n_chunks:
        for extra_chunk in chunk_files[n_chunks:]:
            extra_chunk.unlink(missing_ok=True)
        chunk_files = chunk_files[:n_chunks]

    results: List[Tuple[Path, float, float]] = []

    for i, chunk_file in enumerate(chunk_files):
        duration = _safe_duration_seconds(chunk_file)
        if duration < 0.25:
            # Skip tiny/corrupt chunks that transcription APIs frequently reject.
            chunk_file.unlink(missing_ok=True)
            continue
        start_sec = i * segment_duration
        end_sec = min((i + 1) * segment_duration, total_seconds)
        results.append((chunk_file, start_sec, end_sec))

    return results
