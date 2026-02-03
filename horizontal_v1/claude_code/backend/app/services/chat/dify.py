"""
Dify AI platform integration service.

Provides:
- Chat mode (conversational AI)
- Streaming response support
- Conversation history management
- Workflow execution
- Agent interaction

Reference:
- cool-admin-midway/typings/dify.d.ts
- Wiki: AI机器学习集成/AI机器学习集成.md
"""

import json
import logging
from collections.abc import AsyncGenerator
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger("work_assistant.chat.dify")


class DifyClient:
    """
    Async Dify AI platform client.

    Features:
    - Chat conversations with context
    - Streaming and blocking response modes
    - Workflow execution
    - Agent mode
    - Text generation
    """

    def __init__(self) -> None:
        """Initialize Dify client with settings."""
        self._base_url = settings.ai.dify_api_base_url or "http://localhost/v1"
        self._default_api_key = settings.ai.dify_api_key
        self._timeout = 120.0

    def _get_headers(self, api_key: str | None = None) -> dict[str, str]:
        """
        Get request headers with API key.

        Args:
            api_key: Optional API key override

        Returns:
            Headers dict
        """
        key = api_key or self._default_api_key
        return {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }

    # ==================== Chat Mode ====================

    async def chat(
        self,
        query: str,
        user: str,
        inputs: dict[str, Any] | None = None,
        conversation_id: str | None = None,
        api_key: str | None = None,
        files: list[dict[str, Any]] | None = None,
        auto_generate_name: bool = True,
    ) -> dict[str, Any]:
        """
        Send chat message (blocking mode).

        Args:
            query: User message
            user: User identifier
            inputs: Optional input variables
            conversation_id: Optional existing conversation ID
            api_key: Optional API key override
            files: Optional file attachments
            auto_generate_name: Whether to auto-generate conversation name

        Returns:
            Chat response dict with answer, conversation_id, etc.
        """
        url = f"{self._base_url}/chat-messages"

        body = {
            "query": query,
            "inputs": inputs or {},
            "user": user,
            "response_mode": "blocking",
            "auto_generate_name": auto_generate_name,
        }

        if conversation_id:
            body["conversation_id"] = conversation_id
        if files:
            body["files"] = files

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(
                url,
                headers=self._get_headers(api_key),
                json=body,
            )
            response.raise_for_status()
            result = response.json()
            logger.debug(f"Chat response for user {user}: conversation_id={result.get('conversation_id')}")
            return result

    async def chat_stream(
        self,
        query: str,
        user: str,
        inputs: dict[str, Any] | None = None,
        conversation_id: str | None = None,
        api_key: str | None = None,
        files: list[dict[str, Any]] | None = None,
        auto_generate_name: bool = True,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """
        Send chat message (streaming mode).

        Args:
            query: User message
            user: User identifier
            inputs: Optional input variables
            conversation_id: Optional existing conversation ID
            api_key: Optional API key override
            files: Optional file attachments
            auto_generate_name: Whether to auto-generate conversation name

        Yields:
            Stream events with answer chunks
        """
        url = f"{self._base_url}/chat-messages"

        body = {
            "query": query,
            "inputs": inputs or {},
            "user": user,
            "response_mode": "streaming",
            "auto_generate_name": auto_generate_name,
        }

        if conversation_id:
            body["conversation_id"] = conversation_id
        if files:
            body["files"] = files

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            async with client.stream(
                "POST",
                url,
                headers=self._get_headers(api_key),
                json=body,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data.strip():
                            try:
                                yield json.loads(data)
                            except json.JSONDecodeError:
                                logger.warning(f"Failed to parse SSE data: {data}")

    # ==================== Conversation Management ====================

    async def get_conversations(
        self,
        user: str,
        api_key: str | None = None,
        limit: int = 20,
        last_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Get user's conversation list.

        Args:
            user: User identifier
            api_key: Optional API key override
            limit: Maximum conversations to return
            last_id: Last conversation ID for pagination

        Returns:
            Conversations list response
        """
        url = f"{self._base_url}/conversations"

        params = {
            "user": user,
            "limit": limit,
        }
        if last_id:
            params["last_id"] = last_id

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                url,
                headers=self._get_headers(api_key),
                params=params,
            )
            response.raise_for_status()
            return response.json()

    async def get_messages(
        self,
        user: str,
        conversation_id: str,
        api_key: str | None = None,
        limit: int = 20,
        first_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Get messages in a conversation.

        Args:
            user: User identifier
            conversation_id: Conversation ID
            api_key: Optional API key override
            limit: Maximum messages to return
            first_id: First message ID for pagination

        Returns:
            Messages list response
        """
        url = f"{self._base_url}/messages"

        params = {
            "user": user,
            "conversation_id": conversation_id,
            "limit": limit,
        }
        if first_id:
            params["first_id"] = first_id

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                url,
                headers=self._get_headers(api_key),
                params=params,
            )
            response.raise_for_status()
            return response.json()

    async def delete_conversation(
        self,
        user: str,
        conversation_id: str,
        api_key: str | None = None,
    ) -> bool:
        """
        Delete a conversation.

        Args:
            user: User identifier
            conversation_id: Conversation ID to delete
            api_key: Optional API key override

        Returns:
            True if deleted successfully
        """
        url = f"{self._base_url}/conversations/{conversation_id}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.delete(
                url,
                headers=self._get_headers(api_key),
                json={"user": user},
            )
            response.raise_for_status()
            logger.info(f"Deleted conversation {conversation_id} for user {user}")
            return True

    async def rename_conversation(
        self,
        user: str,
        conversation_id: str,
        name: str,
        api_key: str | None = None,
    ) -> dict[str, Any]:
        """
        Rename a conversation.

        Args:
            user: User identifier
            conversation_id: Conversation ID
            name: New conversation name
            api_key: Optional API key override

        Returns:
            Updated conversation info
        """
        url = f"{self._base_url}/conversations/{conversation_id}/name"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                headers=self._get_headers(api_key),
                json={
                    "user": user,
                    "name": name,
                },
            )
            response.raise_for_status()
            return response.json()

    # ==================== Workflow Mode ====================

    async def workflows(
        self,
        inputs: dict[str, Any],
        user: str,
        api_key: str | None = None,
        files: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        Execute workflow (blocking mode).

        Args:
            inputs: Workflow input variables
            user: User identifier
            api_key: Optional API key override
            files: Optional file attachments

        Returns:
            Workflow execution result
        """
        url = f"{self._base_url}/workflows/run"

        body = {
            "inputs": inputs,
            "user": user,
            "response_mode": "blocking",
        }
        if files:
            body["files"] = files

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(
                url,
                headers=self._get_headers(api_key),
                json=body,
            )
            response.raise_for_status()
            return response.json()

    async def workflows_stream(
        self,
        inputs: dict[str, Any],
        user: str,
        api_key: str | None = None,
        files: list[dict[str, Any]] | None = None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """
        Execute workflow (streaming mode).

        Args:
            inputs: Workflow input variables
            user: User identifier
            api_key: Optional API key override
            files: Optional file attachments

        Yields:
            Stream events with workflow progress
        """
        url = f"{self._base_url}/workflows/run"

        body = {
            "inputs": inputs,
            "user": user,
            "response_mode": "streaming",
        }
        if files:
            body["files"] = files

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            async with client.stream(
                "POST",
                url,
                headers=self._get_headers(api_key),
                json=body,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data.strip():
                            try:
                                yield json.loads(data)
                            except json.JSONDecodeError:
                                logger.warning(f"Failed to parse SSE data: {data}")

    # ==================== Agent Mode ====================

    async def agent(
        self,
        query: str,
        user: str,
        inputs: dict[str, Any] | None = None,
        conversation_id: str | None = None,
        api_key: str | None = None,
        files: list[dict[str, Any]] | None = None,
        auto_generate_name: bool = True,
    ) -> dict[str, Any]:
        """
        Send agent query (blocking mode).

        Args:
            query: User query
            user: User identifier
            inputs: Optional input variables
            conversation_id: Optional existing conversation ID
            api_key: Optional API key override
            files: Optional file attachments
            auto_generate_name: Whether to auto-generate conversation name

        Returns:
            Agent response dict
        """
        # Agent uses the same endpoint as chat but with agent capabilities
        url = f"{self._base_url}/agent/chat"

        body = {
            "query": query,
            "inputs": inputs or {},
            "user": user,
            "response_mode": "blocking",
            "auto_generate_name": auto_generate_name,
        }

        if conversation_id:
            body["conversation_id"] = conversation_id
        if files:
            body["files"] = files

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(
                url,
                headers=self._get_headers(api_key),
                json=body,
            )
            response.raise_for_status()
            return response.json()

    async def agent_stream(
        self,
        query: str,
        user: str,
        inputs: dict[str, Any] | None = None,
        conversation_id: str | None = None,
        api_key: str | None = None,
        files: list[dict[str, Any]] | None = None,
        auto_generate_name: bool = True,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """
        Send agent query (streaming mode).

        Yields:
            Stream events with agent thoughts and actions
        """
        url = f"{self._base_url}/agent/chat"

        body = {
            "query": query,
            "inputs": inputs or {},
            "user": user,
            "response_mode": "streaming",
            "auto_generate_name": auto_generate_name,
        }

        if conversation_id:
            body["conversation_id"] = conversation_id
        if files:
            body["files"] = files

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            async with client.stream(
                "POST",
                url,
                headers=self._get_headers(api_key),
                json=body,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data.strip():
                            try:
                                yield json.loads(data)
                            except json.JSONDecodeError:
                                logger.warning(f"Failed to parse SSE data: {data}")

    # ==================== Text Generation Mode ====================

    async def text(
        self,
        inputs: dict[str, Any],
        user: str,
        api_key: str | None = None,
        conversation_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Generate text (blocking mode).

        Args:
            inputs: Input variables for text generation
            user: User identifier
            api_key: Optional API key override
            conversation_id: Optional conversation ID

        Returns:
            Text generation result
        """
        url = f"{self._base_url}/completion-messages"

        body = {
            "inputs": inputs,
            "user": user,
            "response_mode": "blocking",
        }

        if conversation_id:
            body["conversation_id"] = conversation_id

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(
                url,
                headers=self._get_headers(api_key),
                json=body,
            )
            response.raise_for_status()
            return response.json()

    async def text_stream(
        self,
        inputs: dict[str, Any],
        user: str,
        api_key: str | None = None,
        conversation_id: str | None = None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """
        Generate text (streaming mode).

        Yields:
            Stream events with text chunks
        """
        url = f"{self._base_url}/completion-messages"

        body = {
            "inputs": inputs,
            "user": user,
            "response_mode": "streaming",
        }

        if conversation_id:
            body["conversation_id"] = conversation_id

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            async with client.stream(
                "POST",
                url,
                headers=self._get_headers(api_key),
                json=body,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data.strip():
                            try:
                                yield json.loads(data)
                            except json.JSONDecodeError:
                                logger.warning(f"Failed to parse SSE data: {data}")

    # ==================== Message Feedback ====================

    async def feedback(
        self,
        message_id: str,
        user: str,
        rating: str,
        api_key: str | None = None,
    ) -> dict[str, Any]:
        """
        Submit feedback for a message.

        Args:
            message_id: Message ID
            user: User identifier
            rating: Rating ("like", "dislike", or null)
            api_key: Optional API key override

        Returns:
            Feedback response
        """
        url = f"{self._base_url}/messages/{message_id}/feedbacks"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                headers=self._get_headers(api_key),
                json={
                    "user": user,
                    "rating": rating,
                },
            )
            response.raise_for_status()
            return response.json()

    # ==================== File Upload ====================

    async def upload_file(
        self,
        user: str,
        file_content: bytes,
        file_name: str,
        api_key: str | None = None,
    ) -> dict[str, Any]:
        """
        Upload file for use in conversations.

        Args:
            user: User identifier
            file_content: File content as bytes
            file_name: File name
            api_key: Optional API key override

        Returns:
            Upload response with file ID
        """
        url = f"{self._base_url}/files/upload"

        headers = self._get_headers(api_key)
        # Remove Content-Type for multipart
        del headers["Content-Type"]

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                url,
                headers=headers,
                data={"user": user},
                files={"file": (file_name, file_content)},
            )
            response.raise_for_status()
            return response.json()


# Global singleton instance
dify_client = DifyClient()
