from __future__ import annotations

from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from backend.app.core.request_id import get_request_id


def success(result: Any) -> JSONResponse:
    return JSONResponse(
        status_code=200,
        content={
            "code": 1000,
            "message": "success",
            "result": jsonable_encoder(result, by_alias=True),
            "request_id": get_request_id(),
        },
    )


def business_error(message: str, *, result: Any = None, code: int = 1001) -> JSONResponse:
    return JSONResponse(
        status_code=200,
        content={
            "code": code,
            "message": message,
            "result": jsonable_encoder(result, by_alias=True),
            "request_id": get_request_id(),
        },
    )
