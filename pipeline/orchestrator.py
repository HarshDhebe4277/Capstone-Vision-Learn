"""
Pipeline Orchestrator — wires all pipeline steps in an optimised async flow.

Architecture:
  Step 1 (parallel): fetch CDN stream URL + download audio-only
  Step 2: split audio into N chunks
  Step 3 (parallel): transcribe all chunks via Voxtral API
  Step 4: select key timestamps via Mistral LLM (LangChain)
  Step 5 (parallel): extract frames from CDN stream via ffmpeg
  Step 6: generate pedagogical script via Pixtral Vision (LangChain)
  Step 7: synthesise speech via Edge TTS
  Step 8: persist all results to PostgreSQL (optional if db session provided)
"""
import asyncio
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv

load_dotenv(override=True)

from pipeline.services.video_downloader import get_stream_url, download_audio
from pipeline.services.audio_chunker import split_audio_into_chunks
from pipeline.services.transcription_service import transcribe_audio_parallel
from pipeline.services.frame_extractor import extract_frames_parallel
from pipeline.services.tts_service import synthesize_narration
from pipeline.chains.timestamp_chain import build_timestamp_chain
from pipeline.chains.narration_chain import generate_narration_script
from pipeline.utils.cache import PipelineCache
from pipeline.utils.ffmpeg_utils import assert_ffmpeg
from pipeline.progress import update_progress

STORAGE: Path = Path(os.getenv("STORAGE_PATH", "./storage")).resolve()
AUDIO_CHUNK_COUNT: int = int(os.getenv("AUDIO_CHUNK_COUNT", "12"))


def _make_video_id(youtube_url: str, lecture_id: Optional[str]) -> str:
    """Derive a safe, filesystem-friendly ID from the YouTube URL."""
    if lecture_id:
        return lecture_id
    return hashlib.md5(youtube_url.encode()).hexdigest()[:12]


