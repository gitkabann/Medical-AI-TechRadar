import os
from pymongo import MongoClient
from datetime import datetime

# 环境变量 (后续 Docker 部署时通过 env 注入)
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "medical_tech_radar"

class DBClient:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)#创建一个与 MongoDB 服务器的连接实例
        self.db = self.client[DB_NAME]#选中一个特定的数据库
        
        # 集合定义
        self.tasks = self.db["tasks"]#访问或创建名为 tasks 的集合
        self.steps = self.db["steps"]#访问或创建名为 steps 的集合
        self.artifacts = self.db["artifacts"]#访问或创建名为 artifacts 的集合
        
        # 创建索引（幂等性关键）
        # 确保同一个 task 的同一个 step 唯一
        self.steps.create_index([("task_id", 1), ("step_name", 1)], unique=True)

# 全局同步客户端 (供 Workers 使用)
db = DBClient()