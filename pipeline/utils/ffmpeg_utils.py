"""ffmpeg utility helpers."""
import json
import shutil
import subprocess


def is_ffmpeg_available() -> bool:
    """Check if ffmpeg binary is available in PATH."""
    return shutil.which("ffmpeg") is not None


def assert_ffmpeg() -> None:
    """Raise RuntimeError if ffmpeg is not found."""
    if not is_ffmpeg_available():
        raise RuntimeError(
            "ffmpeg not found. Install from https://ffmpeg.org and ensure it is in your PATH."
        )


def get_audio_duration_seconds(audio_path: str) -> float:
    """Return the duration of an audio file in seconds using ffprobe."""
    result = subprocess.run(
        [
            "ffprobe", "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            audio_path,
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(result.stdout)
    return float(data["format"]["duration"])
