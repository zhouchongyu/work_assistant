from fastapi import APIRouter, Depends
from typing import List
from app.schemas.rk import (
    VendorCreateRequest, VendorUpdateRequest, VendorResponse,
    CustomerCreateRequest, CustomerUpdateRequest, CustomerResponse,
    SupplyCreateRequest, SupplyUpdateRequest, SupplyResponse,
    DemandCreateRequest, DemandUpdateRequest, DemandResponse,
    MatchRequest, MatchResponse, AnalysisRequest, AnalysisResponse
)
from app.services.rk_service import (
    VendorService, CustomerService, SupplyService, DemandService, MatchService
)
from app.api.v1.auth import get_current_user
from app.core.exceptions import BusinessError


router = APIRouter()


# 供应商相关接口
@router.post("/vendor", response_model=VendorResponse)
async def create_vendor(
    request: VendorCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    """创建供应商"""
    vendor_data = request.model_dump()
    return await VendorService.create_vendor(vendor_data)


@router.get("/vendor/{vendor_id}", response_model=VendorResponse)
async def get_vendor(vendor_id: int):
    """获取供应商"""
    vendor = await VendorService.get_vendor_by_id(vendor_id)
    if not vendor:
        raise BusinessError(message="供应商不存在", code=10034)
    return vendor


@router.put("/vendor/{vendor_id}", response_model=VendorResponse)
async def update_vendor(
    vendor_id: int,
    request: VendorUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """更新供应商"""
    update_data = request.model_dump(exclude_unset=True)
    result = await VendorService.update_vendor(vendor_id, update_data)
    if not result:
        raise BusinessError(message="供应商不存在", code=10034)
    return result


@router.delete("/vendor/{vendor_id}")
async def delete_vendor(
    vendor_id: int,
    current_user: dict = Depends(get_current_user)
):
    """删除供应商"""
    success = await VendorService.delete_vendor(vendor_id)
    if not success:
        raise BusinessError(message="供应商不存在", code=10034)
    return {"code": 1000, "message": "删除成功"}


# 客户相关接口
@router.post("/customer", response_model=CustomerResponse)
async def create_customer(
    request: CustomerCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    """创建客户"""
    customer_data = request.model_dump()
    return await CustomerService.create_customer(customer_data)


@router.get("/customer/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: int):
    """获取客户"""
    customer = await CustomerService.get_customer_by_id(customer_id)
    if not customer:
        raise BusinessError(message="客户不存在", code=10034)
    return customer


@router.put("/customer/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int,
    request: CustomerUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """更新客户"""
    update_data = request.model_dump(exclude_unset=True)
    result = await CustomerService.update_customer(customer_id, update_data)
    if not result:
        raise BusinessError(message="客户不存在", code=10034)
    return result


@router.delete("/customer/{customer_id}")
async def delete_customer(
    customer_id: int,
    current_user: dict = Depends(get_current_user)
):
    """删除客户"""
    success = await CustomerService.delete_customer(customer_id)
    if not success:
        raise BusinessError(message="客户不存在", code=10034)
    return {"code": 1000, "message": "删除成功"}


# 简历相关接口
@router.post("/supply", response_model=SupplyResponse)
async def create_supply(
    request: SupplyCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    """创建简历"""
    supply_data = request.model_dump()
    return await SupplyService.create_supply(supply_data)


@router.get("/supply/{supply_id}", response_model=SupplyResponse)
async def get_supply(supply_id: int):
    """获取简历"""
    supply = await SupplyService.get_supply_by_id(supply_id)
    if not supply:
        raise BusinessError(message="简历不存在", code=10034)
    return supply


@router.put("/supply/{supply_id}", response_model=SupplyResponse)
async def update_supply(
    supply_id: int,
    request: SupplyUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """更新简历"""
    update_data = request.model_dump(exclude_unset=True)
    result = await SupplyService.update_supply(supply_id, update_data)
    if not result:
        raise BusinessError(message="简历不存在", code=10034)
    return result


@router.delete("/supply/{supply_id}")
async def delete_supply(
    supply_id: int,
    current_user: dict = Depends(get_current_user)
):
    """删除简历"""
    success = await SupplyService.delete_supply(supply_id)
    if not success:
        raise BusinessError(message="简历不存在", code=10034)
    return {"code": 1000, "message": "删除成功"}


@router.post("/supply/{supply_id}/analysis", response_model=AnalysisResponse)
async def trigger_supply_analysis(
    supply_id: int,
    current_user: dict = Depends(get_current_user)
):
    """触发简历分析"""
    return await SupplyService.trigger_analysis(supply_id)


# 需求相关接口
@router.post("/demand", response_model=DemandResponse)
async def create_demand(
    request: DemandCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    """创建需求"""
    demand_data = request.model_dump()
    return await DemandService.create_demand(demand_data)


@router.get("/demand/{demand_id}", response_model=DemandResponse)
async def get_demand(demand_id: int):
    """获取需求"""
    demand = await DemandService.get_demand_by_id(demand_id)
    if not demand:
        raise BusinessError(message="需求不存在", code=10034)
    return demand


@router.put("/demand/{demand_id}", response_model=DemandResponse)
async def update_demand(
    demand_id: int,
    request: DemandUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """更新需求"""
    update_data = request.model_dump(exclude_unset=True)
    result = await DemandService.update_demand(demand_id, update_data)
    if not result:
        raise BusinessError(message="需求不存在", code=10034)
    return result


@router.delete("/demand/{demand_id}")
async def delete_demand(
    demand_id: int,
    current_user: dict = Depends(get_current_user)
):
    """删除需求"""
    success = await DemandService.delete_demand(demand_id)
    if not success:
        raise BusinessError(message="需求不存在", code=10034)
    return {"code": 1000, "message": "删除成功"}


# 匹配相关接口
@router.post("/match", response_model=MatchResponse)
async def perform_match(
    request: MatchRequest,
    current_user: dict = Depends(get_current_user)
):
    """执行匹配"""
    return await MatchService.perform_match(request)


@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "rk"}