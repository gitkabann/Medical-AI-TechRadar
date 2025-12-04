import os
import threading
import time
from uuid import uuid4

# === 开启混沌模式 ===
os.environ["ENABLE_CHAOS"] = "true"
# ===================

from app.core.event_bus import bus, Topic
from app.models.protocol import TaskPayload
from app.workers.agents import PlannerAgent, CrawlerAgent, RagAgent, WriterAgent

def start_worker(agent_cls):
    # 简单的 worker 启动封装
    w = agent_cls()
    w.run()

def main():
    print("🔥 启动混沌测试 (Failure Injection Mode) ...")
    print("   Crawler 将面临 50% 的网络故障概率")
    
    # 启动 Workers
    for cls in [PlannerAgent, CrawlerAgent, RagAgent, WriterAgent]:
        threading.Thread(target=start_worker, args=(cls,), daemon=True).start()
    
    time.sleep(2)
    
    # 发送任务
    task_id = str(uuid4())
    topic = "lung nodule detection"
    
    print(f"\n📨 [Chaos] 发送任务: {topic}")
    bus.publish(Topic.PLANNER, TaskPayload(
        task_id=task_id, 
        topic=topic, 
        step="init"
    ).model_dump())

    # 保持运行观察
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()