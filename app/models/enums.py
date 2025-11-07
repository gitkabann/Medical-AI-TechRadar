# app/models/enums.py
from enum import Enum
class TaskState(str, Enum):
    pending = "PENDING"
    running = "RUNNING"
    done    = "DONE"
    failed  = "FAILED"

class ArtifactType(str, Enum):
    markdown = "MARKDOWN"
    pdf      = "PDF"
    table    = "TABLE"
    chart    = "CHART"
