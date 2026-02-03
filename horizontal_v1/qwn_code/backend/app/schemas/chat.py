from app.schemas.response import BaseSchema
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class ChatMessageRequest(BaseModel):
    """聊天消息请求"""
    query: str
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None
    inputs: Optional[Dict[str, Any]] = {}
    response_mode: str = "blocking"  # blocking or streaming


class ChatMessageResponse(BaseModel):
    """聊天消息响应"""
    code: int = 1000
    message: str = "success"
    result: Dict[str, Any]  # 包含answer, conversation_id, message_id等
    request_id: Optional[str] = None


class ChatHistoryRequest(BaseModel):
    """聊天历史请求"""
    conversation_id: str
    limit: int = 20
    offset: int = 0


class ChatHistoryItem(BaseModel):
    """聊天历史项"""
    id: str
    query: str
    answer: str
    created_at: str


class ChatHistoryResponse(BaseModel):
    """聊天历史响应"""
    code: int = 1000
    message: str = "success"
    result: Dict[str, Any]  # 包含items和total
    request_id: Optional[str] = None


class ConversationListRequest(BaseModel):
    """会话列表请求"""
    limit: int = 20
    offset: int = 0


class ConversationItem(BaseModel):
    """会话项"""
    id: str
    name: str
    created_at: str
    updated_at: str


class ConversationListResponse(BaseModel):
    """会话列表响应"""
    code: int = 1000
    message: str = "success"
    result: Dict[str, Any]  # 包含items和total
    request_id: Optional[str] = None