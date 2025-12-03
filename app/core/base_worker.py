import json
import traceback
from abc import ABC, abstractmethod
from app.core.event_bus import bus, Topic
from app.models.protocol import TaskPayload
from app.core.state_manager import state_manager

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
        
        bus.create_group(listen_topic, group_name)#创建消费者组，如果已存在则忽略

    def run(self):
        print(f"👷 [{self.__class__.__name__}] Listening on {self.listen_topic.value} (DB-Backed)...")
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

                        # 2. 执行具体业务逻辑 (由子类实现)
                        result_payload = self.process(payload)

                        # 3. 状态持久化
                        if result_payload:
                            state_manager.save_checkpoint(result_payload, input_payload=payload)
                        if self.listen_topic == Topic.WRITER:
                            state_manager.mark_task_done(payload.task_id)

                        # 4. ACK
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