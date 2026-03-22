"""Pipeline orchestration: download video, extract audio, transcribe, select key timestamps,
extract frames, generate pedagogical script via LLM, produce TTS-ready output.

This is a high-level orchestrator with pragmatic commands — adapt paths and model names
for your environment. It expects a venv with packages installed from `pipeline/requirements.txt`.
"""
import os
import subprocess
import json
import shutil
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Dict, Any

from mistral_client import get_mistral_client

load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / '.env')

STORAGE = Path(os.getenv("STORAGE_PATH", "./storage")).resolve()
STORAGE.mkdir(parents=True, exist_ok=True)

MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral-large-3")

# create a unified client (prefers LangChain if available)
client = get_mistral_client(prefer_langchain=True, model=MISTRAL_MODEL)


def run_cmd(cmd: List[str], cwd: Path = None) -> None:
    print("RUN:", " ".join(cmd))
    subprocess.run(cmd, check=True, cwd=cwd)


def download_video(youtube_url: str, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    # Download best video and audio; save filename template
    out_template = str(out_dir / "%(id)s.%(ext)s")
    cmd = [
        "yt-dlp",
        "-f",
        "bv*+ba/b",
        "-o",
        out_template,
        youtube_url,
    ]
    run_cmd(cmd)

    # Find the downloaded file (assume one file present)
    files = list(out_dir.glob("*.*"))
    if not files:
        raise FileNotFoundError("Downloaded video not found")
    # return the largest file (likely video)
    return max(files, key=lambda p: p.stat().st_size)


def extract_audio(video_path: Path, out_audio: Path) -> Path:
    # Use yt-dlp to extract audio directly
    cmd = [
        "yt-dlp",
        "-x",
        "--audio-format",
        "wav",
        "-o",
        str(out_audio),
        str(video_path),
    ]
    run_cmd(cmd)
    return Path(str(out_audio).replace("%(title)s", video_path.stem))


def transcribe_with_whispers2t(audio_path: Path, out_json: Path) -> Dict[str, Any]:
    # This assumes WhisperS2T provides a CLI that outputs JSON segments with timestamps
    whisper_cli = os.getenv("WHISPERS2T_PATH", "whisper_s2t")
    cmd = [whisper_cli, "--model", "small", "--input", str(audio_path), "--output", str(out_json)]
    run_cmd(cmd)
    # load result if JSON
    if out_json.exists():
        return json.loads(out_json.read_text())
    # If CLI produced a different file, adjust as needed
    return {}


def ask_mistral_for_key_timestamps(transcript: str, client: MistralClient) -> List[Dict[str, Any]]:
    # Prompt Mistral to analyze transcripts and return important timestamp ranges
    prompt = (
        "Given the transcript with timestamps, return a JSON array of important segments "
        "for extracting frames: each item {start: seconds, end: seconds, reason: short}.\n\n"
        + transcript
        + "\n\nRespond ONLY with valid JSON."
    )
    resp = client.create_completion(model=MISTRAL_MODEL, prompt=prompt, max_tokens=800)
    # The exact response shape depends on Mistral; try to parse returned text
    text = resp.get("output", resp)
    if isinstance(text, dict):
        # already parsed
        return text
    # if output is string
    possible = None
    if isinstance(text, str):
        try:
            possible = json.loads(text)
        except Exception:
            # attempt to extract JSON substring
            import re

            m = re.search(r"(\[\{.*\}\])", text, re.S)
            if m:
                possible = json.loads(m.group(1))
    return possible or []


def extract_frames(video_path: Path, segments: List[Dict[str, Any]], frames_out: Path) -> List[Dict[str, Any]]:
    frames_out.mkdir(parents=True, exist_ok=True)
    results = []
    for i, seg in enumerate(segments):
        start = seg.get("start")
        end = seg.get("end", start + 2)
        mid = (start + end) / 2.0
        out_file = frames_out / f"frame_{i:03d}_{int(mid)}.jpg"
        cmd = [
            "ffmpeg",
            "-y",
            "-ss",
            str(mid),
            "-i",
            str(video_path),
            "-frames:v",
            "1",
            str(out_file),
        ]
        run_cmd(cmd)
        results.append({"timestamp": mid, "path": str(out_file), "reason": seg.get("reason")})
    return results


def generate_pedagogical_script(frames: List[Dict[str, Any]], transcript: str, client: MistralClient) -> str:
    # Create a prompt combining key frames and transcript snippets
    prompt = "Generate a pedagogical narration script for the lecture. Use the frame timestamps and transcript to describe visual content and explain concepts. Output full script text.\n\n"
    prompt += "Transcript excerpt:\n" + transcript + "\n\n"
    prompt += "Frames:\n"
    for f in frames:
        prompt += f"- timestamp: {f['timestamp']}, image: {f['path']}, reason: {f.get('reason')}\n"
    resp = client.create_completion(model=MISTRAL_MODEL, prompt=prompt, max_tokens=2000)
    out = resp.get("output") or resp
    if isinstance(out, dict):
        return out.get("text", json.dumps(out))
    return out if isinstance(out, str) else json.dumps(out)


def main(youtube_url: str, workdir: Path):
    workdir = Path(workdir).resolve()
    video_dir = workdir / "video"
    audio_dir = workdir / "audio"
    transcript_dir = workdir / "transcript"
    frames_dir = workdir / "frames"

    video_path = download_video(youtube_url, video_dir)
    audio_path = audio_dir / (video_path.stem + ".wav")
    audio_dir.mkdir(parents=True, exist_ok=True)
    # extract audio
    extract_audio(video_path, str(audio_path))

    # transcribe
    transcript_json = transcript_dir / (video_path.stem + ".json")
    transcript_dir.mkdir(parents=True, exist_ok=True)
    transcription = transcribe_with_whispers2t(audio_path, transcript_json)

    # prepare transcript text for LLM
    transcript_text = transcription.get("text") if isinstance(transcription, dict) else str(transcription)

    # Mistral client
    # ask for key timestamps
    segments = ask_mistral_for_key_timestamps(transcript_text, client)

    # extract frames for segments
    frames = extract_frames(video_path, segments, frames_dir)

    # generate pedagogical script
    script = generate_pedagogical_script(frames, transcript_text, client)

    # save script
    out_script = workdir / (video_path.stem + "_pedagogical_script.txt")
    out_script.write_text(script, encoding="utf-8")
    print("Saved script to", out_script)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("youtube_url")
    parser.add_argument("--workdir", default=str(STORAGE))
    args = parser.parse_args()
    main(args.youtube_url, args.workdir)
