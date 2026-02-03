"""
Async SharePoint/Graph API client.

Provides:
- OAuth2 client credentials authentication
- File operations (get, upload, delete)
- Folder operations (create, list)
- Sharing link management

Reference:
- assistant_py/azure_api/graph_api.py
- Wiki: 系统架构/数据架构设计.md
"""

import base64
import logging
from typing import Any

import httpx

from app.core.config import settings
from app.core.redis import CacheManager

logger = logging.getLogger("work_assistant.azure.graph")


class GraphClient:
    """
    Async Microsoft Graph API client for SharePoint operations.

    Features:
    - Client credentials OAuth2 flow
    - Token caching in Redis (20 minutes TTL)
    - File/folder CRUD operations
    - Sharing link creation
    """

    GRAPH_ENDPOINT = "https://graph.microsoft.com/v1.0"
    TOKEN_CACHE_KEY = "azure_graph_token"
    TOKEN_CACHE_NAMESPACE = "token"
    TOKEN_TTL = 1200  # 20 minutes

    def __init__(self) -> None:
        """Initialize Graph client with settings."""
        self._tenant_id = settings.azure.tenant_id
        self._client_id = settings.azure.client_id
        self._client_secret = settings.azure.client_secret
        self._drive_id = settings.azure.drive_id
        self._supply_path = settings.azure.supply_path
        self._token_url = f"https://login.microsoftonline.com/{self._tenant_id}/oauth2/v2.0/token"
        self._scope = "https://graph.microsoft.com/.default"

    async def _fetch_token(self) -> str:
        """
        Fetch new access token from Azure AD.

        Returns:
            Access token string
        """
        token_data = {
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "scope": self._scope,
            "grant_type": "client_credentials",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self._token_url,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data=token_data,
            )
            response.raise_for_status()
            data = response.json()
            logger.debug("Fetched new Graph API token")
            return data["access_token"]

    async def get_token(self) -> str:
        """
        Get access token with Redis caching.

        Returns:
            Access token string
        """
        # Try cache first
        cached = await CacheManager.get(self.TOKEN_CACHE_NAMESPACE, self.TOKEN_CACHE_KEY)
        if cached:
            return cached

        # Fetch new token
        token = await self._fetch_token()
        await CacheManager.set(
            self.TOKEN_CACHE_NAMESPACE,
            self.TOKEN_CACHE_KEY,
            token,
            ttl=self.TOKEN_TTL,
        )
        return token

    @staticmethod
    def encode_sharing_url(sharing_url: str) -> str:
        """
        Encode a sharing URL for Graph API.

        Args:
            sharing_url: SharePoint sharing URL

        Returns:
            Encoded URL for Graph API shares endpoint
        """
        base64_value = base64.b64encode(sharing_url.encode("utf-8")).decode("utf-8")
        encoded_url = "u!" + base64_value.rstrip("=").replace("/", "_").replace("+", "-")
        return encoded_url

    async def _request(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Make authenticated request to Graph API.

        Args:
            method: HTTP method
            url: Request URL
            **kwargs: Additional httpx request arguments

        Returns:
            httpx Response object
        """
        token = await self.get_token()
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {token}"

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.request(method, url, headers=headers, **kwargs)
            return response

    # ==================== File Operations ====================

    async def get_file_data(self, sharing_url: str) -> dict[str, Any]:
        """
        Get file metadata from sharing URL.

        Args:
            sharing_url: SharePoint sharing URL

        Returns:
            File metadata dict
        """
        encoded_url = self.encode_sharing_url(sharing_url)
        url = f"{self.GRAPH_ENDPOINT}/shares/{encoded_url}/driveItem"

        response = await self._request("GET", url)
        response.raise_for_status()
        return response.json()

    async def get_file_content(self, sharing_url: str) -> bytes:
        """
        Download file content from sharing URL.

        Args:
            sharing_url: SharePoint sharing URL

        Returns:
            File content as bytes
        """
        encoded_url = self.encode_sharing_url(sharing_url)
        url = f"{self.GRAPH_ENDPOINT}/shares/{encoded_url}/driveItem/content"

        response = await self._request("GET", url)
        response.raise_for_status()
        return response.content

    async def get_file_content_and_type(self, sharing_url: str) -> tuple[bytes, str]:
        """
        Download file content with content type.

        Args:
            sharing_url: SharePoint sharing URL

        Returns:
            Tuple of (file content, content type)
        """
        encoded_url = self.encode_sharing_url(sharing_url)
        url = f"{self.GRAPH_ENDPOINT}/shares/{encoded_url}/driveItem/content"

        response = await self._request("GET", url)
        content_type = response.headers.get("Content-Type", "")
        response.raise_for_status()
        return response.content, content_type

    async def upload_file(
        self,
        folder_id: str,
        file_name: str,
        file_content: bytes,
        content_type: str = "application/octet-stream",
    ) -> dict[str, Any]:
        """
        Upload file to a folder.

        Args:
            folder_id: Parent folder ID
            file_name: Name for the uploaded file
            file_content: File content as bytes
            content_type: MIME content type

        Returns:
            Uploaded file metadata
        """
        url = f"{self.GRAPH_ENDPOINT}/drives/{self._drive_id}/items/{folder_id}:/{file_name}:/content"

        response = await self._request(
            "PUT",
            url,
            headers={"Content-Type": content_type},
            content=file_content,
        )
        response.raise_for_status()
        logger.info(f"Uploaded file: {file_name} to folder {folder_id}")
        return response.json()

    async def update_file(
        self,
        file_id: str,
        file_content: bytes,
        content_type: str = "application/octet-stream",
    ) -> dict[str, Any]:
        """
        Update existing file content.

        Args:
            file_id: File ID to update
            file_content: New file content
            content_type: MIME content type

        Returns:
            Updated file metadata
        """
        url = f"{self.GRAPH_ENDPOINT}/drives/{self._drive_id}/items/{file_id}/content"

        response = await self._request(
            "PUT",
            url,
            headers={"Content-Type": content_type},
            content=file_content,
        )
        response.raise_for_status()
        logger.info(f"Updated file: {file_id}")
        return response.json()

    async def delete_file(self, file_id: str) -> None:
        """
        Delete a file.

        Args:
            file_id: File ID to delete
        """
        url = f"{self.GRAPH_ENDPOINT}/drives/{self._drive_id}/items/{file_id}"

        response = await self._request("DELETE", url)
        response.raise_for_status()
        logger.info(f"Deleted file: {file_id}")

    async def rename_file(self, file_id: str, new_name: str) -> str:
        """
        Rename a file.

        Args:
            file_id: File ID to rename
            new_name: New file name

        Returns:
            New web URL of the file
        """
        url = f"{self.GRAPH_ENDPOINT}/drives/{self._drive_id}/items/{file_id}"

        response = await self._request(
            "PATCH",
            url,
            headers={"Content-Type": "application/json"},
            json={"name": new_name},
        )
        response.raise_for_status()
        logger.info(f"Renamed file {file_id} to {new_name}")
        return response.json().get("webUrl", "")

    async def move_file(self, file_id: str, new_folder_id: str) -> dict[str, Any]:
        """
        Move file to another folder.

        Args:
            file_id: File ID to move
            new_folder_id: Target folder ID

        Returns:
            Updated file metadata
        """
        url = f"{self.GRAPH_ENDPOINT}/drives/{self._drive_id}/items/{file_id}"

        response = await self._request(
            "PATCH",
            url,
            headers={"Content-Type": "application/json"},
            json={"parentReference": {"id": new_folder_id}},
        )
        response.raise_for_status()
        logger.info(f"Moved file {file_id} to folder {new_folder_id}")
        return response.json()

    # ==================== Folder Operations ====================

    async def create_folder(self, folder_name: str) -> dict[str, str]:
        """
        Create folder in supply path.

        Args:
            folder_name: Name of the folder to create

        Returns:
            Dict with 'id' and 'url' of created folder, empty if failed
        """
        url = f"{self.GRAPH_ENDPOINT}/drives/{self._drive_id}/root:{self._supply_path}:/children"

        data = {
            "name": folder_name,
            "folder": {},
            "@microsoft.graph.conflictBehavior": "fail",
        }

        response = await self._request(
            "POST",
            url,
            headers={"Content-Type": "application/json"},
            json=data,
        )

        if response.status_code == 201:
            body = response.json()
            logger.info(f"Created folder: {folder_name}")
            return {
                "id": body.get("id", ""),
                "url": body.get("webUrl", ""),
            }
        else:
            logger.warning(f"Failed to create folder {folder_name}: {response.status_code}")
            return {}

    async def ensure_child_folder(self, parent_id: str, folder_name: str) -> dict[str, str]:
        """
        Ensure a child folder exists, create if not.

        Args:
            parent_id: Parent folder ID
            folder_name: Name of child folder

        Returns:
            Dict with 'id' and 'webUrl' of the folder
        """
        url = f"{self.GRAPH_ENDPOINT}/drives/{self._drive_id}/items/{parent_id}/children"

        data = {
            "name": folder_name,
            "folder": {},
            "@microsoft.graph.conflictBehavior": "fail",
        }

        response = await self._request(
            "POST",
            url,
            headers={"Content-Type": "application/json"},
            json=data,
        )

        if response.status_code == 201:
            body = response.json()
            return {
                "id": body.get("id", ""),
                "webUrl": body.get("webUrl", ""),
            }
        elif response.status_code == 409:
            # Folder already exists, get it
            return await self._get_child_folder(parent_id, folder_name)
        else:
            response.raise_for_status()
            return {}

    async def _get_child_folder(self, parent_id: str, folder_name: str) -> dict[str, str]:
        """
        Get existing child folder by name.

        Args:
            parent_id: Parent folder ID
            folder_name: Name of folder to find

        Returns:
            Dict with 'id' and 'webUrl' of the folder
        """
        url: str | None = f"{self.GRAPH_ENDPOINT}/drives/{self._drive_id}/items/{parent_id}/children"

        while url:
            response = await self._request("GET", url)
            response.raise_for_status()
            data = response.json()

            for item in data.get("value", []):
                if item.get("folder") is not None and item.get("name") == folder_name:
                    return {
                        "id": item.get("id", ""),
                        "webUrl": item.get("webUrl", ""),
                    }

            url = data.get("@odata.nextLink")

        return {}

    async def rename_folder(self, folder_id: str, new_name: str) -> str:
        """
        Rename a folder.

        Args:
            folder_id: Folder ID to rename
            new_name: New folder name

        Returns:
            New web URL of the folder
        """
        url = f"{self.GRAPH_ENDPOINT}/drives/{self._drive_id}/items/{folder_id}"

        response = await self._request(
            "PATCH",
            url,
            headers={"Content-Type": "application/json"},
            json={"name": new_name},
        )

        if response.status_code == 200:
            logger.info(f"Renamed folder {folder_id} to {new_name}")
            return response.json().get("webUrl", "")
        else:
            logger.warning(f"Failed to rename folder: {response.status_code}")
            return ""

    # ==================== File Listing ====================

    async def get_files(
        self,
        folder_name: str,
        delta_link: str | None = None,
    ) -> tuple[list[dict[str, Any]], str]:
        """
        Get files in a folder with delta support.

        Args:
            folder_name: Folder name within supply path
            delta_link: Optional delta link for incremental sync

        Returns:
            Tuple of (file list, new delta link)
        """
        if delta_link:
            url: str | None = delta_link
        else:
            url = f"{self.GRAPH_ENDPOINT}/drives/{self._drive_id}/root:{self._supply_path}/{folder_name}:/delta"

        files: list[dict[str, Any]] = []
        new_delta_link = ""

        while url:
            response = await self._request("GET", url)
            response.raise_for_status()
            data = response.json()

            for item in data.get("value", []):
                if "folder" in item or "deleted" in item:
                    continue

                file_id = item["id"]
                web_url = await self.create_link(self._drive_id, file_id)
                if not web_url:
                    web_url = item.get("webUrl", "")

                files.append({
                    "id": file_id,
                    "name": item.get("name", ""),
                    "webUrl": web_url,
                    "createdDateTime": item.get("createdDateTime", ""),
                    "lastModifiedDateTime": item.get("lastModifiedDateTime", ""),
                    "createdBy": item.get("createdBy", {}).get("user", {}).get("email", ""),
                })

            url = data.get("@odata.nextLink")
            if data.get("@odata.deltaLink"):
                new_delta_link = data["@odata.deltaLink"]

        return files, new_delta_link

    async def get_files_by_folder_id(
        self,
        folder_id: str,
        delta_link: str | None = None,
    ) -> tuple[list[dict[str, Any]], str]:
        """
        Get files by folder ID with delta support.

        Args:
            folder_id: Folder ID
            delta_link: Optional delta link for incremental sync

        Returns:
            Tuple of (file list, new delta link)
        """
        if delta_link:
            url: str | None = delta_link
        else:
            url = f"{self.GRAPH_ENDPOINT}/drives/{self._drive_id}/items/{folder_id}/delta"

        files: list[dict[str, Any]] = []
        new_delta_link = ""

        while url:
            response = await self._request("GET", url)
            response.raise_for_status()
            data = response.json()

            for item in data.get("value", []):
                if "folder" in item or "deleted" in item:
                    continue

                file_id = item["id"]
                web_url = await self.create_link(self._drive_id, file_id)
                if not web_url:
                    web_url = item.get("webUrl", "")

                files.append({
                    "id": file_id,
                    "name": item.get("name", ""),
                    "webUrl": web_url,
                    "createdDateTime": item.get("createdDateTime", ""),
                    "lastModifiedDateTime": item.get("lastModifiedDateTime", ""),
                    "createdBy": item.get("createdBy", {}).get("user", {}).get("email", ""),
                })

            url = data.get("@odata.nextLink")
            if data.get("@odata.deltaLink"):
                new_delta_link = data["@odata.deltaLink"]

        return files, new_delta_link

    # ==================== Sharing Links ====================

    async def create_link(self, drive_id: str, item_id: str) -> str:
        """
        Create organization sharing link for an item.

        Args:
            drive_id: Drive ID
            item_id: Item ID

        Returns:
            Sharing link URL
        """
        url = f"{self.GRAPH_ENDPOINT}/drives/{drive_id}/items/{item_id}/createLink"

        data = {
            "type": "edit",
            "scope": "organization",
        }

        try:
            response = await self._request(
                "POST",
                url,
                headers={"Content-Type": "application/json"},
                json=data,
            )
            response.raise_for_status()
            return response.json().get("link", {}).get("webUrl", "")
        except Exception as e:
            logger.warning(f"Failed to create link for {item_id}: {e}")
            return ""


# Global singleton instance
graph_client = GraphClient()
