# -*- coding: utf-8 -*-
import logging
import sys

def setup_logger(name="WebServerLogger"):
    """
    配置并返回一个线程安全的全局日志记录器。
    后期可以轻松扩展，将日志输出重定向到 GUI 的 Text 控件中。
    """
    logger = logging.getLogger(name)
    
    # 防止重复添加 Handler 导致日志重复打印
    if not logger.handlers:
        logger.setLevel(logging.INFO) # 设置最低日志级别为 DEBUG
        
        # 定义日志输出格式：[时间] [线程名] [级别] 日志内容
        # 这种格式对于多线程课设程序的调试和展示极其重要
        formatter = logging.Formatter(
            fmt='[%(asctime)s] [%(threadName)s] %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        
    return logger

# 实例化全局可用的 logger 对象
# 在其他文件中直接 `from src.logger import logger` 即可使用
logger = setup_logger()