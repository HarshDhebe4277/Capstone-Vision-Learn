"""PipelineCache — simple JSON file-based cache to avoid re-processing the same video."""
import json
from pathlib import Path
from typing import Any


class PipelineCache:
    """
    Stores intermediate pipeline results in a hidden JSON file inside the work directory.
    Re-running the pipeline for the same video_id skips completed steps automatically.
    """

    def __init__(self, workdir: Path):
        self._path = workdir / ".cache" / "pipeline_state.json"
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._data: dict = self._load()

    def _load(self) -> dict:
        if self._path.exists():
            try:
                return json.loads(self._path.read_text(encoding="utf-8"))
            except Exception:
                return {}
        return {}

    def _persist(self) -> None:
        self._path.write_text(json.dumps(self._data, indent=2), encoding="utf-8")

    def has(self, key: str) -> bool:
        return key in self._data

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value
        self._persist()

    def clear(self) -> None:
        self._data = {}
        self._persist()
