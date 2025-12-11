from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from uuid import uuid4
from typing import Optional, Dict, List
import json

from app.core.event_bus import bus, Topic
from app.models.protocol import TaskPayload
from app.core.db import db
from app.core.state_manager import state_manager

router = APIRouter()

class TaskRequest(BaseModel):
    topic: str
    depth: str = "light"  # light | deep

class TaskResponse(BaseModel):
    task_id: str
    status: str

@router.post("/task", response_model=TaskResponse)
async def create_task(req: TaskRequest):
    """提交新任务"""
    task_id = str(uuid4())
    
    # 1. 构造初始 Payload
    payload = TaskPayload(
        task_id=task_id,
        topic=req.topic,
        step="init",
        params={"depth": req.depth}
    )
    
    # 2. 初始化 MongoDB 记录（确保前端能及时查到状态）
    state_manager.init_task(task_id, req.topic, payload.params)
    
    # 3. 推送到 Redis (触发 Planner)
    bus.publish(Topic.PLANNER, payload.model_dump())
    
    return {"task_id": task_id, "status": "PENDING"}

@router.get("/task/{task_id}")
async def get_task_status(task_id: str):
    """查询任务状态与轨迹"""
    # 1. 查主任务状态
    task = db.tasks.find_one({"task_id": task_id}, {"_id": 0})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    # 2. 查步骤轨迹 (Steps)
    steps_cursor = db.steps.find({"task_id": task_id}, {"_id": 0}).sort("created_at", 1)
    steps = list(steps_cursor)
    
    # 3. 如果有生成的报告内容，最好也取出来（Writer 可能会把结果存到 output_data）
    # 或者我们约定前端通过 /artifact/ 下载 PDF，通过 text 渲染 Markdown
    # 这里我们简单拼装一下，如果有 report_path，前端可以去下载
    
    return {
        "info": task,
        "timeline": steps
    }