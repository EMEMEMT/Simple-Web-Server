# -*- coding: utf-8 -*-
import logging
import sys

def setup_logger(name="WebServerLogger"):
    # 配置并返回一个线程安全的全局日志记录器。

    logger = logging.getLogger(name)
    
    # 防止重复添加 Handler 导致日志重复打印
    if not logger.handlers:
        logger.setLevel(logging.INFO) # 设置最低日志级别为 DEBUG
        
        # 定义日志输出格式：[时间] [线程名] [级别] 日志内容
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
logger = setup_logger()