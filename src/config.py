# -*- coding: utf-8 -*-
import os

# 获取项目根目录 (config.py 上级目录的上一级)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 静态资源根目录 (浏览器请求的根目录)
WEB_ROOT = os.path.join(BASE_DIR, 'webroot')

# 服务器默认网络配置
DEFAULT_HOST = '0.0.0.0'  # 监听所有网卡
DEFAULT_PORT = 8080       # 默认监听端口
MAX_CONNECTIONS = 100     # 最大排队连接数
BUFFER_SIZE = 4096        # Socket 接收缓冲区大小 (4KB)

# HTTP 协议相关配置
HTTP_VERSION = 'HTTP/1.1'
SERVER_NAME = 'Simple-Web-Server/1.0 (Python)'

# HTTP 状态码及描述
STATUS_CODES = {
    200: 'OK',
    404: 'Not Found',
    501: 'Not Implemented'
}

# MIME 类型字典 (用于 Content-Type 响应头)
MIME_TYPES = {
    # 文本与前端资源
    '.html': 'text/html; charset=utf-8',
    '.htm': 'text/html; charset=utf-8',
    '.txt': 'text/plain; charset=utf-8',
    '.css': 'text/css; charset=utf-8',
    '.js': 'application/javascript; charset=utf-8',
    '.json': 'application/json; charset=utf-8',
    
    # 图片文件 (支持预览)
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.gif': 'image/gif',
    '.ico': 'image/x-icon',
    
    # 视频文件 (支持在线播放)
    '.mp4': 'video/mp4',
    '.webm': 'video/webm',
    
    # 默认二进制流
    'default': 'application/octet-stream'
}