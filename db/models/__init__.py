"""DB models package — imports all models so SQLAlchemy can register them."""
from db.models.associations import lecture_tags  # noqa: F401 — must load first
from db.models.user import User                         # noqa: F401
from db.models.tag import Tag                           # noqa: F401
from db.models.lecture import Lecture                   # noqa: F401
from db.models.media_file import MediaFile              # noqa: F401
from db.models.processing_job import ProcessingJob      # noqa: F401
from db.models.transcript import Transcript             # noqa: F401
from db.models.frame import Frame                       # noqa: F401
from db.models.visual_element import VisualElement      # noqa: F401
from db.models.pedagogical_script import PedagogicalScript  # noqa: F401
from db.models.audio_lecture import AudioLecture        # noqa: F401
from db.models.annotation import Annotation             # noqa: F401
from db.models.audit_log import AuditLog                # noqa: F401
from db.models.model_resource import ModelResource      # noqa: F401

__all__ = [
    "lecture_tags",
    "User", "Tag", "Lecture", "MediaFile", "ProcessingJob",
    "Transcript", "Frame", "VisualElement", "PedagogicalScript",
    "AudioLecture", "Annotation", "AuditLog", "ModelResource",
]
