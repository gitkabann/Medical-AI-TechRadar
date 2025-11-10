from fastapi import APIRouter
from api.models.task import TaskRequest, TaskResponse
from api.models.status import StatusResponse
from api.models.report import ReportResponse

router = APIRouter()

@router.post("/task", response_model=TaskResponse)
async def create_task(req: TaskRequest):
    # TODO: 实际任务创建逻辑
    return {"task_id": "demo-task-uuid"}

@router.get("/status", response_model=StatusResponse)
async def get_status(task_id: str):
    # TODO: 查询任务进度
    return {
        "state": "Running",
        "progress": 0.35,
        "steps": [
            {"step_id": "1", "name": "SearchPubMed", "status": "done"},
            {"step_id": "2", "name": "FetchGitHub", "status": "running"},
        ],
    }

@router.get("/report", response_model=ReportResponse)
async def get_report(task_id: str):
    # TODO: 返回最终报告
    return {
        "markdown": "## 报告示例\n这是一个占位报告。\n[1] 示例引用"
    }