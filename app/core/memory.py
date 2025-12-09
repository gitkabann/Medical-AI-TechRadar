import uuid
import json
from datetime import datetime
from typing import Optional, Dict, Any
from app.core.logger import get_logger
import chromadb
from chromadb.config import Settings

logger = get_logger("Memory")

DB_DIR = "./chroma_db"

class TaskMemory:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=DB_DIR)
        # 专门的集合，用于存储任务级别的记忆
        self.collection = self.client.get_or_create_collection(name="task_memory")

    def remember_task(self, topic: str, summary: str, artifact_path: str, tags: str = ""):
        """
        任务完成后，将任务主题与结果摘要存入向量库
        """
        try:
            doc_id = str(uuid.uuid4())
            # 存入：Topic 作为向量内容，Metadata 存摘要和文件路径
            self.collection.add(
                ids=[doc_id],
                documents=[topic],
                metadatas=[{
                    "topic": topic,
                    "summary": summary[:1000], # 限制长度
                    "artifact_path": artifact_path,
                    "tags": tags,
                    "timestamp": datetime.now().isoformat()
                }]
            )
            logger.info(f"🧠 已记住任务: {topic}")
        except Exception as e:
            logger.error(f"🧠 保存任务记忆失败: {e}")

    def recall_task(self, topic: str, threshold: float = 0.3) -> Optional[Dict[str, Any]]:
        """
        回忆：查找是否有相似的任务已完成
        threshold: 距离阈值（越小越相似），Chroma 默认 L2 距离
        """
        try:
            results = self.collection.query(
                query_texts=[topic],
                n_results=1
            )
            
            if not results["ids"] or not results["ids"][0]:
                return None

            distance = results["distances"][0][0]
            metadata = results["metadatas"][0][0]

            logger.info(f"🧠 回忆查询: '{topic}' | 最佳匹配: '{metadata['topic']}' (L2距离={distance:.4f})")

            # 如果距离小于阈值，认为是同一个任务
            if distance < threshold:
                return metadata
            
            return None

        except Exception as e:
            logger.warning(f"🧠 回忆任务失败: {e}")
            return None

# 全局单例
task_memory = TaskMemory()