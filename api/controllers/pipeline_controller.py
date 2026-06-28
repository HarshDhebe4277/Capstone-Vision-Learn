"""PipelineController — endpoints for triggering the processing pipeline.

Supports:
  POST /api/pipeline/process       — YouTube URL
  POST /api/pipeline/process-local — local file path
  POST /api/pipeline/upload        — multipart file upload
"""
import os
import traceback

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from db.session import get_db
from api.schemas.pipeline_schema import PipelineRunRequest, PipelineRunResponse, LocalPathRequest
from pipeline.orchestrator import run_pipeline, run_pipeline_local

router = APIRouter(prefix="/api/pipeline", tags=["Pipeline"])


@router.get("/status/{job_id}", summary="Get the status of a running pipeline job")
async def get_pipeline_status(job_id: str):
    """
    Returns current JSON status saved by the orchestrator in the storage directory.
    If the job does not exist yet, returns step 1 with 0 progress.
    """
    import json
    from pathlib import Path
    
    storage_path = Path(os.getenv("STORAGE_PATH", "./storage")).resolve()
    status_file = storage_path / job_id / "status.json"
    
    if status_file.exists():
        try:
            status_data = json.loads(status_file.read_text(encoding="utf-8"))
            return status_data
        except Exception:
            pass
            
    return {"current_step": 1, "progress": 0}


def _build_response(result: dict) -> PipelineRunResponse:
    return PipelineRunResponse(
        video_id=result["video_id"],
        audio=result["audio"],
        transcript=result["transcript"],
        script=result["script"],
        narration=result["narration"],
        frame_count=result["frame_count"],
        status="completed",
    )


@router.post("/process", response_model=PipelineRunResponse, summary="Process a YouTube lecture")
async def process_youtube_lecture(
    request: PipelineRunRequest,
    db: Session = Depends(get_db),
):
    """YouTube URL → full narration pipeline."""
    try:
        result = await run_pipeline(
            youtube_url=request.youtube_url,
            lecture_id=request.lecture_id,
            db_session=db,
        )
        return _build_response(result)
    except Exception as exc:
        print(f"[Pipeline ERROR]\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"{type(exc).__name__}: {exc}")


@router.post("/process-local", response_model=PipelineRunResponse, summary="Process a local video/audio file by path")
async def process_local_path(
    request: LocalPathRequest,
    db: Session = Depends(get_db),
):
    """Local file path → full narration pipeline. Accepts absolute or relative paths."""
    try:
        result = await run_pipeline_local(
            file_path=request.file_path,
            lecture_id=request.lecture_id,
            db_session=db,
        )
        return _build_response(result)
    except Exception as exc:
        print(f"[Pipeline ERROR]\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"{type(exc).__name__}: {exc}")


@router.post("/upload", response_model=PipelineRunResponse, summary="Upload a video/audio file and process")
async def upload_and_process(
    file: UploadFile = File(..., description="Video (mp4/mkv/avi/mov) or audio (mp3/wav/m4a) file"),
    lecture_id: str | None = Form(None),
    db: Session = Depends(get_db),
):
    """
    Upload a file directly from the browser, save it to storage/uploads/, then run pipeline.
    Max file size is controlled by FastAPI/uvicorn config.
    """
    from pipeline.services.local_file_processor import save_upload

    try:
        contents = await file.read()
        saved_path = save_upload(contents, file.filename or "upload.mp4")
        result = await run_pipeline_local(
            file_path=str(saved_path),
            lecture_id=lecture_id,
            db_session=db,
        )
        return _build_response(result)
    except Exception as exc:
        print(f"[Pipeline ERROR]\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"{type(exc).__name__}: {exc}")
