# app/tools/dummy_search.py
from langchain.tools import BaseTool
from typing import Type
from pydantic import BaseModel
from app.tools.schema import SearchInput, SearchOutput

class DummySearchTool(BaseTool):
    """一个假的搜索工具，用于测试 Agent 调用"""
    name: str = "dummy_search"
    description: str = "返回模拟的搜索结果（结构化输出）"
    args_schema: Type[BaseModel] = SearchInput  # 输入类型模型

    def _run(self, query: str) -> SearchOutput:
        """同步执行"""
        results = [
            f"伪搜索结果：{query} 相关论文1",
            f"伪搜索结果：{query} 相关论文2"
        ]
        return SearchOutput(results=results)

    async def _arun(self, query: str) -> SearchOutput:
        """异步执行"""
        return self._run(query)