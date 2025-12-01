from app.core.event_bus import bus, Topic
from enum import Enum
import json
import time

class TaskStatus(str, Enum):
    PENDING = "PENDING"# 任务刚刚创建，等待激活。
    RUNNING = "RUNNING"# 任务正在执行中。
    DONE = "DONE"# 任务已完成。
    FAILED = "FAILED"# 任务执行失败。

class Orchestrator:
    def __init__(self):
        self.group_name = "group_orchestrator"# 定义 Orchestrator 实例所在的消费者组名称。由于 Orchestrator 是总指挥，通常只有一个，但仍需要加入组来管理 Offset。
        self.consumer_name = f"orchestrator_{int(time.time())}"# 定义 Orchestrator 实例的唯一名称，使用时间戳确保唯一性。
        
        # 1. 初始化所有 Topic 的消费者组
        self._init_groups()

    def _init_groups(self):
        """在每个 Topic 上创建或确认消费者组已经存在"""
        for topic in Topic:
            bus.create_group(topic, self.group_name)

    def create_task(self, task_id: str, topic: str, params: dict):
        """
        用户提交任务 -> 写入状态 -> 发送消息
        """
        # 1. 记录初始状态 (使用 Redis Hash)
        state_key = f"task:{task_id}"
        bus.redis.hset(state_key, mapping={#使用 Redis Hash (哈希表) 存储任务的初始元数据，包括 PENDING 状态、创建时间、原始 Topic 和参数。
            "status": TaskStatus.PENDING,
            "topic": topic,
            "created_at": time.time(),
            "params": json.dumps(params)
        })
        print(f"⭐ [Orch] Task {task_id} Created.")

        # 2. 根据任务类型分发到不同 Stream (解耦) (目前假设都去 Crawler)
        # 实际上根据 Plan，这里可能先发给 PLANNER
        target_topic = Topic.CRAWLER # 示例：直接发给爬虫
        bus.publish(target_topic, {"task_id": task_id, "params": params})
        
        # 更新状态为 Running
        bus.redis.hset(state_key, "status", TaskStatus.RUNNING)

    def get_task_status(self, task_id: str):
        state = bus.redis.hgetall(f"task:{task_id}")
        return state

# 全局单例
orchestrator = Orchestrator()