from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List

class TaskPayload(BaseModel):
    """
    Agent 之间传递的标准包裹
    """
    task_id: str
    topic: str
    step: str  # 当前步骤名，用于幂等性校验
    params: Dict[str, Any] = {} # 原始参数
    data: Dict[str, Any] = {}   # 上一步产生的数据
    history: List[str] = []     # 执行轨迹摘要

    def next_step(self, step_name: str, new_data: Dict[str, Any] = None) -> "TaskPayload":
        """生成下一步的 Payload"""
        new_payload = self.model_copy(deep=True)#深拷贝TaskPayload
        new_payload.step = step_name # 更新步骤名
        if new_data:
            new_payload.data.update(new_data)# 合并数据，不存在的 key 会被添加，存在的 key 会被覆盖
        new_payload.history.append(f"{self.step} -> {step_name}")# 记录执行轨迹
        return new_payload