from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from .enums import TaskState          # 枚举：任务/步骤状态，如 pending, running, done, failed
from .base import Timestamps, gen_id  # 时间戳对象与 ID 生成函数

# ✅ 表示一个任务中的单个执行步骤（Step）
class Step(BaseModel):
    # 每个步骤唯一ID，比如 "step-20251110-xxxxx"
    step_id: str = Field(default_factory=lambda: gen_id("step"))
    # 步骤名称（例如 "SearchPubMed"、"FetchGitHub"）
    name: str
    # 步骤当前状态（pending/running/done/failed）
    state: TaskState = TaskState.pending
    # 可选的状态信息（例如错误提示、进度描述）
    message: Optional[str] = None
    # meta 用于附加上下文信息（如耗时、URL、结果数等），灵活扩展
    meta: Dict[str, Any] = {}

# ✅ 表示一个完整的任务（Task）
class Task(BaseModel):
    # 全局唯一任务ID（task-开头，系统自动生成）
    task_id: str = Field(default_factory=lambda: gen_id("task"))
    # 用户输入的主题，如 "CT 肺结节分割"
    topic: str
    # 任务范围，比如 "literature" / "code" / "trial" / "all"
    scope: str = "default"
    # 搜索或分析深度：整数表示层级（例如1代表浅层，2代表深入）
    depth: int = 1
    # 当前任务总体状态（pending/running/done/failed）
    state: TaskState = TaskState.pending
    # 当前进度，0.0 ~ 1.0 之间的小数
    progress: float = 0.0
    # 子步骤列表（每个Step表示一个阶段）
    steps: List[Step] = []
    # 产物文件路径或ID列表（报告、图表、缓存等）
    artifacts: List[str] = []
    # 时间戳对象，记录创建时间/开始时间/结束时间
    timestamps: Timestamps = Timestamps()
