"""
Async Azure Blob Storage client.

Provides:
- Blob upload/download operations
- Container management
- Async streaming support

Reference:
- assistant_py/db/blob.py
- Wiki: 数据管理/缓存与存储.md
"""

import logging
from typing import Any

from azure.storage.blob.aio import BlobServiceClient, ContainerClient

from app.core.config import settings

logger = logging.getLogger("work_assistant.azure.blob")


class BlobClient:
    """
    Async Azure Blob Storage client.

    Features:
    - Async blob operations
    - Connection pooling via SDK
    - Container-level operations
    """

    _instance: "BlobClient | None" = None
    _service_client: BlobServiceClient | None = None

    def __new__(cls) -> "BlobClient":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize Blob client with settings."""
        if self._service_client is not None:
            return

        self._connection_string = settings.azure.storage_connection_string
        self._resume_container = settings.azure.storage_container_resume

    async def _get_service_client(self) -> BlobServiceClient:
        """
        Get or create async BlobServiceClient.

        Returns:
            Async BlobServiceClient instance
        """
        if self._service_client is None:
            self._service_client = BlobServiceClient.from_connection_string(
                self._connection_string
            )
        return self._service_client

    async def _get_container_client(self, container_name: str) -> ContainerClient:
        """
        Get container client for a specific container.

        Args:
            container_name: Name of the container

        Returns:
            ContainerClient instance
        """
        service_client = await self._get_service_client()
        return service_client.get_container_client(container_name)

    async def upload(
        self,
        blob_name: str,
        data: bytes | str,
        container_name: str | None = None,
        content_type: str | None = None,
        overwrite: bool = True,
        **kwargs: Any,
    ) -> str:
        """
        Upload data to a blob.

        Args:
            blob_name: Name/path of the blob
            data: Data to upload (bytes or string)
            container_name: Container name (default: resume container)
            content_type: MIME content type
            overwrite: Whether to overwrite existing blob
            **kwargs: Additional arguments for upload_blob

        Returns:
            Blob URL
        """
        container = container_name or self._resume_container
        container_client = await self._get_container_client(container)
        blob_client = container_client.get_blob_client(blob_name)

        # Prepare content settings
        content_settings = None
        if content_type:
            from azure.storage.blob import ContentSettings
            content_settings = ContentSettings(content_type=content_type)

        await blob_client.upload_blob(
            data,
            overwrite=overwrite,
            content_settings=content_settings,
            **kwargs,
        )

        logger.info(f"Uploaded blob: {blob_name} to container {container}")
        return blob_client.url

    async def download(
        self,
        blob_name: str,
        container_name: str | None = None,
    ) -> bytes:
        """
        Download blob content.

        Args:
            blob_name: Name/path of the blob
            container_name: Container name (default: resume container)

        Returns:
            Blob content as bytes
        """
        container = container_name or self._resume_container
        container_client = await self._get_container_client(container)
        blob_client = container_client.get_blob_client(blob_name)

        download_stream = await blob_client.download_blob()
        content = await download_stream.readall()

        logger.debug(f"Downloaded blob: {blob_name} from container {container}")
        return content

    async def download_to_stream(
        self,
        blob_name: str,
        stream: Any,
        container_name: str | None = None,
    ) -> None:
        """
        Download blob content to a stream.

        Args:
            blob_name: Name/path of the blob
            stream: Writable stream object
            container_name: Container name (default: resume container)
        """
        container = container_name or self._resume_container
        container_client = await self._get_container_client(container)
        blob_client = container_client.get_blob_client(blob_name)

        download_stream = await blob_client.download_blob()
        await download_stream.readinto(stream)

        logger.debug(f"Downloaded blob to stream: {blob_name}")

    async def delete(
        self,
        blob_name: str,
        container_name: str | None = None,
    ) -> None:
        """
        Delete a blob.

        Args:
            blob_name: Name/path of the blob
            container_name: Container name (default: resume container)
        """
        container = container_name or self._resume_container
        container_client = await self._get_container_client(container)
        blob_client = container_client.get_blob_client(blob_name)

        await blob_client.delete_blob()
        logger.info(f"Deleted blob: {blob_name} from container {container}")

    async def exists(
        self,
        blob_name: str,
        container_name: str | None = None,
    ) -> bool:
        """
        Check if a blob exists.

        Args:
            blob_name: Name/path of the blob
            container_name: Container name (default: resume container)

        Returns:
            True if blob exists
        """
        container = container_name or self._resume_container
        container_client = await self._get_container_client(container)
        blob_client = container_client.get_blob_client(blob_name)

        return await blob_client.exists()

    async def get_properties(
        self,
        blob_name: str,
        container_name: str | None = None,
    ) -> dict[str, Any]:
        """
        Get blob properties.

        Args:
            blob_name: Name/path of the blob
            container_name: Container name (default: resume container)

        Returns:
            Blob properties dict
        """
        container = container_name or self._resume_container
        container_client = await self._get_container_client(container)
        blob_client = container_client.get_blob_client(blob_name)

        props = await blob_client.get_blob_properties()
        return {
            "name": props.name,
            "size": props.size,
            "content_type": props.content_settings.content_type if props.content_settings else None,
            "created_on": props.creation_time,
            "last_modified": props.last_modified,
            "etag": props.etag,
        }

    async def list_blobs(
        self,
        prefix: str | None = None,
        container_name: str | None = None,
        max_results: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        List blobs in a container.

        Args:
            prefix: Optional blob name prefix filter
            container_name: Container name (default: resume container)
            max_results: Maximum number of results to return

        Returns:
            List of blob info dicts
        """
        container = container_name or self._resume_container
        container_client = await self._get_container_client(container)

        blobs = []
        count = 0
        async for blob in container_client.list_blobs(name_starts_with=prefix):
            blobs.append({
                "name": blob.name,
                "size": blob.size,
                "content_type": blob.content_settings.content_type if blob.content_settings else None,
                "created_on": blob.creation_time,
                "last_modified": blob.last_modified,
            })
            count += 1
            if max_results and count >= max_results:
                break

        return blobs

    async def copy_blob(
        self,
        source_blob: str,
        dest_blob: str,
        source_container: str | None = None,
        dest_container: str | None = None,
    ) -> str:
        """
        Copy a blob to another location.

        Args:
            source_blob: Source blob name
            dest_blob: Destination blob name
            source_container: Source container (default: resume container)
            dest_container: Destination container (default: same as source)

        Returns:
            Destination blob URL
        """
        src_container = source_container or self._resume_container
        dst_container = dest_container or src_container

        src_container_client = await self._get_container_client(src_container)
        src_blob_client = src_container_client.get_blob_client(source_blob)
        source_url = src_blob_client.url

        dst_container_client = await self._get_container_client(dst_container)
        dst_blob_client = dst_container_client.get_blob_client(dest_blob)

        await dst_blob_client.start_copy_from_url(source_url)

        logger.info(f"Copied blob from {source_blob} to {dest_blob}")
        return dst_blob_client.url

    async def close(self) -> None:
        """Close the service client connection."""
        if self._service_client:
            await self._service_client.close()
            self._service_client = None
            logger.info("Blob service client closed")


# Global singleton instance
blob_client = BlobClient()
