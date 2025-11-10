from pydantic import BaseModel
from typing import List

class StepInfo(BaseModel):
    step_id: str
    name: str
    status: str

class StatusResponse(BaseModel):
    state: str
    progress: float
    steps: List[StepInfo]
