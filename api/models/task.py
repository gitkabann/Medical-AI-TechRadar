from pydantic import BaseModel
from typing import Literal

class TaskRequest(BaseModel):
    topic: str
    scope: Literal["literature", "code", "trial", "all"]
    depth: Literal["light", "deep"]

class TaskResponse(BaseModel):
    task_id: str
