"""
Async MSAL (Microsoft Authentication Library) client.

Provides:
- On-Behalf-Of (OBO) flow for delegated permissions
- Teams chat operations
- Email sending via Graph API

Reference:
- assistant_py/msal_api/msal_api.py
- assistant_py/azure_api/graph_api_mail.py
"""

import logging
from typing import Any

import httpx
import msal
import anyio

from app.core.config import settings

logger = logging.getLogger("work_assistant.azure.msal")


class MsalClient:
    """
    Async MSAL client for delegated Graph API operations.

    Features:
    - On-Behalf-Of flow for user context
    - Teams chat operations
    - Batch Graph API requests
    """

    GRAPH_ENDPOINT = "https://graph.microsoft.com/v1.0"

    def __init__(self) -> None:
        """Initialize MSAL client with settings."""
        self._tenant_id = settings.azure.msal_tenant_id
        self._client_id = settings.azure.msal_client_id
        self._client_secret = settings.azure.msal_client_secret

        # Build authority URL
        if str(self._tenant_id).startswith("https://"):
            self._authority_url = self._tenant_id
        else:
            self._authority_url = f"https://login.microsoftonline.com/{self._tenant_id}"

        # Create MSAL confidential client
        self._cca = msal.ConfidentialClientApplication(
            client_id=self._client_id,
            authority=self._authority_url,
            client_credential=self._client_secret,
        )

    async def _obo(self, scopes: list[str], user_token: str) -> str:
        """
        Acquire token on behalf of user.

        Args:
            scopes: List of Graph API scopes
            user_token: User's access token

        Returns:
            Graph API access token

        Note:
            Currently returns the user token directly.
            Uncomment OBO logic if delegated permissions are configured.
        """
        # If OBO is properly configured, uncomment below:
        # def _call():
        #     return self._cca.acquire_token_on_behalf_of(
        #         user_assertion=user_token,
        #         scopes=scopes,
        #     )
        #
        # result = await anyio.to_thread.run_sync(_call)
        #
        # if "access_token" not in result:
        #     raise HTTPException(status_code=401, detail=result)
        # return result["access_token"]

        # For now, pass through the user token
        return user_token

    # ==================== Teams Chat Operations ====================

    async def send_chat_message(
        self,
        user_token: str,
        chat_id: str,
        content: str,
        content_type: str = "html",
    ) -> None:
        """
        Send a message to a Teams chat.

        Args:
            user_token: User's access token
            chat_id: Teams chat ID
            content: Message content
            content_type: Content type ("html" or "text")
        """
        graph_token = await self._obo(
            ["https://graph.microsoft.com/.default"],
            user_token=user_token,
        )

        # Convert newlines to HTML breaks for HTML content
        if content_type == "html":
            content = content.replace("\n", "<br>")

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                f"{self.GRAPH_ENDPOINT}/chats/{chat_id}/messages",
                headers={
                    "Authorization": f"Bearer {graph_token}",
                    "Content-Type": "application/json",
                },
                json={
                    "body": {
                        "contentType": content_type,
                        "content": content,
                    }
                },
            )

        if response.status_code >= 300:
            logger.error(f"Failed to send chat message: {response.status_code}")
            response.raise_for_status()

        logger.info(f"Sent message to chat {chat_id}")

    async def get_chats(self, user_token: str) -> list[dict[str, str]]:
        """
        Get all chats for the user.

        Args:
            user_token: User's access token

        Returns:
            List of chat dicts with 'id' and 'name'
        """
        graph_token = await self._obo(
            ["https://graph.microsoft.com/.default"],
            user_token=user_token,
        )

        # Get current user for filtering
        me = await self._get_me(graph_token)
        me_id = me.get("id", "")

        # Get all chats
        chats = await self._get_all_chats(graph_token)

        # Simplify to id and name
        result = []
        for chat in chats:
            chat_id = chat.get("id")
            if not chat_id:
                continue
            name = self._name_for_chat(chat, me_id)
            result.append({"id": chat_id, "name": name})

        return result

    async def _get_me(self, graph_token: str) -> dict[str, Any]:
        """Get current user profile."""
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                f"{self.GRAPH_ENDPOINT}/me",
                headers={"Authorization": f"Bearer {graph_token}"},
            )
        response.raise_for_status()
        return response.json()

    async def _get_all_chats(self, graph_token: str) -> list[dict[str, Any]]:
        """Get all chats with pagination."""
        url: str | None = (
            f"{self.GRAPH_ENDPOINT}/me/chats"
            "?$top=50"
            "&$select=id,topic,chatType,lastUpdatedDateTime"
        )

        items: list[dict[str, Any]] = []

        async with httpx.AsyncClient(timeout=20.0) as client:
            while url:
                response = await client.get(
                    url,
                    headers={"Authorization": f"Bearer {graph_token}"},
                )
                response.raise_for_status()
                data = response.json()
                items.extend(data.get("value", []))
                url = data.get("@odata.nextLink")

        # Get members for 1:1 chats without topic
        need_members = [
            c["id"] for c in items
            if (c.get("chatType", "").lower() == "oneonone" and not c.get("topic", "").strip())
        ]

        if need_members:
            members_map = await self._batch_get_chat_members(graph_token, need_members)

            # Get user details for members without display names
            missing_user_ids = set()
            for members in members_map.values():
                for m in members:
                    if not m.get("displayName", "").strip() and m.get("userId"):
                        missing_user_ids.add(m["userId"])

            users_map = {}
            if missing_user_ids:
                users_map = await self._batch_get_users(graph_token, list(missing_user_ids))

            # Attach members to chats
            for chat in items:
                chat_id = chat.get("id")
                if chat_id in members_map:
                    members = members_map[chat_id]
                    for m in members:
                        if not m.get("displayName", "").strip():
                            user = users_map.get(m.get("userId", ""), {})
                            m["displayName"] = (
                                user.get("displayName")
                                or user.get("userPrincipalName")
                                or user.get("mail")
                                or ""
                            )
                    chat["members"] = members

        return items

    async def _batch_get_chat_members(
        self,
        graph_token: str,
        chat_ids: list[str],
    ) -> dict[str, list[dict[str, Any]]]:
        """Batch get members for multiple chats."""
        if not chat_ids:
            return {}

        result: dict[str, list[dict[str, Any]]] = {}

        async with httpx.AsyncClient(timeout=20.0) as client:
            # Graph batch supports max 20 requests
            for i in range(0, len(chat_ids), 20):
                chunk = chat_ids[i:i + 20]
                body = {
                    "requests": [
                        {
                            "id": str(j),
                            "method": "GET",
                            "url": f"/v1.0/chats/{cid}/members?$select=userId,displayName",
                        }
                        for j, cid in enumerate(chunk)
                    ]
                }

                response = await client.post(
                    f"{self.GRAPH_ENDPOINT}/$batch",
                    headers={
                        "Authorization": f"Bearer {graph_token}",
                        "Content-Type": "application/json",
                    },
                    json=body,
                )
                response.raise_for_status()
                data = response.json()

                for req, cid in zip(data.get("responses", []), chunk):
                    if 200 <= req.get("status", 0) < 300:
                        result[cid] = req.get("body", {}).get("value", [])

        return result

    async def _batch_get_users(
        self,
        graph_token: str,
        user_ids: list[str],
    ) -> dict[str, dict[str, Any]]:
        """Batch get user profiles."""
        if not user_ids:
            return {}

        result: dict[str, dict[str, Any]] = {}

        async with httpx.AsyncClient(timeout=20.0) as client:
            for i in range(0, len(user_ids), 20):
                chunk = user_ids[i:i + 20]
                body = {
                    "requests": [
                        {
                            "id": str(j),
                            "method": "GET",
                            "url": f"/v1.0/users/{uid}?$select=id,displayName,mail,userPrincipalName",
                        }
                        for j, uid in enumerate(chunk)
                    ]
                }

                response = await client.post(
                    f"{self.GRAPH_ENDPOINT}/$batch",
                    headers={
                        "Authorization": f"Bearer {graph_token}",
                        "Content-Type": "application/json",
                    },
                    json=body,
                )
                response.raise_for_status()
                data = response.json()

                for item in data.get("responses", []):
                    if 200 <= item.get("status", 0) < 300:
                        user = item.get("body", {})
                        if user.get("id"):
                            result[user["id"]] = user

        return result

    @staticmethod
    def _name_for_chat(chat: dict[str, Any], me_id: str) -> str:
        """Derive display name for a chat."""
        chat_type = chat.get("chatType", "").lower()
        topic = chat.get("topic", "").strip()
        members = chat.get("members", [])

        def other_member_names(max_count: int | None = None) -> str:
            names = []
            for m in members:
                uid = m.get("userId") or m.get("user", {}).get("id")
                if uid and uid == me_id:
                    continue
                dn = m.get("displayName", "").strip()
                if dn:
                    names.append(dn)
            if not names:
                return ""
            if max_count is None or len(names) <= max_count:
                return ", ".join(names)
            return ", ".join(names[:max_count]) + f" +{len(names) - max_count}"

        if chat_type == "oneonone":
            # 1:1 chat - use other person's name
            for m in members:
                uid = m.get("userId") or m.get("user", {}).get("id")
                if uid and uid != me_id:
                    name = m.get("displayName", "").strip()
                    if name:
                        return name
            return topic or "1:1 聊天"

        if chat_type in ("group", "meeting"):
            return topic or other_member_names(max_count=3) or (
                "会议" if chat_type == "meeting" else "群聊"
            )

        return topic or other_member_names(max_count=3) or "聊天"

    # ==================== Email Operations ====================

    async def send_email(
        self,
        user_token: str,
        to_recipients: list[str],
        subject: str,
        body: str,
        body_type: str = "HTML",
        cc_recipients: list[str] | None = None,
        attachments: list[dict[str, Any]] | None = None,
    ) -> None:
        """
        Send email via Graph API.

        Args:
            user_token: User's access token
            to_recipients: List of recipient email addresses
            subject: Email subject
            body: Email body content
            body_type: Body type ("HTML" or "Text")
            cc_recipients: Optional CC recipients
            attachments: Optional list of attachments
        """
        graph_token = await self._obo(
            ["https://graph.microsoft.com/.default"],
            user_token=user_token,
        )

        message = {
            "subject": subject,
            "body": {
                "contentType": body_type,
                "content": body,
            },
            "toRecipients": [
                {"emailAddress": {"address": addr}} for addr in to_recipients
            ],
        }

        if cc_recipients:
            message["ccRecipients"] = [
                {"emailAddress": {"address": addr}} for addr in cc_recipients
            ]

        if attachments:
            message["attachments"] = attachments

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.GRAPH_ENDPOINT}/me/sendMail",
                headers={
                    "Authorization": f"Bearer {graph_token}",
                    "Content-Type": "application/json",
                },
                json={"message": message},
            )

        if response.status_code >= 300:
            logger.error(f"Failed to send email: {response.status_code}")
            response.raise_for_status()

        logger.info(f"Sent email to {to_recipients}")


# Global singleton instance
msal_client = MsalClient()
