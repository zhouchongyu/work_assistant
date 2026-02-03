from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from typing import Union
import traceback
from app.core.config.settings import settings
import json
import datetime
import decimal
import uuid
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from pydantic.main import BaseModel


class CJsonEncoder(json.JSONEncoder):
    """自定义JSON编码器，处理特殊类型"""
    def default(self, obj):
        if hasattr(obj, 'keys') and hasattr(obj, '__getitem__'):
            return dict(obj)
        elif isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, datetime.time):
            return obj.isoformat()
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        elif isinstance(obj, bytes):
            return str(obj, encoding='utf-8')
        elif isinstance(obj, BaseModel):
            return obj.dict()
        return json.JSONEncoder.default(self, obj)


class ApiException(Exception):
    """自定义API异常基类"""
    def __init__(self, code: int, message: str, status_code: int = 200, request_id: str = None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.request_id = request_id
        super().__init__(message)


class BusinessError(ApiException):
    """业务异常"""
    def __init__(self, message: str = "Business Error", code: int = 1001, request_id: str = None):
        super().__init__(code=code, message=message, status_code=200, request_id=request_id)


class ValidationError(ApiException):
    """参数校验异常"""
    def __init__(self, message: str = "Validation Error", code: int = 422, request_id: str = None):
        super().__init__(code=code, message=message, status_code=422, request_id=request_id)


class UnauthorizedError(ApiException):
    """未授权异常"""
    def __init__(self, message: str = "Unauthorized", code: int = 10032, request_id: str = None):
        super().__init__(code=code, message=message, status_code=401, request_id=request_id)


class ForbiddenError(ApiException):
    """禁止访问异常"""
    def __init__(self, message: str = "Forbidden", code: int = 10033, request_id: str = None):
        super().__init__(code=code, message=message, status_code=403, request_id=request_id)


class NotFoundError(ApiException):
    """未找到异常"""
    def __init__(self, message: str = "Not Found", code: int = 10034, request_id: str = None):
        super().__init__(code=code, message=message, status_code=404, request_id=request_id)


def create_response(code: int, message: str, result=None, request_id: str = None):
    """创建统一响应格式"""
    response_data = {
        "code": code,
        "message": message,
        "result": result,
    }
    
    if request_id:
        response_data["request_id"] = request_id
    
    return response_data


async def business_error_handler(request: Request, exc: BusinessError):
    """业务异常处理器"""
    request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))
    return JSONResponse(
        status_code=exc.status_code,
        content=create_response(exc.code, exc.message, request_id=request_id)
    )


async def unauthorized_error_handler(request: Request, exc: UnauthorizedError):
    """未授权异常处理器"""
    request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))
    return JSONResponse(
        status_code=exc.status_code,
        content=create_response(exc.code, exc.message, request_id=request_id)
    )


async def forbidden_error_handler(request: Request, exc: ForbiddenError):
    """禁止访问异常处理器"""
    request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))
    return JSONResponse(
        status_code=exc.status_code,
        content=create_response(exc.code, exc.message, request_id=request_id)
    )


async def validation_error_handler(request: Request, exc: RequestValidationError):
    """请求参数校验异常处理器"""
    request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))
    return JSONResponse(
        status_code=422,
        content=create_response(
            422, 
            "Validation Error", 
            {"detail": exc.errors()}, 
            request_id=request_id
        )
    )


async def sql_alchemy_error_handler(request: Request, exc: SQLAlchemyError):
    """数据库异常处理器"""
    request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))
    return JSONResponse(
        status_code=500,
        content=create_response(
            500, 
            "Database Error", 
            request_id=request_id
        )
    )


async def http_error_handler(request: Request, exc: StarletteHTTPException):
    """HTTP异常处理器"""
    request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))
    
    # 根据HTTP状态码返回相应的错误信息
    if exc.status_code == 404:
        return JSONResponse(
            status_code=200,
            content=create_response(10034, "Not Found", request_id=request_id)
        )
    elif exc.status_code == 405:
        return JSONResponse(
            status_code=200,
            content=create_response(10034, "Method Not Allowed", request_id=request_id)
        )
    elif exc.status_code == 429:
        return JSONResponse(
            status_code=429,
            content=create_response(429, "Rate Limit Exceeded", request_id=request_id)
        )
    else:
        return JSONResponse(
            status_code=exc.status_code,
            content=create_response(exc.status_code, exc.detail, request_id=request_id)
        )


async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理器"""
    request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))
    print(f"Exception occurred: {exc}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content=create_response(
            500, 
            "Internal Server Error", 
            request_id=request_id
        )
    )


def register_exception_handlers(app: FastAPI):
    """注册异常处理器"""
    app.add_exception_handler(BusinessError, business_error_handler)
    app.add_exception_handler(UnauthorizedError, unauthorized_error_handler)
    app.add_exception_handler(ForbiddenError, forbidden_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(SQLAlchemyError, sql_alchemy_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_error_handler)
    app.add_exception_handler(Exception, general_exception_handler)