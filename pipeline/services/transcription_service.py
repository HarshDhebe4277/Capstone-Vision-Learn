"""TranscriptionService — parallel Voxtral transcription via official mistralai SDK."""
import asyncio
import os
from pathlib import Path
from typing import Any, Dict, List, Tuple

from mistralai.client import Mistral

MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "")
TRANSCRIPTION_MODEL: str = os.getenv("MISTRAL_TRANSCRIPTION_MODEL", "voxtral-mini-latest")


async def _transcribe_single_chunk(
    client: Mistral,
    chunk_path: Path,
    start_offset_seconds: float,
) -> List[Dict[str, Any]]:
    """
    Transcribe one audio chunk and offset every segment timestamp
    by start_offset_seconds to reconstruct global timing.
    Runs the blocking SDK call in a thread executor so it doesn't block the event loop.
    """
    loop = asyncio.get_event_loop()

    def _call_api() -> Any:
        with open(chunk_path, "rb") as f:
            audio_bytes = f.read()
        return client.audio.transcriptions.complete(
            model=TRANSCRIPTION_MODEL,
            file={"content": audio_bytes, "file_name": chunk_path.name},
            timestamp_granularities=["segment"],
            language=os.getenv("WHISPER_LANGUAGE", "en"),
        )

    response = await loop.run_in_executor(None, _call_api)

    segments: List[Dict[str, Any]] = []
    for seg in response.segments or []:
        segments.append(
            {
                "start": round(seg.start + start_offset_seconds, 2),
                "end": round(seg.end + start_offset_seconds, 2),
                "text": seg.text.strip(),
            }
        )
    return segments


async def transcribe_audio_parallel(
    chunks: List[Tuple[Path, float, float]],
) -> Dict[str, Any]:
    """
    Transcribe all audio chunks in parallel and merge into a single transcript.

    Args:
        chunks: list of (chunk_path, start_sec, end_sec) from AudioChunker

    Returns a dict with:
      - segments:          [{start, end, text}, ...]  sorted by start
      - full_text:         complete transcript as one string
      - formatted_for_llm: "[MM:SS] text" per segment — fed to timestamp selector LLM
    """
    if not MISTRAL_API_KEY:
        raise RuntimeError("MISTRAL_API_KEY is not set in environment")

    client = Mistral(api_key=MISTRAL_API_KEY)

    # Fire all chunk transcriptions concurrently
    tasks = [
        _transcribe_single_chunk(client, chunk_path, start_sec)
        for chunk_path, start_sec, _ in chunks
    ]
    chunk_results: List[List[Dict]] = await asyncio.gather(*tasks)

    # Flatten and sort by start time
    all_segments: List[Dict[str, Any]] = []
    for segs in chunk_results:
        all_segments.extend(segs)
    all_segments.sort(key=lambda s: s["start"])

    full_text = " ".join(s["text"] for s in all_segments)

    formatted_for_llm = "\n".join(
        f"[{int(s['start']) // 60:02d}:{int(s['start']) % 60:02d}] {s['text']}"
        for s in all_segments
    )

    return {
        "segments": all_segments,
        "full_text": full_text,
        "formatted_for_llm": formatted_for_llm,
        "model": TRANSCRIPTION_MODEL,
    }
