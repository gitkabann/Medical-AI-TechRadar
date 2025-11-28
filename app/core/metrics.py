# app/core/metrics.py
import time
from collections import defaultdict
from contextlib import contextmanager
from typing import Dict, Any

class MetricsTracker:
    def __init__(self):
        self.metrics: Dict[str, Any] = defaultdict(lambda: {"count": 0, "success": 0, "fail": 0, "total_time": 0.0})
        self.pipeline_start = 0.0

    def start_pipeline(self):
        self.pipeline_start = time.time()

    def end_pipeline(self):
        return time.time() - self.pipeline_start

    @contextmanager
    def track(self, component_name: str):
        """上下文管理器：自动记录耗时与成功/失败状态"""
        start = time.time()
        try:
            # yield 前的代码是进入逻辑 (__enter__)，yield 后的代码是退出逻辑 (__exit__)。
            # 执行到 yield 时，函数暂停，允许用户执行 with tracker.track(...) 块内的代码。
            yield 
            duration = time.time() - start
            self.record_success(component_name, duration)
        except Exception as e:
            duration = time.time() - start
            self.record_fail(component_name, duration)
            raise e  # 抛出异常供上层处理

    def record_success(self, component: str, duration: float):
        self.metrics[component]["count"] += 1
        self.metrics[component]["success"] += 1
        self.metrics[component]["total_time"] += duration

    def record_fail(self, component: str, duration: float):
        self.metrics[component]["count"] += 1
        self.metrics[component]["fail"] += 1
        self.metrics[component]["total_time"] += duration

    def report(self):
        """打印简单的文本报告"""
        print("\n" + "="*50)
        print(f"📊 性能指标报告 (Total: {self.end_pipeline():.2f}s)")
        print("="*50)
        print(f"{'组件':<15} | {'耗时(s)':<10} | {'状态 (✅/❌)'}")
        print("-" * 50)
        
        for name, data in self.metrics.items():
            avg_time = data["total_time"] / data["count"] if data["count"] > 0 else 0
            status = f"{data['success']} / {data['fail']}"
            print(f"{name:<15} | {avg_time:<10.4f} | {status}")
        print("="*50 + "\n")

# 全局单例
tracker = MetricsTracker()