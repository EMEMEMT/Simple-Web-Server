# -*- coding: utf-8 -*-
"""
HTTP 响应报文构造器
负责读取本地文件，并按照 HTTP/1.1 规范组装响应报文。
"""
import os
from datetime import datetime
from src.config import WEB_ROOT, HTTP_VERSION, SERVER_NAME, STATUS_CODES, MIME_TYPES
from src.logger import logger

def get_mime_type(file_path: str) -> str:
    """根据文件后缀获取 MIME 类型"""
    ext = os.path.splitext(file_path)[1].lower()
    return MIME_TYPES.get(ext, MIME_TYPES['default'])

def build_http_response(status_code: int, content: bytes, mime_type: str) -> bytes:
    """
    构造完整的 HTTP 响应报文
    :param status_code: HTTP 状态码 (200, 404, 501 等)
    :param content: 响应体 (文件的二进制内容)
    :param mime_type: Content-Type
    :return: 准备通过 Socket 发送的 bytes
    """
    status_text = STATUS_CODES.get(status_code, "Unknown Status")
    
    # 1. 构造状态行
    response_line = f"{HTTP_VERSION} {status_code} {status_text}\r\n"
    
    # 2. 构造响应头
    # 格式化时间，遵循 HTTP 协议标准的 GMT 时间格式
    now_gmt = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    headers = [
        f"Server: {SERVER_NAME}",
        f"Date: {now_gmt}",
        f"Content-Type: {mime_type}",
        f"Content-Length: {len(content)}",
        "Connection: close" # 课设通常实现短连接即可
    ]
    header_block = "\r\n".join(headers) + "\r\n\r\n"
    
    # 3. 拼接并编码
    # 注意：状态行和 Header 必须用 ASCII/UTF-8 编码为 bytes，然后再与文件的纯二进制数据拼接
    full_response = response_line.encode('utf-8') + header_block.encode('utf-8') + content
    return full_response

def handle_request(method: str, url: str):
    """
    处理客户端请求，读取文件并返回构造好的响应流
    :param method: 请求方法 (GET, POST等)
    :param url: 请求的路径 (如 /index.html)
    :return: (status_code, response_bytes)
    """
    # NOTE:
    # 为了让上层能够在访问日志中打印响应状态码，这里返回 (status_code, response_bytes)
    # 而不是只返回 bytes。
    #
    # （保持对外部调用的最小改动：仅 `src/server_core.py` 会用到返回值）

    # 1. 处理非 GET 请求 (对应任务书：若请求方法不是GET，返回 501)
    if method != 'GET':
        logger.warning(f"不支持的请求方法: {method}")
        error_msg = "<h1>501 Not Implemented</h1><p>The requested method is not supported by this server.</p>"
        response = build_http_response(501, error_msg.encode('utf-8'), MIME_TYPES['.html'])
        return 501, response

    # 2. 处理 URL 路径映射
    if url == '/':
        url = '/index.html'
    
    # 去除 URL 参数 (例如 /index.html?a=1 变成 /index.html)
    url = url.split('?')[0]
    
    # 构建本地绝对路径
    # 注意：在 Windows 上路径分隔符是 \，URL 里是 /，需要做转换
    web_root_abs = os.path.abspath(WEB_ROOT)
    local_path = os.path.abspath(os.path.join(web_root_abs, url.lstrip('/')))

    # 安全防护：防止路径穿越攻击 (Directory Traversal) 比如请求 /../../../etc/password
    # 使用 "前缀 + 分隔符" 避免像 C:\\webroot2 这样的前缀误匹配。
    if not (local_path == web_root_abs or local_path.startswith(web_root_abs + os.sep)):
        logger.warning(f"检测到非法路径访问尝试: {url}")
        error_msg = "<h1>403 Forbidden</h1>"
        response = build_http_response(403, error_msg.encode('utf-8'), MIME_TYPES['.html'])
        return 403, response

    # 3. 尝试读取文件
    try:
        with open(local_path, 'rb') as f: # 必须以 'rb' 二进制模式读取，才能兼容图片和视频
            content = f.read()
            mime_type = get_mime_type(local_path)
            logger.debug(f"成功读取本地文件: {local_path} ({mime_type})")
            response = build_http_response(200, content, mime_type)
            return 200, response
            
    except FileNotFoundError:
        # 对应任务书：文件不存在返回 404
        logger.error(f"404 Not Found: 文件不存在 {local_path}")
        # 尝试寻找 webroot 下自定义的 404.html
        custom_404_path = os.path.join(WEB_ROOT, '404.html')
        if os.path.exists(custom_404_path):
            with open(custom_404_path, 'rb') as f:
                response = build_http_response(404, f.read(), MIME_TYPES['.html'])
                return 404, response
        else:
            # 如果没有自定义页面，返回默认字符串
            fallback_msg = "<h1>404 Not Found</h1><p>The requested URL was not found on this server.</p>"
            response = build_http_response(404, fallback_msg.encode('utf-8'), MIME_TYPES['.html'])
            return 404, response
            
    except Exception as e:
        logger.error(f"读取文件发生服务器内部错误: {e}")
        error_msg = "<h1>500 Internal Server Error</h1>"
        response = build_http_response(500, error_msg.encode('utf-8'), MIME_TYPES['.html'])
        return 500, response