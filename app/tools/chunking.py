from typing import List
from app.models.document import DocumentChunk, DocumentMetadata
from app.models.base import gen_id
import re
def simple_chunk(text: str, source: str, url: str = None) -> List[DocumentChunk]:#保留给test_chroma.py使用
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
def chunk_text(text: str, source: str, metadata_extra: dict = None) -> List[DocumentChunk]:
    """
    基于固定长度的分块器：每 300 字为一块。
    返回若干 DocumentChunk 对象。
    text: 待分块的abstract
    其余参数用于构造 DocumentMetadata
    """

    chunks = []
    CHUNK_SIZE = 300

    # --- 🔥 关键补丁：把 metadata 中的 datetime 等转换成字符串 ---
    safe_meta_extra = {
        k: (str(v) if not isinstance(v, (str, int, float, bool, type(None))) else v)
        for k, v in (metadata_extra or {}).items()
    }

    for i in range(0, len(text), CHUNK_SIZE):
        content = text[i:i+CHUNK_SIZE]

        meta = DocumentMetadata(
            source=source,
            section="abstract",
            **safe_meta_extra
        )

        chunks.append(DocumentChunk(
            chunk_id=gen_id("chunk"),
            content=content,
            metadata=meta
        ))

    return chunks
