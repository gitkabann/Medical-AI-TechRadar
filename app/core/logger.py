import logging  # Python 自带的日志模块

def get_logger(name: str):
    """
    获取（或创建）一个模块专属的日志记录器。
    参数:
        name: 通常传 __name__，表示当前模块名，用于区分日志来源。
    返回:
        一个配置好输出格式和级别的 logger 对象，可直接 logger.info()/warning()/error() 使用。
    """
    
    # 根据模块名获取 logger 对象（如果该名字的 logger 已存在，会返回同一个实例）
    logger = logging.getLogger(name)
    
    # 防止重复添加 handler（否则会导致日志重复打印）
    if not logger.handlers:
        # 创建一个“输出到控制台”的日志处理器（StreamHandler）
        handler = logging.StreamHandler()
        
        # 定义日志格式：
        # %(asctime)s  → 打印时间
        # %(levelname)s → 日志级别（INFO/WARNING/ERROR）
        # %(name)s      → 模块名（即传入的 name）
        # %(message)s   → 实际日志内容
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )
        
        # 把格式应用到 handler 上
        handler.setFormatter(formatter)
        
        # 把 handler 加入 logger（告诉 logger 要把日志输出到控制台）
        logger.addHandler(handler)
        
        # 设置日志等级为 INFO（只显示 INFO 及以上的日志）
        logger.setLevel(logging.INFO)
    
    # 返回这个配置好的 logger
    return logger
