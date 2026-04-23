"""VideoDownloader service — yt-dlp wrapper for audio-only download and stream URL fetch.

Uses asyncio.get_event_loop().run_in_executor() rather than asyncio.create_subprocess_exec
so it works on BOTH Windows SelectorEventLoop (uvicorn default) and ProactorEventLoop.
"""
import asyncio
import os
import shutil
import subprocess
import sys
from pathlib import Path


def _get_ytdlp_path() -> str:
    """Locate the yt-dlp binary — checks PATH first, then the current venv's Scripts folder."""
    path = shutil.which("yt-dlp")
    if path:
        return path
    sibling = Path(sys.executable).parent / "yt-dlp.exe"
    if sibling.exists():
        return str(sibling)
    return "yt-dlp"


def _run_subprocess(cmd: list) -> subprocess.CompletedProcess:
    """Run a subprocess synchronously (called inside a thread executor)."""
    return subprocess.run(cmd, capture_output=True, text=True)


async def get_stream_url(youtube_url: str) -> str:
    """
    Fetch the direct CDN video stream URL via yt-dlp (no download).
    Runs in a thread executor so it is compatible with any asyncio event loop.
    """
    ytdlp = _get_ytdlp_path()
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,
        _run_subprocess,
        [ytdlp, "--get-url", "-f", "bestvideo[ext=mp4]/bestvideo", youtube_url],
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"yt-dlp get-url failed (code {result.returncode}): {result.stderr[:500]}"
        )
    url = result.stdout.strip().split("\n")[0]
    if not url:
        raise RuntimeError("yt-dlp returned empty stream URL")
    return url


async def download_audio(youtube_url: str, out_path: Path) -> Path:
    """
    Download only the audio track as MP3.
    Runs in a thread executor so it is compatible with any asyncio event loop.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    ytdlp = _get_ytdlp_path()
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,
        _run_subprocess,
        [
            ytdlp,
            "-f", "bestaudio",
            "-x", "--audio-format", "mp3",
            "--audio-quality", "5",
            "--no-playlist",
            "-o", str(out_path),
            youtube_url,
        ],
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Audio download failed (code {result.returncode}): {result.stderr[:500]}"
        )
    if not out_path.exists():
        candidates = list(out_path.parent.glob("audio.*"))
        if candidates:
            return candidates[0]
        raise FileNotFoundError(f"Audio file not found after download: {out_path}")
    return out_path


async def download_video(youtube_url: str, out_path: Path) -> Path:
    """
    Download the best quality video file (MP4 format).
    Runs in a thread executor so it is compatible with any asyncio event loop.
    
    Returns the path to the downloaded video file.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    ytdlp = _get_ytdlp_path()
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,
        _run_subprocess,
        [
            ytdlp,
            "-f", "bestvideo[ext=mp4]",
            "--no-playlist",
            "-o", str(out_path),
            youtube_url,
        ],
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Video download failed (code {result.returncode}): {result.stderr[:500]}"
        )
    if not out_path.exists():
        candidates = list(out_path.parent.glob("video.*"))
        if candidates:
            return candidates[0]
        raise FileNotFoundError(f"Video file not found after download: {out_path}")
    return out_path


async def get_video_id(youtube_url: str) -> str:
    """Extract the YouTube video ID from a URL."""
    ytdlp = _get_ytdlp_path()
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,
        _run_subprocess,
        [ytdlp, "--get-id", youtube_url],
    )
    return result.stdout.strip()
