from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class DocumentMetadata(BaseModel):
    """统一的文档元数据"""
    source: str
    url: Optional[str] = None
    date : Optional[datetime] = None
    section: Optional[str] = None # 章节、段落标题等

class DocumentChunk(BaseModel):
    """单个分块（Chunk）"""
    chunk_id: str
    content: str
    metadata: DocumentMetadata