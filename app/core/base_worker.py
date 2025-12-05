# app/core/base_worker.py
import json
import traceback
from abc import ABC, abstractmethod
from app.core.event_bus import bus, Topic
from app.models.protocol import TaskPayload
from app.core.state_manager import state_manager
from app.models.protocol import TaskPayload, MAX_STEPS
from app.core.logger import get_logger
from app.core.error_handler import worker_error_handler

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

        # === 初始化Logger ===
        self.logger = get_logger(self.__class__.__name__)
        # === 创建消费者组 ===
        bus.create_group(listen_topic, group_name)

    def run(self):
        # print(f"👷 [{self.__class__.__name__}] Listening on {self.listen_topic.value} (DB-Backed)...")
        self.logger.info(f"Listening on {self.listen_topic.value} (DB-Backed)...")
        while True:
            try:
                # 阻塞读取消息
                messages = bus.consume(self.listen_topic, self.group_name, self.worker_name, count=1, block=5000)
                
                for msg in messages:
                    msg_id = msg["id"]
                    raw_payload = msg["payload"]
                    
                    # 预定义 task_id 方便异常处理
                    current_task_id = "unknown"

                    try:
                        # 1. 解析 Payload
                        data_dict = raw_payload if isinstance(raw_payload, dict) else json.loads(raw_payload)
                        payload = TaskPayload(**data_dict)
                        current_task_id = payload.task_id
                        self.logger.info(f"正在处理任务步骤: {payload.step}", task_id=payload.task_id)

                        #  == 死循环熔断保护：检查深度是否超过最大限制 ==
                        if payload.depth > MAX_STEPS:
                            self.logger.error("超过最大步数限制", task_id=payload.task_id, depth=payload.depth)
                            bus.ack(self.listen_topic, self.group_name, msg_id)
                            continue
                        #  ============================================
                        
                        print(f"📥 [{self.__class__.__name__}] 收到任务: {payload.task_id} (步骤: {payload.step})")

                        # 2. 执行业务 (由子类实现)
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
                        # === 使用 ErrorHandler 接管异常 ===
                        decision = worker_error_handler.analyze(e, component=self.__class__.__name__, task_id=current_task_id)
                        
                        # 如果是解析错误或代码错误，ACK 掉防止死循环重试
                        if decision == "SKIP":
                            self.logger.warning("跳过格式错误任务", task_id=current_task_id)
                            bus.ack(self.listen_topic, self.group_name, msg_id)

            except KeyboardInterrupt:
                self.logger.info("🛑 收到停止信号，正在停止...")
                break
            except Exception as outer_e:
                # 捕获 consume 本身的错误（如 Redis 断连）
                worker_error_handler.analyze(outer_e, component="BaseWorkerLoop")

    @abstractmethod
    def process(self, payload: TaskPayload) -> TaskPayload:
        """业务逻辑，返回传递给下一个 Agent 的 Payload"""
        pass