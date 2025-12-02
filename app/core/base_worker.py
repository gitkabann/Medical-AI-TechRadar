import json
import traceback
from abc import ABC, abstractmethod
from app.core.event_bus import bus, Topic
from app.models.protocol import TaskPayload

class BaseWorker(ABC):
    def __init__(self, 
                 listen_topic: Topic, 
                 publish_topic: Topic, 
                 group_name: str = "group_main",
                 worker_name: str = "worker_1"):
        self.listen_topic = listen_topic
        self.publish_topic = publish_topic
        self.group_name = group_name
        self.worker_name = worker_name
        
        # 确保消费者组存在
        bus.create_group(listen_topic, group_name)

    def is_processed(self, task_id: str, step: str) -> bool:
        """幂等性检查：判断该任务的该步骤是否已完成"""
        key = f"completed:{task_id}:{step}"#独特的键名
        return bus.redis.exists(key) > 0#检查该键名是否存在，存在则表示该步骤已完成，见下方的 mark_processed 方法

    def mark_processed(self, task_id: str, step: str):
        """标记步骤完成，有效期 24h"""
        key = f"completed:{task_id}:{step}"#独特的键名
        bus.redis.set(key, "1", ex=86400)#将上面构造的 key 设置一个值为 "1" 的记录，有效期 24 小时

    def run(self):
        print(f"👷 [{self.__class__.__name__}] Listening on {self.listen_topic.value}...")
        while True:
            try:
                # 阻塞读取消息
                messages = bus.consume(self.listen_topic, self.group_name, self.worker_name, count=1, block=5000)
                
                for msg in messages:
                    msg_id = msg["id"]
                    raw_payload = msg["payload"]
                    
                    try:
                        # 1. 解析 Payload
                        # 兼容直接传 dict 或 pydantic json
                        data_dict = raw_payload if isinstance(raw_payload, dict) else json.loads(raw_payload)
                        payload = TaskPayload(**data_dict)
                        
                        print(f"📥 [{self.__class__.__name__}] Got task: {payload.task_id} (Step: {payload.step})")

                        # 2. 幂等性过滤
                        if self.is_processed(payload.task_id, payload.step):
                            print(f"⏭️  [Skip] Task {payload.task_id} step {payload.step} already done.")
                            bus.ack(self.listen_topic, self.group_name, msg_id)
                            continue

                        # 3. 执行具体业务逻辑 (由子类实现)
                        result_payload = self.process(payload)

                        # 4. 标记完成 + ACK
                        self.mark_processed(payload.task_id, payload.step)#mark/is_processed解决的是业务逻辑层面的“这个任务步骤只执行一次”的问题。
                        bus.ack(self.listen_topic, self.group_name, msg_id)#bus.ack解决的是Redis Streams层面的“我成功收到了并开始处理了”的问题。

                        # 5. 发布下一步 (如果有)
                        if result_payload and self.publish_topic:
                            bus.publish(self.publish_topic, result_payload.model_dump())
                    
                    except Exception as e:
                        print(f"❌ [{self.__class__.__name__}] Error: {e}")
                        traceback.print_exc()
                        # 可以在这里实现死信队列 (Dead Letter Queue) 逻辑

            except KeyboardInterrupt:
                print("🛑 Stopping worker...")
                break

    @abstractmethod
    def process(self, payload: TaskPayload) -> TaskPayload:
        """业务逻辑，返回传递给下一个 Agent 的 Payload"""
        pass