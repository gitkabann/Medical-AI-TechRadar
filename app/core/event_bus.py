import redis
from typing import Dict, Any, List, Optional
import json
import os
from enum import Enum

# 定义系统中的 Topic（频道）
class Topic(str, Enum):
    PLANNER = "stream:planner"   # 规划任务
    CRAWLER = "stream:crawler"   # 爬取数据
    RAG     = "stream:rag"       # 检索增强
    TRIALS  = "stream:trials"    # 临床试验
    WRITER  = "stream:writer"    # 报告生成
    LOGS    = "stream:logs"      # 系统日志

class EventBus:
    def __init__(self, host="localhost", port=6379, db=0):
        # 优先读取环境变量，方便后续 Docker 部署
        self.redis = redis.Redis(
            host=os.getenv("REDIS_HOST", host),
            port=int(os.getenv("REDIS_PORT", port)),
            db=int(os.getenv("REDIS_DB", db)),
            decode_responses=True # 自动解码为字符串
        )

    def publish(self, topic: Topic, payload: Dict[str, Any]) -> str:
        """
        发布消息到 Stream
        """
        # Redis Streams 只能存简单的 key-value，复杂对象需序列化
        message = {"payload": json.dumps(payload)}# 序列化payload为字符串，保存为字典
        msg_id = self.redis.xadd(topic, message)# 选择频道，存储message键值对，返回消息ID
        print(f"📨 [Bus] Pub -> {topic}: {msg_id}")
        return msg_id

    def create_group(self, topic: Topic, group: str):
        """
        创建消费者组（Consumer Group），实现消息的负载均衡与状态保存
        """
        try:
            # mkstream=True: 如果 Stream 不存在自动创建
            self.redis.xgroup_create(topic, group, id="0", mkstream=True)#id="0"表示从流的开始位置开始消费。mkstream=True表示如果流不存在，自动创建。
            print(f"🔧 [Bus] Created group '{group}' for {topic}")
        except redis.exceptions.ResponseError as e:
            if "BUSYGROUP" in str(e):
                print(f"ℹ️ [Bus] Group '{group}' already exists for {topic}")
            else:
                raise e

    def consume(self, topic: Topic, group: str, consumer_name: str, count=1, block=2000):
        """
        作为消费者组的一员读取消息
        block: 阻塞等待毫秒数
        """
        # group: 消费者组名
        # consumer_name: 消费者实例名（每个消费者组内唯一）
        # topic: 要消费的频道, > 表示读取“在此消费者组中尚未被分发给其他消费者”的新消息
        # count: 每次最多读取多少条消息
        # block: 阻塞等待毫秒数（0 表示不阻塞）
        resp = self.redis.xreadgroup(group, consumer_name, {topic: ">"}, count=count, block=block)
        
        parsed_messages = []
        if resp:
            # resp 结构: [[topic, [(msg_id, {data})]]]
            for _, messages in resp:
                for msg_id, data in messages:
                    payload = json.loads(data["payload"])
                    parsed_messages.append({
                        "id": msg_id,
                        "payload": payload
                    })# 解析消息ID和payload，保存为字典
        return parsed_messages

    def ack(self, topic: Topic, group: str, msg_id: str):
        """
        确认消息已处理（ACK），移动 offset
        """
        self.redis.xack(topic, group, msg_id)
        print(f"✅ [Bus] Ack {topic} {msg_id}")

# 全局单例
bus = EventBus()