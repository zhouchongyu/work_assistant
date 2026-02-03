import json
import time
import uuid
from typing import Callable, Awaitable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from app.core.config.settings import settings
import logging
from logging.handlers import RotatingFileHandler
import os
from pythonjsonlogger import jsonlogger
import traceback
from pydantic import BaseModel


class CustomLogger(logging.Logger):
    """自定义日志记录器"""
    def __init__(self, name: str):
        super().__init__(name)

    def info(self, msg, *args, **kwargs):
        kwargs['extra'] = kwargs.get('extra') or {}
        extra = {}
        kwargs['extra'].update(extra)
        super().info(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        kwargs['extra'] = kwargs.get('extra') or {}
        extra = {}
        kwargs['extra'].update(extra)
        super().error(msg, *args, **kwargs)


# 创建日志目录
log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory, exist_ok=True)

# 创建文件处理器
file_handler = RotatingFileHandler(
    filename=os.path.join(log_directory, "app.log"),
    maxBytes=10 * 1024 * 1024,  # 10 MB
    backupCount=5,
)
file_handler.setLevel(logging.DEBUG)

# 配置日志记录器
logger = CustomLogger("work_assistant_log")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.addHandler(file_handler)


class RequestLoggingMiddleware:
    """请求日志中间件，实现全链路 request_id 追踪"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        request = Request(scope)

        # 获取或生成 request_id
        request_id = request.headers.get(settings.REQUEST_ID_HEADER) or str(uuid.uuid4())

        # 添加 request_id 到请求状态，以便在后续处理中使用
        request.state.request_id = request_id

        start_time = time.time()

        # 记录请求开始
        logger.info(
            "Request started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": str(request.url),
                "headers": dict(request.headers),
            }
        )

        # 捕获响应
        response_body = b""

        async def send_wrapper(message):
            if message["type"] == "http.response.body":
                nonlocal response_body
                response_body += message.get("body", b"")

            # 在响应头中添加 request_id
            if message["type"] == "http.response.start":
                headers = message.get("headers", [])
                headers.append((settings.REQUEST_ID_HEADER.encode(), request_id.encode()))
                message["headers"] = headers

            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Unhandled exception in request: {str(e)}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": str(request.url),
                    "duration": duration,
                    "exception": traceback.format_exc(),
                }
            )
            # 发送错误响应
            response = JSONResponse(
                status_code=500,
                content={
                    "message": "Internal Server Error",
                    "code": 500,
                    "request_id": request_id
                }
            )
            await response(scope, receive, send)
        else:
            duration = time.time() - start_time
            # 记录请求结束
            try:
                response_content = json.loads(response_body.decode()) if response_body else {}
                response_code = response_content.get("code", 200)
            except json.JSONDecodeError:
                response_code = 200

            logger.info(
                "Request completed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": str(request.url),
                    "status_code": response_code,
                    "duration": duration,
                }
            )


def get_request_id():
    """获取当前请求的 request_id（如果在请求上下文中）"""
    # 这个函数可以在依赖项或其他地方使用
    # 但在中间件中我们直接通过 request.state 访问
    pass