# -*- coding: utf-8 -*-
"""
项目入口文件 (Entry Point)
遵循单一职责原则，本文件仅负责系统初始化和启动主 GUI 事件循环。
"""

import sys
import os

# 将项目根目录添加到系统路径，确保 src 目录可以被正确 import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.gui_main import WebServerGUI

def main():
    """
    主程序启动函数
    """
    print("="*50)
    print("  欢迎使用 Simple Web Server (计算机网络课设)  ")
    print("="*50)
    
    # 实例化并运行 GUI 主循环
    app = WebServerGUI()
    app.run()

if __name__ == "__main__":
    main()