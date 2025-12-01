import time
from uuid import uuid4
from app.core.event_bus import bus, Topic
from app.core.orchestrator import orchestrator

def test_streams_flow():
    print("🚀 开始 Redis Streams 测试...")
    
    # 1. 模拟用户创建一个任务
    task_id = str(uuid4())
    topic = "肺结节检测"
    orchestrator.create_task(task_id, topic, {"depth": "shallow"})
    
    # 2. 验证状态是否已写入 Redis
    status = orchestrator.get_task_status(task_id)
    print(f"📊 当前任务状态: {status['status']} (Expect: RUNNING)")

    # 3. 模拟 Worker 消费消息 (Crawler)
    print("👷 模拟 Worker 正在监听 stream:crawler...")
    messages = bus.consume(Topic.CRAWLER, "group_orchestrator", "worker_1", count=1, block=3000)
    
    if messages:
        msg = messages[0]
        print(f"📥 Worker 收到消息: {msg}")
        
        payload = msg['payload']
        assert payload['task_id'] == task_id
        print("✅ 消息内容校验通过！")
        
        # 4. 模拟 Worker 处理完成并 ACK
        bus.ack(Topic.CRAWLER, "group_orchestrator", msg['id'])
        print("✅ 消息已 ACK")
        
    else:
        print("❌ 未收到消息！(请检查 Redis 是否启动)")

if __name__ == "__main__":
    try:
        test_streams_flow()
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        print("💡 提示: 请确保 Docker 容器 'medical-redis' 正在运行 (端口 6379)。")