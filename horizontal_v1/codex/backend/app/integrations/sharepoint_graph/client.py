from __future__ import annotations

import base64
from dataclasses import dataclass

import httpx
from fastapi import Depends
from redis.asyncio import Redis

from backend.app.core.request_id import get_request_id
from backend.app.core.settings import get_settings
from backend.app.integrations.redis_client import get_redis


class GraphClientError(RuntimeError):
    pass


@dataclass(frozen=True)
class GraphDriveItem:
    id: str
    name: str | None
    web_url: str | None
    content_type: str | None


class GraphClient:
    def __init__(
        self,
        *,
        redis: Redis,
        tenant_id: str,
        client_id: str,
        client_secret: str,
        drive_id: str,
        supply_path: str,
    ):
        self._redis = redis
        self._tenant_id = tenant_id
        self._client_id = client_id
        self._client_secret = client_secret
        self._drive_id = drive_id
        self._supply_path = _normalize_supply_path(supply_path)

        self._graph_base_url = "https://graph.microsoft.com/v1.0"
        self._token_url = f"https://login.microsoftonline.com/{self._tenant_id}/oauth2/v2.0/token"
        self._scope = "https://graph.microsoft.com/.default"

    @property
    def drive_id(self) -> str:
        return self._drive_id

    @staticmethod
    def encode_sharing_url(sharing_url: str) -> str:
        base64_value = base64.b64encode(sharing_url.encode("utf-8")).decode("utf-8")
        return "u!" + base64_value.rstrip("=").replace("/", "_").replace("+", "-")

    async def get_access_token(self) -> str:
        token_key = f"wa:graph:token:{self._tenant_id}:{self._client_id}"
        cached = await self._redis.get(token_key)
        if cached:
            return cached

        form = {
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "scope": self._scope,
            "grant_type": "client_credentials",
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(self._token_url, headers=headers, data=form)
            resp.raise_for_status()
            data = resp.json()
        token = data.get("access_token")
        if not token:
            raise GraphClientError("Graph token response missing access_token")
        expires_in = int(data.get("expires_in") or 1200)
        await self._redis.set(token_key, token, ex=max(60, expires_in - 60))
        return token

    async def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        token = await self.get_access_token()
        headers = dict(kwargs.pop("headers", {}) or {})
        headers.setdefault("Authorization", f"Bearer {token}")
        headers.setdefault("x-request-id", get_request_id())

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.request(method, url, headers=headers, **kwargs)
            resp.raise_for_status()
            return resp

    async def create_folder(self, folder_name: str) -> dict:
        data = {
            "name": folder_name,
            "folder": {},
            "@microsoft.graph.conflictBehavior": "fail",
        }
        url = _drive_root_children_url(self._graph_base_url, self._drive_id, self._supply_path)
        resp = await self._request("POST", url, json=data)
        body = resp.json()
        return {"id": body.get("id") or "", "url": body.get("webUrl") or ""}

    async def ensure_child_folder(self, parent_id: str, folder_name: str) -> dict:
        # Try create first; if conflict, list children and find existing folder.
        create_url = f"{self._graph_base_url}/drives/{self._drive_id}/items/{parent_id}/children"
        payload = {
            "name": folder_name,
            "folder": {},
            "@microsoft.graph.conflictBehavior": "fail",
        }
        try:
            resp = await self._request("POST", create_url, json=payload)
            body = resp.json()
            return {"id": body.get("id") or "", "webUrl": body.get("webUrl") or ""}
        except httpx.HTTPStatusError as e:
            if e.response.status_code not in (409,):
                raise

        list_url = f"{self._graph_base_url}/drives/{self._drive_id}/items/{parent_id}/children?$top=999"
        resp = await self._request("GET", list_url)
        items = (resp.json() or {}).get("value") or []
        for item in items:
            if item.get("folder") is not None and item.get("name") == folder_name:
                return {"id": item.get("id") or "", "webUrl": item.get("webUrl") or ""}
        return {}

    async def get_files(self, folder_name: str, delta_link: str) -> tuple[list[dict], str]:
        if delta_link:
            url = delta_link
        else:
            url = f"{self._graph_base_url}/drives/{self._drive_id}/root:{self._supply_path}/{folder_name}:/delta"
        return await self._get_files_delta(url)

    async def get_files_by_folder_id(self, folder_id: str, delta_link: str) -> tuple[list[dict], str]:
        if delta_link:
            url = delta_link
        else:
            url = f"{self._graph_base_url}/drives/{self._drive_id}/items/{folder_id}/delta"
        return await self._get_files_delta(url)

    async def _get_files_delta(self, url: str) -> tuple[list[dict], str]:
        files: list[dict] = []
        next_link = url
        delta_link = ""
        while next_link:
            resp = await self._request("GET", next_link)
            body = resp.json() or {}
            next_link = body.get("@odata.nextLink") or ""
            delta_link = body.get("@odata.deltaLink") or delta_link
            for item in body.get("value") or []:
                if item.get("folder") is not None or item.get("deleted") is not None:
                    continue
                file_id = item.get("id") or ""
                if not file_id:
                    continue
                files.append(
                    {
                        "id": file_id,
                        "name": item.get("name"),
                        "webUrl": item.get("webUrl"),
                        "createdDateTime": item.get("createdDateTime"),
                        "lastModifiedDateTime": item.get("lastModifiedDateTime"),
                        "createdBy": ((item.get("createdBy") or {}).get("user") or {}).get("email"),
                    }
                )
        return files, delta_link

    async def create_link(self, item_id: str) -> str:
        url = f"{self._graph_base_url}/drives/{self._drive_id}/items/{item_id}/createLink"
        payload = {"type": "edit", "scope": "organization"}
        resp = await self._request("POST", url, json=payload)
        link = (resp.json() or {}).get("link") or {}
        return link.get("webUrl") or ""

    async def change_folder_name(self, folder_id: str, new_name: str) -> str:
        url = f"{self._graph_base_url}/drives/{self._drive_id}/items/{folder_id}"
        resp = await self._request("PATCH", url, json={"name": new_name})
        return (resp.json() or {}).get("webUrl") or ""

    async def change_file_name(self, file_id: str, new_name: str) -> str:
        url = f"{self._graph_base_url}/drives/{self._drive_id}/items/{file_id}"
        resp = await self._request("PATCH", url, json={"name": new_name})
        return (resp.json() or {}).get("webUrl") or ""

    async def move_file(self, file_id: str, new_folder_id: str) -> None:
        url = f"{self._graph_base_url}/drives/{self._drive_id}/items/{file_id}"
        await self._request("PATCH", url, json={"parentReference": {"id": new_folder_id}})

    async def upload_file(self, folder_id: str, file_name: str, file_content: bytes, content_type: str | None) -> dict:
        url = f"{self._graph_base_url}/drives/{self._drive_id}/items/{folder_id}:/{file_name}:/content"
        headers = {"Content-Type": content_type or "application/octet-stream"}
        resp = await self._request("PUT", url, headers=headers, content=file_content)
        return resp.json()

    async def update_file(self, file_id: str, file_content: bytes, content_type: str | None) -> dict:
        url = f"{self._graph_base_url}/drives/{self._drive_id}/items/{file_id}/content"
        headers = {"Content-Type": content_type or "application/octet-stream"}
        resp = await self._request("PUT", url, headers=headers, content=file_content)
        return resp.json()

    async def delete_file(self, file_id: str) -> None:
        url = f"{self._graph_base_url}/drives/{self._drive_id}/items/{file_id}"
        await self._request("DELETE", url)

    async def get_drive_item(self, file_id: str) -> GraphDriveItem:
        url = f"{self._graph_base_url}/drives/{self._drive_id}/items/{file_id}"
        resp = await self._request("GET", url)
        body = resp.json() or {}
        return GraphDriveItem(
            id=file_id,
            name=body.get("name"),
            web_url=body.get("webUrl"),
            content_type=((body.get("file") or {}).get("mimeType") or None),
        )

    async def get_drive_item_from_share_url(self, sharing_url: str) -> GraphDriveItem:
        encoded = self.encode_sharing_url(sharing_url)
        url = f"{self._graph_base_url}/shares/{encoded}/driveItem"
        resp = await self._request("GET", url)
        body = resp.json() or {}
        return GraphDriveItem(
            id=body.get("id") or "",
            name=body.get("name"),
            web_url=body.get("webUrl"),
            content_type=((body.get("file") or {}).get("mimeType") or None),
        )

    async def stream_file_content(self, file_id: str):
        url = f"{self._graph_base_url}/drives/{self._drive_id}/items/{file_id}/content"
        token = await self.get_access_token()
        headers = {"Authorization": f"Bearer {token}", "x-request-id": get_request_id()}

        async def _iter_bytes():
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream("GET", url, headers=headers) as resp:
                    resp.raise_for_status()
                    async for chunk in resp.aiter_bytes():
                        yield chunk

        return _iter_bytes()

    async def stream_file_content_from_share_url(self, sharing_url: str):
        encoded = self.encode_sharing_url(sharing_url)
        url = f"{self._graph_base_url}/shares/{encoded}/driveItem/content"
        token = await self.get_access_token()
        headers = {"Authorization": f"Bearer {token}", "x-request-id": get_request_id()}

        async def _iter_bytes():
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream("GET", url, headers=headers) as resp:
                    resp.raise_for_status()
                    async for chunk in resp.aiter_bytes():
                        yield chunk

        return _iter_bytes()


def _normalize_supply_path(path: str) -> str:
    raw = (path or "").strip()
    if not raw:
        return ""
    if raw == "/":
        return ""
    if not raw.startswith("/"):
        raw = "/" + raw
    return raw.rstrip("/")


def _drive_root_children_url(graph_base_url: str, drive_id: str, supply_path: str) -> str:
    if not supply_path:
        return f"{graph_base_url}/drives/{drive_id}/root/children"
    return f"{graph_base_url}/drives/{drive_id}/root:{supply_path}:/children"


def get_graph_client(redis: Redis = Depends(get_redis)) -> GraphClient:
    settings = get_settings()
    return GraphClient(
        redis=redis,
        tenant_id=settings.graph_tenant_id,
        client_id=settings.graph_client_id,
        client_secret=settings.graph_client_secret,
        drive_id=settings.graph_drive_id,
        supply_path=settings.graph_supply_path,
    )
