from app.schemas.response import BaseSchema
from typing import Optional, List
from datetime import datetime


class SupplyCreateRequest(BaseSchema):
    """简历创建请求"""
    vendor_id: int
    name: str
    file_path: str
    file_name: str
    file_id: str
    owner_id: int
    content_confirm: Optional[int] = 1
    version: Optional[int] = 1
    acdtc: Optional[str] = None
    contracted_member: Optional[str] = None
    task_status: Optional[str] = "0000000000000010"
    price_update_task_date: Optional[datetime] = None
    price_update: Optional[float] = None
    price_original: Optional[float] = None


class SupplyUpdateRequest(BaseSchema):
    """简历更新请求"""
    name: Optional[str] = None
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    content_confirm: Optional[int] = None
    version: Optional[int] = None
    task_status: Optional[str] = None
    price_update: Optional[float] = None


class SupplyResponse(BaseSchema):
    """简历响应"""
    id: int
    vendor_id: int
    name: str
    path: str
    file_name: str
    file_id: str
    owner_id: int
    vendor_name: Optional[str] = None
    contact_name: Optional[str] = None
    upload_name: Optional[str] = None
    contact_position: Optional[str] = None
    content_confirm: Optional[int] = 1
    version: int
    acdtc: Optional[str] = None
    contracted_member: Optional[str] = None
    task_status: str
    price_update_task_date: Optional[datetime] = None
    price_update: Optional[float] = None
    price_original: Optional[float] = None
    created_at: datetime
    updated_at: datetime


class DemandCreateRequest(BaseSchema):
    """需求创建请求"""
    customer_id: int
    name: str
    remark: str
    unit_price_max: Optional[float] = None
    japanese_level: Optional[str] = None
    english_level: Optional[str] = None
    citizenship: Optional[str] = None
    work_location: Optional[str] = None
    work_percent: Optional[int] = None
    owner_id: int
    version: Optional[int] = 1
    analysis_status: Optional[str] = "INIT"


class DemandUpdateRequest(BaseSchema):
    """需求更新请求"""
    name: Optional[str] = None
    remark: Optional[str] = None
    unit_price_max: Optional[float] = None
    japanese_level: Optional[str] = None
    english_level: Optional[str] = None
    citizenship: Optional[str] = None
    work_location: Optional[str] = None
    work_percent: Optional[int] = None
    version: Optional[int] = None
    analysis_status: Optional[str] = None


class DemandResponse(BaseSchema):
    """需求响应"""
    id: int
    customer_id: int
    name: str
    remark: str
    unit_price_max: Optional[float] = None
    japanese_level: Optional[str] = None
    english_level: Optional[str] = None
    citizenship: Optional[str] = None
    work_location: Optional[str] = None
    work_percent: Optional[int] = None
    owner_id: int
    customer_name: Optional[str] = None
    contact_name: Optional[str] = None
    contact_position: Optional[str] = None
    owner_nick_name: Optional[str] = None
    version: int
    analysis_status: str
    created_at: datetime
    updated_at: datetime


class VendorCreateRequest(BaseSchema):
    """供应商创建请求"""
    name: str
    code: str
    folder_id: Optional[str] = None
    description: Optional[str] = None


class VendorUpdateRequest(BaseSchema):
    """供应商更新请求"""
    name: Optional[str] = None
    code: Optional[str] = None
    folder_id: Optional[str] = None
    description: Optional[str] = None


class VendorResponse(BaseSchema):
    """供应商响应"""
    id: int
    name: str
    code: str
    folder_id: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class CustomerCreateRequest(BaseSchema):
    """客户创建请求"""
    name: str
    code: str
    address: Optional[str] = None
    postcode: Optional[str] = None
    description: Optional[str] = None


class CustomerUpdateRequest(BaseSchema):
    """客户更新请求"""
    name: Optional[str] = None
    code: Optional[str] = None
    address: Optional[str] = None
    postcode: Optional[str] = None
    description: Optional[str] = None


class CustomerResponse(BaseSchema):
    """客户响应"""
    id: int
    name: str
    code: str
    address: Optional[str] = None
    postcode: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class MatchRequest(BaseSchema):
    """匹配请求"""
    demand_id: int
    supply_ids: List[int]
    role_list: Optional[List[dict]] = []
    flag_data: Optional[dict] = {}


class MatchResponse(BaseSchema):
    """匹配响应"""
    success: bool
    message: str
    match_results: Optional[List[dict]] = []


class AnalysisRequest(BaseSchema):
    """分析请求"""
    supply_id: int


class AnalysisResponse(BaseSchema):
    """分析响应"""
    success: bool
    message: str