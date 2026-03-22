"""ScriptRepository — DB operations for pedagogical scripts."""
from typing import Optional
from sqlalchemy.orm import Session
from db.models.pedagogical_script import PedagogicalScript


class ScriptRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_lecture(self, lecture_id: str) -> Optional[PedagogicalScript]:
        return (
            self.db.query(PedagogicalScript)
            .filter(PedagogicalScript.lecture_id == lecture_id)
            .order_by(PedagogicalScript.version.desc())
            .first()
        )

    def save(self, lecture_id: str, content: str, model_info: dict) -> PedagogicalScript:
        # Get next version number
        latest = self.get_by_lecture(lecture_id)
        next_version = (latest.version + 1) if latest else 1

        script = PedagogicalScript(
            lecture_id=lecture_id,
            version=next_version,
            content=content,
            generated_by=model_info,
        )
        self.db.add(script)
        self.db.commit()
        self.db.refresh(script)
        return script
