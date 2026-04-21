"""TranscriptionService — parallel Voxtral transcription via official mistralai SDK."""
import asyncio
import os
from pathlib import Path
from typing import Any, Dict, List, Tuple

from mistralai.client import Mistral

MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "")
TRANSCRIPTION_MODEL: str = os.getenv("MISTRAL_TRANSCRIPTION_MODEL", "voxtral-mini-latest")
TRANSCRIPTION_MAX_RETRIES: int = int(os.getenv("TRANSCRIPTION_MAX_RETRIES", "3"))
TRANSCRIPTION_RETRY_BACKOFF_SECONDS: float = float(
    os.getenv("TRANSCRIPTION_RETRY_BACKOFF_SECONDS", "1.5")
)
TRANSCRIPTION_PARALLEL_LIMIT: int = int(os.getenv("TRANSCRIPTION_PARALLEL_LIMIT", "4"))


async def _transcribe_single_chunk(
    client: Mistral,
    chunk_path: Path,
    start_offset_seconds: float,
    semaphore: asyncio.Semaphore,
) -> List[Dict[str, Any]]:
    """
    Transcribe one audio chunk and offset every segment timestamp
    by start_offset_seconds to reconstruct global timing.
    Runs the blocking SDK call in a thread executor so it doesn't block the event loop.
    """
    loop = asyncio.get_running_loop()

    def _call_api() -> Any:
        with open(chunk_path, "rb") as f:
            audio_bytes = f.read()
        return client.audio.transcriptions.complete(
            model=TRANSCRIPTION_MODEL,
            file={"content": audio_bytes, "file_name": chunk_path.name},
            timestamp_granularities=["segment"],
            language=os.getenv("WHISPER_LANGUAGE", "en"),
        )

    async with semaphore:
        last_exc: Exception | None = None

        for attempt in range(1, TRANSCRIPTION_MAX_RETRIES + 1):
            try:
                response = await loop.run_in_executor(None, _call_api)
                break
            except Exception as exc:
                last_exc = exc
                if attempt == TRANSCRIPTION_MAX_RETRIES:
                    raise RuntimeError(
                        f"Transcription failed for chunk '{chunk_path.name}' after {TRANSCRIPTION_MAX_RETRIES} attempts"
                    ) from exc
                backoff = TRANSCRIPTION_RETRY_BACKOFF_SECONDS * (2 ** (attempt - 1))
                print(
                    f"[Transcription] Attempt {attempt}/{TRANSCRIPTION_MAX_RETRIES} failed for {chunk_path.name}: {type(exc).__name__}: {exc}. Retrying in {backoff:.1f}s..."
                )
                await asyncio.sleep(backoff)

        if last_exc and 'response' not in locals():
            raise RuntimeError(
                f"Transcription failed for chunk '{chunk_path.name}'"
            ) from last_exc

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
    semaphore = asyncio.Semaphore(max(1, TRANSCRIPTION_PARALLEL_LIMIT))

    # Fire chunk transcriptions concurrently with a bounded parallelism limit.
    tasks = [
        _transcribe_single_chunk(client, chunk_path, start_sec, semaphore)
        for chunk_path, start_sec, _ in chunks
    ]
    gathered_results = await asyncio.gather(*tasks, return_exceptions=True)

    chunk_results: List[List[Dict[str, Any]]] = []
    failed_count = 0
    for idx, item in enumerate(gathered_results):
        if isinstance(item, Exception):
            failed_count += 1
            chunk_name = chunks[idx][0].name
            print(
                f"[Transcription] Chunk failed: {chunk_name} -> {type(item).__name__}: {item}"
            )
            continue
        chunk_results.append(item)

    if not chunk_results:
        raise RuntimeError(
            f"All chunk transcriptions failed ({failed_count}/{len(chunks)}). Check Mistral API availability and timeout settings."
        )

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
        "failed_chunks": failed_count,
        "total_chunks": len(chunks),
    }
