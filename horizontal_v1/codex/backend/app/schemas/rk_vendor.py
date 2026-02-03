from __future__ import annotations

from backend.app.schemas.base import Schema


class RkVendorCreateRequest(Schema):
    name: str
    code: str | None = None


class RkVendorUpdateRequest(Schema):
    id: int
    name: str | None = None
    code: str | None = None


class RkVendorOut(Schema):
    id: int
    name: str
    code: str | None = None


class RkCustomerContactCreateRequest(Schema):
    customer_id: int
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    default: bool | None = None


class RkCustomerContactUpdateRequest(Schema):
    id: int
    customer_id: int
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    default: bool | None = None


class RkVendorContactCreateRequest(Schema):
    vendor_id: int
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    default: bool | None = None


class RkVendorContactUpdateRequest(Schema):
    id: int
    vendor_id: int
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    default: bool | None = None


class RkCustomerContactOut(Schema):
    id: int
    customer_id: int
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    default: bool | None = None


class RkVendorContactOut(Schema):
    id: int
    vendor_id: int
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    default: bool | None = None