async def run_pipeline(
    youtube_url: str,
    lecture_id: Optional[str] = None,
    db_session=None,          # optional SQLAlchemy session for DB persistence
) -> Dict[str, Any]:
    """
    Run the full YouTube → Narration pipeline asynchronously.

    Returns a result dict with paths to every generated artifact.
    Intermediate results are cached; re-running the same video_id skips completed steps.
    """
    assert_ffmpeg()

    video_id = _make_video_id(youtube_url, lecture_id)
    workdir = STORAGE / video_id
    workdir.mkdir(parents=True, exist_ok=True)

    cache = PipelineCache(workdir)
    audio_path = workdir / "audio" / "audio.mp3"

    print(f"\n[Orchestrator] Starting pipeline for video_id={video_id}")

    # ── Step 1: Fetch stream URL + download audio in PARALLEL ──────────────
    if cache.has("stream_url") and audio_path.exists():
        update_progress(video_id, 1, 15.0, "Cache hit: audio already downloaded.")
        stream_url = cache.get("stream_url")
        print("[Step 1] Cache hit: stream URL + audio")
    else:
        update_progress(video_id, 1, 0.0, "Fetching YouTube stream URL & downloading audio in parallel...")
        print("[Step 1] Fetching stream URL and downloading audio in parallel...")
        stream_url, _ = await asyncio.gather(
            get_stream_url(youtube_url),
            download_audio(youtube_url, audio_path),
        )
        cache.set("stream_url", stream_url)
        print(f"[Step 1] Done — stream URL obtained, audio at {audio_path}")

    # ── Step 2: Split audio into chunks ────────────────────────────────────
    print(f"[Step 2] Splitting audio into {AUDIO_CHUNK_COUNT} chunks...")
    update_progress(video_id, 2, 20.0, f"Splitting audio into {AUDIO_CHUNK_COUNT} chunks...")
    chunks = split_audio_into_chunks(audio_path, n_chunks=AUDIO_CHUNK_COUNT)
    print(f"[Step 2] {len(chunks)} chunks created")

    # ── Step 3: Parallel Voxtral transcription ─────────────────────────────
    transcript_path = workdir / "transcript" / "transcript.json"

    if cache.has("transcript"):
        update_progress(video_id, 3, 40.0, "Cache hit: transcript already generated.")
        transcript_data = cache.get("transcript")
        print(f"[Step 3] Cache hit: {len(transcript_data['segments'])} segments")
    else:
        update_progress(video_id, 3, 25.0, f"Transcribing {len(chunks)} chunks in parallel via Voxtral API...")
        print(f"[Step 3] Transcribing {len(chunks)} chunks in parallel via Voxtral...")
        transcript_data = await transcribe_audio_parallel(chunks)
        update_progress(video_id, 3, 40.0, "Transcription complete.")
        transcript_path.parent.mkdir(parents=True, exist_ok=True)
        transcript_path.write_text(json.dumps(transcript_data, indent=2, ensure_ascii=False), encoding="utf-8")
        cache.set("transcript", transcript_data)
        print(f"[Step 3] Transcription complete — {len(transcript_data['segments'])} segments")

    # ── Step 4: Select key timestamps via Mistral LLM ─────────────────────
    if cache.has("segments"):
        update_progress(video_id, 4, 55.0, "Cache hit: key timestamps found.")
        segments = cache.get("segments")
        print(f"[Step 4] Cache hit: {len(segments)} key segments")
    else:
        update_progress(video_id, 4, 45.0, "Selecting key pedagogical timestamps via Mistral LLM...")
        print("[Step 4] Selecting key timestamps via Mistral LLM...")
        timestamp_chain = build_timestamp_chain()
        segments = await timestamp_chain.ainvoke(
            {"transcript": transcript_data["formatted_for_llm"]}
        )
        cache.set("segments", segments)
        print(f"[Step 4] {len(segments)} key segments identified")

    # ── Step 5: Extract frames in PARALLEL from CDN stream ─────────────────
    frames_dir = workdir / "frames"

    if cache.has("frames") and frames_dir.exists():
        update_progress(video_id, 5, 70.0, "Cache hit: video frames extracted.")
        frames = cache.get("frames")
        print(f"[Step 5] Cache hit: {len(frames)} frames")
    else:
        update_progress(video_id, 5, 60.0, f"Extracting {len(segments)} frames in parallel from stream...")
        print(f"[Step 5] Extracting {len(segments)} frames in parallel from CDN stream...")
        frames = await extract_frames_parallel(stream_url, segments, frames_dir)
        cache.set("frames", frames)
        print(f"[Step 5] {len(frames)} frames extracted")

    # ── Step 6: Generate pedagogical script via Vision Model ────────────
    script_path = workdir / "script.txt"

    if cache.has("script"):
        update_progress(video_id, 6, 85.0, "Cache hit: narration script found.")
        script = cache.get("script")
        print(f"[Step 6] Cache hit: script ({len(script)} chars)")
    else:
        vision_model_name = os.getenv("MISTRAL_VISION_MODEL", "pixtral-12b-latest")
        update_progress(video_id, 6, 75.0, f"Generating pedagogical script via {vision_model_name}...")
        print(f"[Step 6] Generating pedagogical script via {vision_model_name} ({len(frames)} frames)...")
        script = await generate_narration_script(
            frames=frames,
            transcript=transcript_data["formatted_for_llm"],
        )
        script_path.write_text(script, encoding="utf-8")
        cache.set("script", script)
        print(f"[Step 6] Script saved ({len(script)} chars)")

    # ── Step 7: Edge TTS synthesis ─────────────────────────────────────────
    narration_path = workdir / "narration.mp3"

    if narration_path.exists():
        update_progress(video_id, 7, 95.0, "Cache hit: TTS audio generated.")
        print("[Step 7] Narration MP3 already exists, skipping TTS")
    else:
        update_progress(video_id, 7, 88.0, "Synthesising final narrative speech with Edge TTS...")
        print("[Step 7] Synthesising speech with Edge TTS...")
        await synthesize_narration(script, narration_path)
        print(f"[Step 7] Narration saved: {narration_path}")

    # ── Step 8: Persist to DB (optional) ──────────────────────────────────
    update_progress(video_id, 8, 98.0, "Finalizing pipeline and persisting to database...")
    if db_session and lecture_id:
        _persist_to_db(db_session, lecture_id, transcript_data, frames, script, str(narration_path))

    result = {
        "video_id": video_id,
        "workdir": str(workdir),
        "audio": str(audio_path),
        "transcript": str(transcript_path),
        "frames": frames,
        "frame_count": len(frames),
        "script": str(script_path),
        "narration": str(narration_path),
    }

    update_progress(video_id, 8, 100.0, "Processing complete! Output is ready.")
    print(f"\n[Orchestrator] Pipeline complete! All artifacts in {workdir}\n")
    return result


