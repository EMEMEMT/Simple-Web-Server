# -*- coding: utf-8 -*-
"""
Web 服务器图形用户界面 (GUI)
负责展示控制面板、接收用户配置、控制后台服务器启停，并安全地实时展示日志。
"""
import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import queue
import logging
from src.server_core import WebServer
from src.config import DEFAULT_PORT
from src.logger import logger

class QueueLogHandler(logging.Handler):
    """
    自定义的日志处理器 (Handler)。
    作用：拦截系统的日志输出，将其放入一个线程安全的队列中，供前端 GUI 消费。
    """
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        # 格式化日志内容
        log_entry = self.format(record)
        # 放入队列
        self.log_queue.put(log_entry)

class WebServerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Simple Web Server 控制台 - 计算机网络课程设计")
        self.root.geometry("750x500")
        self.root.configure(padx=10, pady=10)
        
        # 拦截窗口关闭事件，确保安全退出
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 核心：用于跨线程安全通信的消息队列
        self.log_queue = queue.Queue()
        self.setup_logging_queue()

        self.server = None
        self.server_thread = None

        self.create_widgets()

    def setup_logging_queue(self):
        """将日志输出重定向到队列中"""
        queue_handler = QueueLogHandler(self.log_queue)
        formatter = logging.Formatter(
            fmt='[%(asctime)s] %(levelname)s: %(message)s',
            datefmt='%H:%M:%S'
        )
        queue_handler.setFormatter(formatter)
        logger.addHandler(queue_handler)

    def create_widgets(self):
        """创建界面组件"""
        # ================= 控制区 (Top Frame) =================
        control_frame = tk.Frame(self.root)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(control_frame, text="监听端口:", font=("Arial", 11)).pack(side=tk.LEFT, padx=(0, 5))
        
        self.port_entry = tk.Entry(control_frame, width=10, font=("Arial", 11))
        self.port_entry.insert(0, str(DEFAULT_PORT))
        self.port_entry.pack(side=tk.LEFT, padx=(0, 20))

        self.start_btn = tk.Button(control_frame, text="▶ 启动服务器", bg="#4CAF50", fg="white", 
                                   font=("Arial", 10, "bold"), command=self.start_server)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = tk.Button(control_frame, text="⏹ 停止服务器", bg="#F44336", fg="white", 
                                  font=("Arial", 10, "bold"), state=tk.DISABLED, command=self.stop_server)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        tk.Label(control_frame, text="状态: ", font=("Arial", 11)).pack(side=tk.LEFT, padx=(30, 0))
        self.status_label = tk.Label(control_frame, text="已停止", fg="red", font=("Arial", 11, "bold"))
        self.status_label.pack(side=tk.LEFT)

        # ================= 日志区 (Bottom Frame) =================
        log_frame = tk.Frame(self.root)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(log_frame, text="实时访问日志:", font=("Arial", 10, "bold")).pack(anchor=tk.W)

        self.log_text = scrolledtext.ScrolledText(log_frame, state=tk.DISABLED, bg="#1E1E1E", fg="#00FF00", font=("Consolas", 10))
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

    def start_server(self):
        """启动服务器逻辑"""
        port_str = self.port_entry.get().strip()
        if not port_str.isdigit() or not (1 <= int(port_str) <= 65535):
            messagebox.showerror("错误", "请输入有效的端口号 (1-65535)！")
            return

        port = int(port_str)
        
        # 实例化服务器对象
        self.server = WebServer(port=port)
        
        # 在独立的后台线程中运行服务器的主循环，防止阻塞 GUI 界面
        self.server_thread = threading.Thread(target=self.server.start, daemon=True)
        self.server_thread.start()

        # 更新 UI 状态
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.port_entry.config(state=tk.DISABLED)
        self.status_label.config(text=f"运行中 (Port: {port})", fg="green")

    def stop_server(self):
        """停止服务器逻辑"""
        if self.server:
            self.server.stop()
            self.server = None

        # 更新 UI 状态
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.port_entry.config(state=tk.NORMAL)
        self.status_label.config(text="已停止", fg="red")

    def poll_log_queue(self):
        """
        核心机制：定时轮询消息队列
        每隔 100 毫秒检查一次队列中是否有新的日志，如果有则更新到 Text 组件中。
        """
        while not self.log_queue.empty():
            try:
                msg = self.log_queue.get_nowait()
                self.log_text.config(state=tk.NORMAL)
                self.log_text.insert(tk.END, msg + "\n")
                self.log_text.see(tk.END) # 自动滚动到最底部
                self.log_text.config(state=tk.DISABLED)
            except queue.Empty:
                break
        
        # Tkinter 的 after 方法：在 100ms 后再次调用自己，形成非阻塞的死循环
        self.root.after(100, self.poll_log_queue)

    def on_closing(self):
        """窗口关闭时的清理工作"""
        if self.server and self.server.is_running:
            self.stop_server()
        self.root.destroy()

    def run(self):
        """启动 GUI 主事件循环"""
        # 启动日志轮询定时器
        self.root.after(100, self.poll_log_queue)
        logger.info("系统初始化完成，等待启动服务器...")
        self.root.mainloop()