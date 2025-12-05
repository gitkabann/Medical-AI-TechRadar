import logging
import sys
# import json # JSON 模块用于生产环境的结构化输出
from datetime import datetime

class StructuredLogger:
    """
    结构化日志记录器类。
    封装了标准的 logging 模块，并实现了将日志消息转换为键值对结构的功能。
    """
    def __init__(self, name: str):
        """
        初始化日志记录器。执行标准配置，但保留传统的日志格式化器。
        
        参数:
            name: 通常是模块名 __name__。
        """
        # 1. 获取 Logger 实例：如果该名字的 logger 已存在，则返回同一实例。
        self.logger = logging.getLogger(name)
        # 2. 设置日志级别：设置 INFO 级别，只记录 INFO 及以上的日志。
        self.logger.setLevel(logging.INFO)
        # 3. 存储模块名
        self.name = name
        
        # 4. 避免重复添加 Handler
        if not self.logger.handlers:
            # 创建 StreamHandler：指定日志输出到标准输出流（控制台）。
            handler = logging.StreamHandler(sys.stdout)
            
            # 定义日志格式：使用传统的文本格式，我们只改变 %(message)s 的内容。
            formatter = logging.Formatter(
                '%(asctime)s | %(levelname)s | %(name)s | %(message)s'
            )
            
            # 应用格式和添加 Handler
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def _format_msg(self, msg: str, task_id: str = None, **kwargs):
        """
        核心方法：构造结构化日志消息的 Payload，并将其格式化为键值对字符串。
        
        参数:
            msg: 实际的、主要的日志内容。
            task_id: 可选的任务追踪 ID (Trace ID)。
            **kwargs: 任何需要附加到日志中的额外上下文信息。
            
        返回:
            一个格式化的字符串，形如 "主消息 [key=value key2=value2]"。
        """
        # 1. 初始化 Payload：将主消息和所有额外参数收集到一个字典中。
        payload = {
            "msg": msg,
            **kwargs # 展开所有 kwargs 到 payload 字典中
        }
        
        # 2. 添加追踪 ID：如果提供了 task_id，将其标准化为 trace_id 字段。
        if task_id:
            payload["trace_id"] = task_id
            
        # 生产环境的 JSON 格式化示例（目前注释掉）
        # return json.dumps(payload, ensure_ascii=False) 
        
        # 3. 开发友好格式（键值对格式）：
        # 遍历 payload 字典，排除 msg 字段，将剩余字段格式化为 "key=value" 字符串列表。
        extras = " ".join([f"{k}={v}" for k, v in payload.items() if k != "msg"])
        
        # 4. 拼接最终消息：将主消息和结构化信息拼接起来。
        # 如果有附加信息 (extras)，则以方括号包围并追加；否则只返回主消息。
        return f"{msg} [{extras}]" if extras else msg

    # --- 日志级别方法 (调用者接口) ---
    
    def info(self, msg: str, task_id: str = None, **kwargs):
        """记录 INFO 级别的结构化日志。"""
        # 调用 _format_msg 构造结构化消息，然后传给底层的 logger
        self.logger.info(self._format_msg(msg, task_id, **kwargs))

    def error(self, msg: str, task_id: str = None, exc_info=False, **kwargs):
        """
        记录 ERROR 级别的结构化日志。
        参数 exc_info=True 时会包含完整的堆栈追踪信息。
        """
        # 允许用户通过 exc_info=True 传入堆栈信息，此参数直接传递给底层 logger.error
        self.logger.error(self._format_msg(msg, task_id, **kwargs), exc_info=exc_info)

    def warning(self, msg: str, task_id: str = None, **kwargs):
        """记录 WARNING 级别的结构化日志。"""
        self.logger.warning(self._format_msg(msg, task_id, **kwargs))

# --- 工厂函数 ---
def get_logger(name: str):
    """
    公共工厂函数：用于实例化和获取 StructuredLogger 对象。
    用户在每个模块中调用此函数获取 Logger 实例。
    """
    return StructuredLogger(name)