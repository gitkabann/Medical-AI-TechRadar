import time
import random
import asyncio
async def process_item(item):
    # 模拟耗时操作
    print(f"处理中：{item}")
    process_time = random.uniform(0.5, 2.0)
    await asyncio.sleep(process_time)
    print(f"处理完成：{item}，耗时 {process_time:.2f} 秒")

async def process_all_items():
    items = ["任务A", "任务B", "任务C", "任务D"]
    tasks = asyncio.gather(*[process_item(item) for item in items])
    await tasks

start = time.time()
asyncio.run(process_all_items())
end = time.time()

print(f"总耗时：{end - start:.2f} 秒")