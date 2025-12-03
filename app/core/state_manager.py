from datetime import datetime
from app.core.db import db
from app.models.protocol import TaskPayload

class StateManager:
    def init_task(self, task_id: str, topic: str, params: dict):
        """初始化任务记录"""
        db.tasks.update_one(#在tasks中更新或插入一条记录
            {"task_id": task_id},
            {
                "$set": {
                    "task_id": task_id,
                    "topic": topic,
                    "params": params,
                    "status": "RUNNING",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )

    def is_step_completed(self, task_id: str, step_name: str) -> bool:
        """
        检查点查询：判断该步骤是否已持久化完成
        """
        record = db.steps.find_one({"task_id": task_id, "step_name": step_name})
        return record is not None

    def save_checkpoint(self, payload: TaskPayload, input_payload: TaskPayload):
        """
        保存检查点：记录步骤完成，并保存输入/输出数据
        """
        # 1. 插入步骤记录
        step_doc = {
            "task_id": payload.task_id,
            "step_name": payload.step,
            "input_data": input_payload.data,   # 记录输入
            "output_data": payload.data,        # 记录输出
            "history": payload.history,
            "created_at": datetime.utcnow()
        }
        
        # 使用 update_one + upsert 防止并发重复插入报错
        db.steps.update_one(
            {"task_id": payload.task_id, "step_name": payload.step},
            {"$set": step_doc},
            upsert=True
        )

        # 2. 更新主任务状态
        db.tasks.update_one(
            {"task_id": payload.task_id},
            {
                "$set": {
                    "updated_at": datetime.utcnow(),
                    "last_step": payload.step
                }
            }
        )

    def mark_task_done(self, task_id: str, artifact_path: str = None):
        """任务结束"""
        update_doc = {
            "status": "DONE",
            "updated_at": datetime.utcnow()
        }
        if artifact_path:
            update_doc["result_path"] = artifact_path
            
        db.tasks.update_one(
            {"task_id": task_id},
            {"$set": update_doc}
        )

# 全局单例
state_manager = StateManager()