async def run_pipeline_local(
    file_path: str,
    db_session=None,
) -> Dict[str, Any]:
    """
    Run the full pipeline for a local video or audio file.

    Instead of yt-dlp, uses ffmpeg to extract audio from video files.
    Frame extraction uses the local file path directly (no CDN URL needed).
    Steps 3-7 are identical to the YouTube flow.
    """
    from pipeline.services.local_file_processor import (
        classify_file,
        make_file_id,
        extract_audio_from_video,
    )

    assert_ffmpeg()

    source_path = Path(file_path).resolve()
    if not source_path.exists():
        raise FileNotFoundError(f"File not found: {source_path}")

    file_type = classify_file(source_path)
    video_id = make_file_id(source_path)
    workdir = STORAGE / video_id
    workdir.mkdir(parents=True, exist_ok=True)

    cache = PipelineCache(workdir)
    audio_dir = workdir / "audio"
    audio_path = audio_dir / "audio.mp3"

    print(f"\n[Orchestrator] Local pipeline for {source_path.name} (id={video_id})")

    # ── Step 1: Get audio ───────────────────────────────────────────────────
    update_progress(video_id, 1, 0.0, "Verifying local file and extracting audio...")
    if audio_path.exists():
        update_progress(video_id, 1, 15.0, "Cache hit: audio file already extracted")
        print("[Step 1] Cache hit: audio file already extracted")
    elif file_type == "video":
        print("[Step 1] Extracting audio from local video with ffmpeg...")
        extract_audio_from_video(source_path, audio_dir)
        update_progress(video_id, 1, 15.0, "Extracted audio from local video...")
        print(f"[Step 1] Done — audio at {audio_path}")
    else:
        # audio file: just copy/symlink into workdir
        import shutil
        audio_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(source_path), str(audio_path))
        print(f"[Step 1] Audio file copied to {audio_path}")

    # ── Step 2: Split audio ─────────────────────────────────────────────────
    print(f"[Step 2] Splitting audio into {AUDIO_CHUNK_COUNT} chunks...")
    update_progress(video_id, 2, 20.0, f"Splitting audio into {AUDIO_CHUNK_COUNT} chunks...")
    chunks = split_audio_into_chunks(audio_path, n_chunks=AUDIO_CHUNK_COUNT)
    print(f"[Step 2] {len(chunks)} chunks created")

    # ── Step 3: Parallel Voxtral transcription ─────────────────────────────
    transcript_path = workdir / "transcript" / "transcript.json"
    if cache.has("transcript"):
        update_progress(video_id, 3, 40.0, "Cache hit: transcript already generated.")
        transcript_data = cache.get("transcript")
        print(f"[Step 3] Cache hit: {len(transcript_data['segments'])} segments")
    else:
        update_progress(video_id, 3, 25.0, f"Transcribing {len(chunks)} chunks in parallel via Voxtral API...")
        print(f"[Step 3] Transcribing {len(chunks)} chunks in parallel via Voxtral...")
        transcript_data = await transcribe_audio_parallel(chunks)
        transcript_path.parent.mkdir(parents=True, exist_ok=True)
        transcript_path.write_text(
            json.dumps(transcript_data, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        cache.set("transcript", transcript_data)
        print(f"[Step 3] Transcription complete — {len(transcript_data['segments'])} segments")

    # ── Step 4: Select key timestamps ──────────────────────────────────────
    segments = []
    if cache.has("segments"):
        update_progress(video_id, 4, 55.0, "Cache hit: key timestamps found.")
        segments = cache.get("segments")
        print(f"[Step 4] Cache hit: {len(segments)} key segments")
    else:
        update_progress(video_id, 4, 45.0, "Selecting key pedagogical timestamps via Mistral LLM...")
        print("[Step 4] Selecting key timestamps via Mistral LLM...")
        timestamp_chain = build_timestamp_chain()
        segments = await timestamp_chain.ainvoke(
            {"transcript": transcript_data["formatted_for_llm"]}
        )
        cache.set("segments", segments)
        print(f"[Step 4] {len(segments)} key segments identified")

    # ── Step 5: Extract frames (video only) ────────────────────────────────
    frames_dir = workdir / "frames"
    frames: list = []

    if file_type == "video":
        if cache.has("frames") and frames_dir.exists():
            update_progress(video_id, 5, 70.0, "Cache hit: video frames extracted.")
            frames = cache.get("frames")
            print(f"[Step 5] Cache hit: {len(frames)} frames")
        else:
            update_progress(video_id, 5, 60.0, f"Extracting {len(segments)} frames from local video...")
            print(f"[Step 5] Extracting {len(segments)} frames from local video...")
            # Use local file:// path — ffmpeg handles it natively
            frames = await extract_frames_parallel(str(source_path), segments, frames_dir)
            cache.set("frames", frames)
            print(f"[Step 5] {len(frames)} frames extracted")
    else:
        print("[Step 5] Audio-only input — skipping frame extraction")

    # ── Step 6: Generate pedagogical script ────────────────────────────────
    script_path = workdir / "script.txt"
    if cache.has("script"):
        update_progress(video_id, 6, 85.0, "Cache hit: narration script found.")
        script = cache.get("script")
        print(f"[Step 6] Cache hit: script ({len(script)} chars)")
    else:
        update_progress(video_id, 6, 75.0, "Generating pedagogical script via Vision LLM...")
        print(f"[Step 6] Generating pedagogical script...")
        script = await generate_narration_script(
            frames=frames,
            transcript=transcript_data["formatted_for_llm"],
        )
        script_path.write_text(script, encoding="utf-8")
        cache.set("script", script)
        print(f"[Step 6] Script saved ({len(script)} chars)")

    # ── Step 7: Edge TTS synthesis ─────────────────────────────────────────
    narration_path = workdir / "narration.mp3"
    if narration_path.exists():
        update_progress(video_id, 7, 95.0, "Cache hit: TTS audio generated.")
        print("[Step 7] Narration MP3 already exists, skipping TTS")
    else:
        update_progress(video_id, 7, 88.0, "Synthesising final narrative speech with Edge TTS...")
        print("[Step 7] Synthesising speech with Edge TTS...")
        await synthesize_narration(script, narration_path)
        print(f"[Step 7] Narration saved: {narration_path}")

    result = {
        "video_id": video_id,
        "workdir": str(workdir),
        "audio": str(audio_path),
        "transcript": str(transcript_path),
        "frames": frames,
        "frame_count": len(frames),
        "script": str(script_path),
        "narration": str(narration_path),
        "source": str(source_path),
    }

    update_progress(video_id, 8, 100.0, "Local processing complete! Output is ready.")
    print(f"\n[Orchestrator] Local pipeline complete! All artifacts in {workdir}\n")
    return result



def _persist_to_db(db, lecture_id, transcript_data, frames, script, narration_path):
    """Save all pipeline results to PostgreSQL via repositories."""
    from db.repositories.transcript_repository import TranscriptRepository
    from db.repositories.frame_repository import FrameRepository
    from db.repositories.script_repository import ScriptRepository
    from db.repositories.audio_repository import AudioRepository
    from db.repositories.lecture_repository import LectureRepository
    import os

    LectureRepository(db).update_status(lecture_id, "done")
    TranscriptRepository(db).save(
        lecture_id=lecture_id,
        content=transcript_data["full_text"],
        segments=transcript_data["segments"],
        model_info={"model": transcript_data.get("model", "voxtral-mini-latest")},
    )
    FrameRepository(db).bulk_save(lecture_id=lecture_id, frames=frames)
    saved_script = ScriptRepository(db).save(
        lecture_id=lecture_id,
        content=script,
        model_info={"model": os.getenv("MISTRAL_VISION_MODEL", "pixtral-12b-latest")},
    )
    AudioRepository(db).save(
        lecture_id=lecture_id,
        audio_path=narration_path,
        voice=os.getenv("EDGE_TTS_VOICE", "en-US-GuyNeural"),
        script_id=str(saved_script.id),
    )


# ── CLI entry point ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    import time

    parser = argparse.ArgumentParser(description="Vision-Learn AI Pipeline")
    parser.add_argument("youtube_url", help="YouTube video URL to process")
    parser.add_argument("--workdir", default=None, help="Override storage directory")
    parser.add_argument("--lecture-id", default=None, help="Lecture ID for DB persistence")
    args = parser.parse_args()

    if args.workdir:
        STORAGE = Path(args.workdir).resolve()

    start = time.perf_counter()
    result = asyncio.run(run_pipeline(args.youtube_url, args.lecture_id))
    elapsed = time.perf_counter() - start

    print(f"\n{'='*60}")
    print(f"  Pipeline finished in {elapsed:.1f} seconds")
    print(f"  Narration MP3 : {result['narration']}")
    print(f"  Script        : {result['script']}")
    print(f"  Frames        : {result['frame_count']}")
    print(f"{'='*60}\n")
