from typing import List
from app.models.document import DocumentChunk, DocumentMetadata
from app.models.base import gen_id

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
