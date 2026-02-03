from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.app.core.request_id import get_request_id


def _error_response(*, status_code: int, code: int, message: str, result: Any = None) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "code": code,
            "message": message,
            "result": result,
            "request_id": get_request_id(),
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        status_code = int(exc.status_code)
        detail = exc.detail if isinstance(exc.detail, str) else None

        if status_code == 401:
            return _error_response(
                status_code=401,
                code=10032,
                message=detail or "未经许可授权",
            )
        if status_code == 403:
            return _error_response(
                status_code=403,
                code=10033,
                message=detail or "失败！当前访问没有权限，或操作的数据没权限!",
            )
        if status_code == 404:
            return _error_response(status_code=404, code=10034, message=detail or "访问地址不存在")

        return _error_response(
            status_code=status_code,
            code=status_code,
            message=detail or "请求失败",
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(request: Request, exc: RequestValidationError):
        return _error_response(
            status_code=422,
            code=10031,
            message="参数校验错误,请检查提交的参数信息",
            result={"detail": exc.errors()},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        return _error_response(status_code=500, code=50000, message="系统崩溃了")

