Agent 工具集合（Search/Fetch/Trials/Export 等）
------------------------------------------------
schema.py: 用 Pydantic 定义工具输入输出格式，让 Agent 调用时有明确的字段校验。
chroma_client.py: ChromaDB 客户端，用于向量存储和检索。
chunking.py: 文本分块工具，将长文本切分成多个小块，用于向量存储。
dummy_search.py: 假的搜索工具，返回固定结果，用于测试。