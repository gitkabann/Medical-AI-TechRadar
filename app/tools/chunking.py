import re
from typing import List
from app.models.document import DocumentChunk, DocumentMetadata

def simple_chunk(text: str, source: str, url: str = None) -> List[DocumentChunk]:
    """
    简单分块器：按双换行或句号分段。
    返回若干 DocumentChunk 对象。
    """
    parts = re.split(r'\n\n|。', text)
    chunks = []
    for i, part in enumerate(parts):
        if len(part.strip()) < 5:  # 太短的段落略过
            continue
        meta = DocumentMetadata(source=source, url=url)
        chunks.append(DocumentChunk(
            chunk_id=f"{source}_{i}",
            content=part.strip(),
            metadata=meta
        ))
    return chunks
