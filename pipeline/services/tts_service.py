"""TTS service — Edge TTS text-to-speech synthesis with pause support.

[PAUSE] markers in the script are converted to real audio silence (0.8s)
by splitting the script into segments, synthesizing each, and stitching
them together with ffmpeg. The word "PAUSE" is never spoken.
"""
import asyncio
import os
import subprocess
import tempfile
import re
from pathlib import Path

import edge_tts

TTS_VOICE: str = os.getenv("EDGE_TTS_VOICE", "en-US-GuyNeural")
PAUSE_DURATION_MS: int = int(os.getenv("TTS_PAUSE_MS", "800"))   # silence between sections


def _clean_segment(text: str) -> str:
    """Remove any leftover bracket markers and strip whitespace."""
    # Remove [PAUSE], [pause], any remaining [ANYTHING] bracket markers
    text = re.sub(r'\[.*?\]', '', text)
    return text.strip()


async def _synthesize_segment(text: str, out_path: Path) -> None:
    """Synthesize one text segment to an MP3 file."""
    communicate = edge_tts.Communicate(
        text=text,
        voice=TTS_VOICE,
        rate="+0%",
        volume="+0%",
    )
    await communicate.save(str(out_path))


def _generate_silence(ms: int, out_path: Path) -> None:
    """Generate a silent MP3 of duration `ms` milliseconds using ffmpeg."""
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"anullsrc=r=24000:cl=mono",
            "-t", f"{ms / 1000:.3f}",
            "-acodec", "libmp3lame",
            "-ab", "128k",
            str(out_path),
        ],
        capture_output=True,
        check=True,
    )


def _concat_mp3s(parts: list[Path], out_path: Path) -> None:
    """Concatenate a list of MP3 files into one using ffmpeg concat demuxer."""
    list_file = out_path.parent / "concat_list.txt"
    list_file.write_text(
        "\n".join(f"file '{str(p).replace(chr(92), '/')}'" for p in parts),
        encoding="utf-8",
    )
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(list_file),
            "-c", "copy",
            str(out_path),
        ],
        capture_output=True,
        check=True,
    )
    list_file.unlink(missing_ok=True)


async def synthesize_narration(script_text: str, out_path: Path) -> Path:
    """
    Convert the pedagogical narration script to speech.

    [PAUSE] markers are replaced by 0.8s of real audio silence.
    All other bracket markers are stripped before TTS.
    Saves the final stitched MP3 at out_path.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Split on [PAUSE] (case-insensitive)
    raw_segments = re.split(r'\[PAUSE\]', script_text, flags=re.IGNORECASE)
    segments = [_clean_segment(s) for s in raw_segments]
    segments = [s for s in segments if s]   # drop empty segments

    if len(segments) == 1:
        # No PAUSE markers — simple single TTS call
        communicate = edge_tts.Communicate(
            text=segments[0], voice=TTS_VOICE, rate="+0%", volume="+0%"
        )
        await communicate.save(str(out_path))
        return out_path

    # Multiple segments — synthesize each and interleave with silence
    tmp_dir = out_path.parent / "_tts_tmp"
    tmp_dir.mkdir(exist_ok=True)

    parts: list[Path] = []
    silence_path = tmp_dir / "silence.mp3"
    _generate_silence(PAUSE_DURATION_MS, silence_path)

    # Synthesize all segments concurrently
    seg_paths = [tmp_dir / f"seg_{i:04d}.mp3" for i in range(len(segments))]
    await asyncio.gather(
        *[_synthesize_segment(text, path) for text, path in zip(segments, seg_paths)]
    )

    # Interleave audio segments with silence
    for i, seg_path in enumerate(seg_paths):
        if seg_path.exists():
            parts.append(seg_path)
            if i < len(seg_paths) - 1:
                parts.append(silence_path)

    _concat_mp3s(parts, out_path)

    # Cleanup temp files (keep silence.mp3 for reuse is fine, clean rest)
    for p in seg_paths:
        p.unlink(missing_ok=True)

    print(f"[TTS] {len(segments)} segments synthesized and stitched with {PAUSE_DURATION_MS}ms pauses")
    return out_path


async def list_available_voices() -> list:
    """List all available Edge TTS English voices (for configuration)."""
    voices = await edge_tts.list_voices()
    return [v for v in voices if v["Locale"].startswith("en-")]
