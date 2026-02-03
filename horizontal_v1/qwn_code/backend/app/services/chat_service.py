import httpx
from typing import Optional, Dict, Any
from app.core.config.settings import settings
from app.schemas.chat import ChatMessageRequest, ChatMessageResponse, ChatHistoryRequest, ChatHistoryResponse
import json
import logging


logger = logging.getLogger(__name__)


class DifyClient:
    """Dify客户端，用于与Dify服务进行交互"""
    
    def __init__(self):
        self.base_url = settings.DIFY_BASE_URL
        self.api_key = settings.DIFY_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def chat_completion(self, query: str, conversation_id: Optional[str] = None, 
                           user: Optional[str] = None) -> Dict[str, Any]:
        """聊天补全"""
        url = f"{self.base_url}/chat-messages"
        
        payload = {
            "inputs": {},
            "query": query,
            "response_mode": "blocking",  # 使用阻塞模式以获得完整响应
            "conversation_id": conversation_id,
            "user": user or "default_user"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=self.headers, json=payload)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Dify API HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Dify API request error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error calling Dify API: {str(e)}")
            raise
    
    async def get_conversations(self, user: str = "default_user", 
                              limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """获取会话列表"""
        url = f"{self.base_url}/conversations"
        
        params = {
            "user": user,
            "limit": limit,
            "offset": offset
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Dify API HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Dify API request error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error calling Dify API: {str(e)}")
            raise
    
    async def get_conversation_messages(self, conversation_id: str, 
                                     user: str = "default_user",
                                     limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """获取会话消息"""
        url = f"{self.base_url}/conversations/{conversation_id}/messages"
        
        params = {
            "user": user,
            "limit": limit,
            "offset": offset
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Dify API HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Dify API request error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error calling Dify API: {str(e)}")
            raise


class ChatService:
    """聊天服务"""
    
    def __init__(self):
        self.dify_client = DifyClient()
    
    async def chat_completion(self, request: ChatMessageRequest) -> ChatMessageResponse:
        """聊天补全"""
        try:
            response_data = await self.dify_client.chat_completion(
                query=request.query,
                conversation_id=request.conversation_id,
                user=request.user_id
            )
            
            return ChatMessageResponse(
                code=1000,
                message="success",
                result={
                    "answer": response_data.get("answer", ""),
                    "conversation_id": response_data.get("conversation_id", ""),
                    "message_id": response_data.get("id", "")
                }
            )
        except Exception as e:
            logger.error(f"Chat completion error: {str(e)}")
            return ChatMessageResponse(
                code=500,
                message=f"聊天服务错误: {str(e)}",
                result={}
            )
    
    async def get_chat_history(self, request: ChatHistoryRequest) -> ChatHistoryResponse:
        """获取聊天历史"""
        try:
            response_data = await self.dify_client.get_conversation_messages(
                conversation_id=request.conversation_id,
                limit=request.limit,
                offset=request.offset
            )
            
            # 格式化响应数据
            messages_data = response_data.get("data", [])
            items = []
            for msg in messages_data:
                items.append({
                    "id": msg.get("id", ""),
                    "query": msg.get("query", ""),
                    "answer": msg.get("answer", ""),
                    "created_at": msg.get("created_at", "")
                })
            
            return ChatHistoryResponse(
                code=1000,
                message="success",
                result={
                    "items": items,
                    "total": len(items)
                }
            )
        except Exception as e:
            logger.error(f"Get chat history error: {str(e)}")
            return ChatHistoryResponse(
                code=500,
                message=f"获取聊天历史错误: {str(e)}",
                result={"items": [], "total": 0}
            )
    
    async def get_conversations_list(self, user_id: str = "default_user", 
                                   limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """获取会话列表"""
        try:
            response_data = await self.dify_client.get_conversations(
                user=user_id,
                limit=limit,
                offset=offset
            )
            
            # 格式化响应数据
            conversations_data = response_data.get("data", [])
            items = []
            for conv in conversations_data:
                items.append({
                    "id": conv.get("id", ""),
                    "name": conv.get("name", ""),
                    "created_at": conv.get("created_at", ""),
                    "updated_at": conv.get("updated_at", "")
                })
            
            return {
                "code": 1000,
                "message": "success",
                "result": {
                    "items": items,
                    "total": len(items)
                }
            }
        except Exception as e:
            logger.error(f"Get conversations list error: {str(e)}")
            return {
                "code": 500,
                "message": f"获取会话列表错误: {str(e)}",
                "result": {"items": [], "total": 0}
            }