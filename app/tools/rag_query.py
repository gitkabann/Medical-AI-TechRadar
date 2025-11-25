from typing import List, Dict, Any
from app.tools.chroma_client import collection, embedding_fn
from app.models.document import DocumentChunk

def query_rag(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """RAG 查询：将结果按 trial / others 分组返回"""

    # 编码 Query 得向量
    query_embedding = embedding_fn(query)
    
    # 检索 top_k
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    docs = results["documents"][0]
    metas = results["metadatas"][0]
    dists = results["distances"][0]

    rag_chunks = []
    for doc, meta, dist in zip(docs, metas, dists):
        rag_chunks.append({
            "content": doc,
            "metadata": meta,
            "score": float(dist),
        })

    # 按 trial / others 分组
    trial_chunks = [c for c in rag_chunks if c["metadata"]["source"] == "ClinicalTrials"]
    other_chunks = [c for c in rag_chunks if c["metadata"]["source"] != "ClinicalTrials"]
    
    return trial_chunks, other_chunks
