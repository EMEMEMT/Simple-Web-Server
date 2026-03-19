# -*- coding: utf-8 -*-
"""
HTTP 请求报文解析器
负责将 Socket 接收到的原始字节流转换为结构化的 HTTP 请求信息。
"""
from src.logger import logger

class HTTPRequest:
    def __init__(self):
        self.method = ""
        self.url = ""
        self.version = ""
        self.headers = {}
        self.body = ""
        self.is_valid = False

def parse_request(raw_data: bytes) -> HTTPRequest:
    """
    解析 HTTP 请求报文
    :param raw_data: 从 Socket 接收到的 bytes 数据
    :return: HTTPRequest 实例
    """
    req = HTTPRequest()
    
    if not raw_data:
        return req

    try:
        # HTTP 报文通常使用 utf-8 或 latin-1 编码
        decoded_data = raw_data.decode('utf-8', errors='ignore')
        
        # HTTP 报文头部和请求体之间由一个空行 (\r\n\r\n) 分隔
        parts = decoded_data.split('\r\n\r\n', 1)
        header_part = parts[0]
        if len(parts) > 1:
            req.body = parts[1]

        # 解析头部行
        lines = header_part.split('\r\n')
        if not lines:
            return req

        # 1. 解析请求行 (Request Line): 例如 "GET /index.html HTTP/1.1"
        request_line = lines[0].split(' ')
        if len(request_line) >= 3:
            req.method = request_line[0]
            req.url = request_line[1]
            req.version = request_line[2]
            req.is_valid = True
        else:
            logger.warning(f"无法解析请求行: {lines[0]}")
            return req

        # 2. 解析请求头 (Headers)
        for line in lines[1:]:
            if ':' in line:
                key, value = line.split(':', 1)
                req.headers[key.strip()] = value.strip()

        logger.debug(f"成功解析请求: {req.method} {req.url} {req.version}")
        return req

    except Exception as e:
        logger.error(f"解析 HTTP 请求时发生异常: {e}")
        return req