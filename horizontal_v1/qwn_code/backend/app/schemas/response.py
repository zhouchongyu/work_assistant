from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from typing import Optional, Generic, TypeVar, List, Any, Dict
from enum import Enum
from datetime import datetime
import uuid


T = TypeVar('T')


class ResponseCode(Enum):
    """响应码枚举"""
    SUCCESS = 1000
    BUSINESS_ERROR = 1001
    PARAM_ERROR = 1002
    UNAUTHORIZED = 10032
    FORBIDDEN = 10033
    NOT_FOUND = 10034
    SYSTEM_ERROR = 500


class BaseResponse(BaseModel):
    """基础响应模型"""
    code: int
    message: str
    request_id: Optional[str] = None
    timestamp: datetime = datetime.now()

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SuccessResponse(BaseModel, Generic[T]):
    """成功响应模型"""
    code: int = ResponseCode.SUCCESS.value
    message: str = "success"
    result: Optional[T] = None
    request_id: Optional[str] = None
    timestamp: datetime = datetime.now()

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ErrorResponse(BaseModel):
    """错误响应模型"""
    code: int
    message: str
    result: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None
    timestamp: datetime = datetime.now()

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# 为了兼容 snake_case 和 camelCase 输入，我们定义一个基类
class BaseSchema(BaseModel):
    """基础Schema，支持别名生成器以实现camelCase输出"""
    model_config = ConfigDict(
        # 允许使用别名进行模型创建
        populate_by_name=True,
        # 允许任意类型
        arbitrary_types_allowed=True,
        # 使用驼峰命名作为别名
        alias_generator=to_camel
    )