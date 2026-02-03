from __future__ import annotations

import uuid
from contextvars import ContextVar
from typing import Awaitable, Callable

from fastapi import Request, Response

REQUEST_ID_HEADER = "x-request-id"

_request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")


def get_request_id() -> str:
    request_id = _request_id_ctx.get()
    if request_id:
        return request_id
    request_id = str(uuid.uuid4())
    _request_id_ctx.set(request_id)
    return request_id


async def request_id_middleware(request: Request, call_next: Callable[[Request], Awaitable[Response]]):
    request_id = request.headers.get(REQUEST_ID_HEADER)
    if not request_id:
        request_id = str(uuid.uuid4())
    _request_id_ctx.set(request_id)
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers[REQUEST_ID_HEADER] = request_id
    return response

