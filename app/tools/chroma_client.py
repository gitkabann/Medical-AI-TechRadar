import chromadb
from chromadb.utils import embedding_functions
from app.core.config import settings
from app.core.logger import get_logger
from app.models.document import DocumentChunk

logger = get_logger(__name__)

# 初始化嵌入模型（这里可替换成 Qwen Embedding 模型）
embedding_fn = embedding_functions.DefaultEmbeddingFunction()

# 连接本地或远程 Chroma
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(
    name="medical_docs",
    embedding_function=embedding_fn
)

def ingest(chunks: list[DocumentChunk]):
    """将分块内容写入 Chroma 向量库"""
    logger.info(f"开始入库 {len(chunks)} 个文档分块")
    ids = [c.chunk_id for c in chunks]
    docs = [c.content for c in chunks]
    metas = [c.metadata.model_dump(exclude_none=True) for c in chunks] #model_dump() 方法将 Pydantic 模型转换为字典
    collection.add(ids=ids, documents=docs, metadatas=metas)
    logger.info("Chroma 入库完成")

def query(text: str, n_results: int = 3):
    """从 Chroma 中查询相似内容"""
    logger.info(f"查询向量相似内容: {text[:30]}...")
    res = collection.query(query_texts=[text], n_results=n_results)
    return [
        {
            "content": doc,
            "score": score,
            "metadata": meta
        }
        for doc, score, meta in zip(
            res["documents"][0],
            res["distances"][0],
            res["metadatas"][0]
        )
    ]
