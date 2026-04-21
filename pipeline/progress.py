from typing import Dict, Any

# Global dict to store pipeline progress: file_id -> progress info
PIPELINE_PROGRESS: Dict[str, Dict[str, Any]] = {}

def update_progress(file_id: str, step: int, progress: float, message: str):
    if file_id:
        PIPELINE_PROGRESS[file_id] = {
            "step": step,
            "progress": progress,
            "message": message
        }

def get_progress(file_id: str) -> Dict[str, Any]:
    return PIPELINE_PROGRESS.get(file_id, {
        "step": 0, 
        "progress": 0.0, 
        "message": "Initializing pipeline..."
    })

def clear_progress(file_id: str):
    if file_id in PIPELINE_PROGRESS:
        del PIPELINE_PROGRESS[file_id]
