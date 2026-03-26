# -*- coding: utf-8 -*-
"""
TCP Socket 监听与多线程调度中心
负责网络底层通信，管理客户端连接的接收与分发。
"""
import socket
import threading
from src.config import DEFAULT_HOST, DEFAULT_PORT, MAX_CONNECTIONS, BUFFER_SIZE, MIME_TYPES
from src.logger import logger
from src.http_parser import parse_request
from src.http_response import handle_request, build_http_response

class WebServer:
    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT):
        self.host = host
        self.port = port
        self.server_socket = None
        self.is_running = False
        self.threads = []  # 用于记录当前活动的客户端处理线程

    def start(self):
        """启动服务器监听主循环"""
        try:
            # 1. 创建 TCP 套接字
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # 设置端口复用，防止重启服务器时提示 "Address already in use" (写报告绝佳素材)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # 2. 绑定 IP 和端口
            self.server_socket.bind((self.host, self.port))
            
            # 3. 开始监听
            self.server_socket.listen(MAX_CONNECTIONS)
            self.is_running = True
            
            # 核心容错设计：设置超时时间为 1 秒。
            # 这样 accept() 不会一直死等，每秒醒来一次检查 is_running 标志，
            # 从而允许 GUI 界面优雅地随时关闭服务器，避免死循环或线程卡死。
            self.server_socket.settimeout(1.0)
            
            logger.info(f"服务器已启动，正在监听 {self.host}:{self.port}")
            
            # 4. 主循环：接收客户端连接
            while self.is_running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    logger.debug(f"接收到来自 {client_address} 的连接")
                    
                    # 【核心要求】：每当接收到一个新连接，创建一个独立线程处理
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address),
                        name=f"Thread-{client_address[1]}"  # 用客户端端口号命名线程，方便日志追踪
                    )
                    client_thread.daemon = True  # 设置为守护线程，主线程退出时自动销毁
                    client_thread.start()
                    
                    # 简单记录活动的线程 (可选清理已完成的线程以防内存泄漏)
                    self.threads = [t for t in self.threads if t.is_alive()]
                    self.threads.append(client_thread)
                    
                except socket.timeout:
                    # 这是正常的，1秒没收到连接就超时，继续下一轮 while 循环检查 is_running
                    continue
                except Exception as e:
                    if self.is_running:
                        logger.error(f"接收连接时发生异常: {e}")
                        
        except Exception as e:
            logger.critical(f"服务器启动失败: {e}")
            self.is_running = False
        finally:
            self.stop()

    def stop(self):
        """停止服务器，释放资源"""
        if self.is_running:
            logger.info("正在关闭服务器...")
            self.is_running = False
            if self.server_socket:
                try:
                    self.server_socket.close()
                except Exception as e:
                    logger.error(f"关闭 Socket 时出错: {e}")
            logger.info("服务器已停止。")

    def handle_client(self, client_socket, client_address):
        """
        处理单个客户端连接的线程函数
        """
        try:
            # 1. 接收客户端发来的原始请求字节流
            # 为了能解析完整的请求头，读取直到遇到空行（\r\n\r\n）或达到最大大小
            client_socket.settimeout(2.0)
            request_data = b""
            max_request_size = BUFFER_SIZE * 16  # 简单的防御，避免请求头无限增长
            while b"\r\n\r\n" not in request_data and len(request_data) < max_request_size:
                chunk = client_socket.recv(BUFFER_SIZE)
                if not chunk:
                    break
                request_data += chunk
            
            if not request_data:
                logger.debug(f"客户端 {client_address} 关闭了连接")
                return

            # 2. 解析 HTTP 请求
            parsed_req = parse_request(request_data)
            
            if parsed_req.is_valid:
                # 3. 根据解析结果，获取响应报文
                status_code, response_data = handle_request(parsed_req.method, parsed_req.url)
                
                # 4. 将响应数据通过 Socket 发送回客户端
                client_socket.sendall(response_data)
                logger.info(f"{client_address[0]} - {parsed_req.method} {parsed_req.url} - {status_code}")
            else:
                url_display = parsed_req.url if parsed_req.url else "-"
                logger.warning(f"接收到无效的 HTTP 请求来自 {client_address}: {url_display}")

                # 向客户端返回一个明确的 400，避免客户端等待超时
                error_msg = "<h1>400 Bad Request</h1><p>Bad Request.</p>"
                response_data = build_http_response(400, error_msg.encode("utf-8"), MIME_TYPES[".html"])
                client_socket.sendall(response_data)
                logger.info(f"ACCESS client={client_address[0]} url={url_display} status=400")

        except socket.timeout:
            logger.debug(f"客户端 {client_address} 连接超时 (通常是浏览器的空闲预连接)")
        except ConnectionResetError:
            logger.warning(f"客户端 {client_address} 强制断开了连接")
        except Exception as e:
            logger.error(f"处理客户端 {client_address} 时发生未捕获异常: {e}")
        finally:
            # 无论发生什么，确保关闭客户端套接字释放系统资源
            try:
                client_socket.close()
                logger.debug(f"已关闭与 {client_address} 的连接")
            except Exception:
                pass