import threading
import time
from uuid import uuid4
from app.core.event_bus import bus, Topic
from app.models.protocol import TaskPayload
from app.workers.agents import PlannerAgent, CrawlerAgent, RagAgent, WriterAgent

def start_worker(agent_cls):
    worker = agent_cls()
    worker.run()

def main():
    print("🚀 正在启动 Medical AI Agent System (多进程模拟)...")
    
    # 1. 启动所有 Worker (在独立线程中)
    agents = [PlannerAgent, CrawlerAgent, RagAgent, WriterAgent]
    threads = []
    
    for cls in agents:
        t = threading.Thread(target=start_worker, args=(cls,), daemon=True)
        t.start()
        threads.append(t)
        
    time.sleep(2) # 等待 Worker 就绪
    
    # 2. 发送一个测试任务
    task_id = str(uuid4())
    topic = "brain tumor detection"
    
    initial_payload = TaskPayload(
        task_id=task_id,
        topic=topic,
        step="init",
        params={"depth": "deep"}
    )
    
    print(f"\n📨 [System] 用户提交任务: {topic} (ID: {task_id})")
    bus.publish(Topic.PLANNER, initial_payload.model_dump())
    
    # 3. 阻塞主线程，观察日志
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("停止系统...")

if __name__ == "__main__":
    main()