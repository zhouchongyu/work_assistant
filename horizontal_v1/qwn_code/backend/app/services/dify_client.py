import httpx
from typing import Optional, Dict, Any, List
from app.core.config.settings import settings
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
    
    async def rename_conversation(self, conversation_id: str, name: str) -> Dict[str, Any]:
        """重命名会话"""
        url = f"{self.base_url}/conversations/{conversation_id}"
        
        payload = {
            "name": name
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.patch(url, headers=self.headers, json=payload)
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