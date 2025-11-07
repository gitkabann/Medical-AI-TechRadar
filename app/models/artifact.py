# app/models/artifact.py
from pydantic import BaseModel
from typing import Optional, Dict, Any
from .enums import ArtifactType

class Artifact(BaseModel):
    artifact_id: str
    task_id: str
    type: ArtifactType
    mime: str
    uri: Optional[str] = None
    inline: Optional[str] = None
    meta: Dict[str, Any] = {}
