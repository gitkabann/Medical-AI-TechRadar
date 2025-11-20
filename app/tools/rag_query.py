from typing import List, Dict, Any
from app.tools.chroma_client import collection, embedding_fn
from app.models.document import DocumentChunk

def query_rag(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """最简单的 RAG：从 Chroma 取 top_k 片段并返回 metadata。"""
    query_embedding = embedding_fn(query)#转向量
    
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    docs = results["documents"][0]
    metas = results["metadatas"][0]
    dists = results["distances"][0]

    rag_results = []
    for doc, meta, dist in zip(docs, metas, dists):
        rag_results.append({
            "content": doc,
            "metadata": meta,
            "score": float(dist),
        })
    return rag_results