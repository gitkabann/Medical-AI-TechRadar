import threading
import time
from uuid import uuid4
from app.core.event_bus import bus, Topic
from app.models.protocol import TaskPayload
from app.workers.agents import PlannerAgent, CrawlerAgent, RagAgent, WriterAgent
from typing import List, Type # 引入 Type 用于类型提示

def start_worker(agent_cls: Type):
    """启动一个 Worker 实例并运行其主循环。"""
    worker = agent_cls()
    worker.run()

def main():
    print("🚀 正在启动 Medical AI Agent Workers (后台监听中)...")
    print("👂 等待前端 UI 提交任务...")
    
    # 1. 启动所有 Worker (在独立线程中)
    agents: List[Type] = [PlannerAgent, CrawlerAgent, RagAgent, WriterAgent]
    threads = []
    
    for cls in agents:
        # daemon=True 保证主线程退出时，worker 线程也会退出
        t = threading.Thread(target=start_worker, args=(cls,), daemon=True)
        t.start()
        threads.append(t)
        
    # 死循环挂起主线程，保持 Agent 存活
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("停止系统...")
    
    # --- 2. 发送测试任务 ---

    # # 2.1. 测试 Light 模式 (应该很快，且不抓 Trials)
    # task_id_1 = str(uuid4())
    # topic_1 = "covid-19 detection"
    
    # print(f"\n📨 [System] 提交 Light 任务: '{topic_1}' (ID: {task_id_1})")
    
    # initial_payload_1 = TaskPayload(
    #     task_id=task_id_1,
    #     topic=topic_1,
    #     step="init",
    #     params={"depth": "light"}  # <--- Light 模式参数
    # )
    # bus.publish(Topic.PLANNER, initial_payload_1.model_dump())

    # # 等待 Light 模式任务处理一段时间
    # time.sleep(10) 

    # 2.2. 测试 Deep 模式 (抓取更多，且包含 Trials)
    # task_id_2 = str(uuid4())
    # topic_2 = "polyp segmentation"
    
    # print(f"\n📨 [System] 提交 Deep 任务: '{topic_2}' (ID: {task_id_2})")
    
    # initial_payload_2 = TaskPayload(
    #     task_id=task_id_2,
    #     topic=topic_2,
    #     step="init",
    #     params={"depth": "deep"}  # <--- Deep 模式参数
    # )
    # bus.publish(Topic.PLANNER, initial_payload_2.model_dump())

    # # 3. 阻塞主线程，观察日志
    # print("\nSystem running. Press Ctrl+C to stop...")
    # try:
    #     while True:
    #         time.sleep(1)
    # except KeyboardInterrupt:
    #     print("\n🛑 停止系统...")

if __name__ == "__main__":
    main()