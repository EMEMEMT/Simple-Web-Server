# main_headless.py
from src.server_core import WebServer
from src.logger import logger

if __name__ == "__main__":
    # 可以在这里修改端口，默认是 config 里的 8080
    port = 8080 
    server = WebServer(port=port)
    
    try:
        logger.info(f"正在无图形界面模式下启动服务器...")
        server.start()
    except KeyboardInterrupt:
        # 按 Ctrl+C 可以退出
        logger.info("\n接收到退出信号，正在停止服务器...")
        server.stop()