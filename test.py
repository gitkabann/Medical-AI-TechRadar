import time
import random

def process_item(item):
    # 模拟耗时操作
    print(f"处理中：{item}")
    process_time = random.uniform(0.5, 2.0)
    time.sleep(process_time)
    return f"处理完成：{item}，耗时 {process_time:.2f} 秒"

def process_all_items():
    items = ["任务A", "任务B", "任务C", "任务D"]
    results = []
    for item in items:
        result = process_item(item)
        results.append(result)
    return results

if __name__ == "__main__":
    start = time.time()
    results = process_all_items()
    end = time.time()
    
    print("\n".join(results))
    print(f"总耗时：{end - start:.2f} 秒")