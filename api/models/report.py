from pydantic import BaseModel

class ReportResponse(BaseModel):
    markdown: str
