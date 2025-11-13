from pydantic import BaseModel, Field

class SearchInput(BaseModel):
    """Search 工具的输入格式"""
    query: str = Field(..., description="要搜索的主题关键词")

class SearchOutput(BaseModel):
    """Search 工具的输出格式"""
    results: list[str] = Field(..., description="搜索结果文本列表")