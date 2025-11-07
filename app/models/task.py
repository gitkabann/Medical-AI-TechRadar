# app/models/task.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from .enums import TaskState
from .base import Timestamps, gen_id

class Step(BaseModel):
    step_id: str = Field(default_factory=lambda: gen_id("step"))
    name: str
    state: TaskState = TaskState.pending
    message: Optional[str] = None
    meta: Dict[str, Any] = {}

class Task(BaseModel):
    task_id: str = Field(default_factory=lambda: gen_id("task"))
    topic: str
    scope: str = "default"
    depth: int = 1
    state: TaskState = TaskState.pending
    progress: float = 0.0
    steps: List[Step] = []
    artifacts: List[str] = []
    timestamps: Timestamps = Timestamps()
