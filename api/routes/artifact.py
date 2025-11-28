# api/routes/artifact.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os

router = APIRouter()

@router.get("/artifact/{task_id}")
def download_artifact(task_id: str):
    pdf_path = f"app/artifacts/{task_id}.pdf"
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="Artifact not found")
    return FileResponse(pdf_path, filename=f"{task_id}.pdf", media_type="application/pdf")