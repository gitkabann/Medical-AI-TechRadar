from pydantic import BaseModel, Field
from typing import List, Literal

class ExecutionPlan(BaseModel):
    """
    描述任务的执行策略
    """
    mode: Literal["light", "deep"] = "light"# 只能是light或deep，默认是light
    sources: List[str] = Field(default_factory=list, description="需要抓取的数据源列表")
    max_items: int = Field(default=3, description="每个源抓取的最大数量")
    enable_trials: bool = Field(default=False, description="是否启用临床试验检索")
    
    # 用于生成的提示词指令
    report_style: str = "brief" # brief | comprehensive

    @classmethod
    def create_light(cls):
        """轻量模式：只查文献，少量，不查代码和试验"""
        return cls(
            mode="light",
            sources=["pubmed", "arxiv"],
            max_items=3,
            enable_trials=False,
            report_style="brief"
        )

    @classmethod
    def create_deep(cls):
        """深度模式：全量查询"""
        return cls(
            mode="deep",
            sources=["pubmed", "arxiv", "github"],
            max_items=10,
            enable_trials=True,
            report_style="comprehensive"
        )