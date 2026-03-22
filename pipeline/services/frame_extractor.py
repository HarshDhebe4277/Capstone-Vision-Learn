"""FrameExtractor service — parallel ffmpeg frame extraction from CDN stream URL.

Uses run_in_executor + subprocess.run for Windows compatibility
(avoids asyncio.create_subprocess_exec which requires ProactorEventLoop on Windows).
"""
import asyncio
import subprocess
import os
from pathlib import Path
from typing import Any, Dict, List

MAX_CONCURRENT_EXTRACTIONS: int = int(os.getenv("MAX_FRAME_WORKERS", "8"))


def _extract_frame_sync(
    stream_url: str,
    timestamp_seconds: float,
    out_path: Path,
) -> bool:
    """
    Extract one JPEG frame at timestamp_seconds from a remote stream URL using ffmpeg.
    Uses HTTP range-request seeking — downloads only ~100KB per frame.
    Runs synchronously (called inside a thread executor).
    """
    result = subprocess.run(
        [
            "ffmpeg", "-y",
            "-ss", f"{timestamp_seconds:.3f}",  # fast seek before input
            "-i", stream_url,
            "-frames:v", "1",
            "-q:v", "2",                        # JPEG quality 2 = near-lossless
            "-vf", "scale=1280:-1",
            str(out_path),
        ],
        capture_output=True,
    )
    return result.returncode == 0 and out_path.exists()


async def extract_frames_parallel(
    stream_url: str,
    segments: List[Dict[str, Any]],
    frames_dir: Path,
) -> List[Dict[str, Any]]:
    """
    For each segment [{start, end, reason}], extract one frame at the midpoint.
    All extractions run concurrently (bounded by MAX_CONCURRENT_EXTRACTIONS).

    Returns list of {timestamp, path, reason, segment_start, segment_end}.
    """
    frames_dir.mkdir(parents=True, exist_ok=True)
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_EXTRACTIONS)
    loop = asyncio.get_event_loop()

    async def _extract(index: int, seg: Dict[str, Any]) -> Dict[str, Any] | None:
        midpoint = (seg["start"] + seg["end"]) / 2.0
        out_path = frames_dir / f"frame_{index:03d}_{int(midpoint):05d}s.jpg"

        async with semaphore:
            success = await loop.run_in_executor(
                None,
                _extract_frame_sync,
                stream_url,
                midpoint,
                out_path,
            )

        if not success:
            return None

        return {
            "timestamp": midpoint,
            "path": str(out_path),
            "reason": seg.get("reason", ""),
            "segment_start": seg["start"],
            "segment_end": seg["end"],
        }

    tasks = [_extract(i, seg) for i, seg in enumerate(segments)]
    results = await asyncio.gather(*tasks)
    return [r for r in results if r is not None]
