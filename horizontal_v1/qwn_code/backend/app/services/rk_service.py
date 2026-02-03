from app.db.dao.rk_dao import (
    VendorDAO, VendorContactDAO, CustomerDAO, CustomerContactDAO, 
    SupplyDAO, DemandDAO, MatchResultDAO
)
from app.db.session import get_db_session
from typing import Optional, List
from app.schemas.rk import (
    VendorResponse, CustomerResponse, SupplyResponse, DemandResponse,
    MatchRequest, MatchResponse, AnalysisRequest, AnalysisResponse
)
from app.core.config.settings import settings
import httpx
import asyncio


class VendorService:
    """供应商服务"""
    
    @staticmethod
    async def get_vendor_by_id(vendor_id: int) -> Optional[VendorResponse]:
        """根据ID获取供应商"""
        async for db in get_db_session():
            vendor = await VendorDAO.get_by_id(db, vendor_id)
            if vendor:
                return VendorResponse(
                    id=vendor.id,
                    name=vendor.name,
                    code=vendor.code,
                    folder_id=vendor.folder_id,
                    description=vendor.description,
                    created_at=vendor.created_at,
                    updated_at=vendor.updated_at
                )
            return None
    
    @staticmethod
    async def get_vendor_by_code(code: str) -> Optional[VendorResponse]:
        """根据编码获取供应商"""
        async for db in get_db_session():
            vendor = await VendorDAO.get_by_code(db, code)
            if vendor:
                return VendorResponse(
                    id=vendor.id,
                    name=vendor.name,
                    code=vendor.code,
                    folder_id=vendor.folder_id,
                    description=vendor.description,
                    created_at=vendor.created_at,
                    updated_at=vendor.updated_at
                )
            return None
    
    @staticmethod
    async def create_vendor(vendor_data: dict) -> VendorResponse:
        """创建供应商"""
        async for db in get_db_session():
            vendor = await VendorDAO.create(db, vendor_data)
            return VendorResponse(
                id=vendor.id,
                name=vendor.name,
                code=vendor.code,
                folder_id=vendor.folder_id,
                description=vendor.description,
                created_at=vendor.created_at,
                updated_at=vendor.updated_at
            )
    
    @staticmethod
    async def update_vendor(vendor_id: int, update_data: dict) -> Optional[VendorResponse]:
        """更新供应商"""
        async for db in get_db_session():
            vendor = await VendorDAO.update(db, vendor_id, update_data)
            if vendor:
                return VendorResponse(
                    id=vendor.id,
                    name=vendor.name,
                    code=vendor.code,
                    folder_id=vendor.folder_id,
                    description=vendor.description,
                    created_at=vendor.created_at,
                    updated_at=vendor.updated_at
                )
            return None
    
    @staticmethod
    async def delete_vendor(vendor_id: int) -> bool:
        """删除供应商"""
        async for db in get_db_session():
            return await VendorDAO.delete(db, vendor_id)


class CustomerService:
    """客户服务"""
    
    @staticmethod
    async def get_customer_by_id(customer_id: int) -> Optional[CustomerResponse]:
        """根据ID获取客户"""
        async for db in get_db_session():
            customer = await CustomerDAO.get_by_id(db, customer_id)
            if customer:
                return CustomerResponse(
                    id=customer.id,
                    name=customer.name,
                    code=customer.code,
                    address=customer.address,
                    postcode=customer.postcode,
                    description=customer.description,
                    created_at=customer.created_at,
                    updated_at=customer.updated_at
                )
            return None
    
    @staticmethod
    async def get_customer_by_code(code: str) -> Optional[CustomerResponse]:
        """根据编码获取客户"""
        async for db in get_db_session():
            customer = await CustomerDAO.get_by_code(db, code)
            if customer:
                return CustomerResponse(
                    id=customer.id,
                    name=customer.name,
                    code=customer.code,
                    address=customer.address,
                    postcode=customer.postcode,
                    description=customer.description,
                    created_at=customer.created_at,
                    updated_at=customer.updated_at
                )
            return None
    
    @staticmethod
    async def create_customer(customer_data: dict) -> CustomerResponse:
        """创建客户"""
        async for db in get_db_session():
            customer = await CustomerDAO.create(db, customer_data)
            return CustomerResponse(
                id=customer.id,
                name=customer.name,
                code=customer.code,
                address=customer.address,
                postcode=customer.postcode,
                description=customer.description,
                created_at=customer.created_at,
                updated_at=customer.updated_at
            )
    
    @staticmethod
    async def update_customer(customer_id: int, update_data: dict) -> Optional[CustomerResponse]:
        """更新客户"""
        async for db in get_db_session():
            customer = await CustomerDAO.update(db, customer_id, update_data)
            if customer:
                return CustomerResponse(
                    id=customer.id,
                    name=customer.name,
                    code=customer.code,
                    address=customer.address,
                    postcode=customer.postcode,
                    description=customer.description,
                    created_at=customer.created_at,
                    updated_at=customer.updated_at
                )
            return None
    
    @staticmethod
    async def delete_customer(customer_id: int) -> bool:
        """删除客户"""
        async for db in get_db_session():
            return await CustomerDAO.delete(db, customer_id)


class SupplyService:
    """简历服务"""
    
    @staticmethod
    async def get_supply_by_id(supply_id: int) -> Optional[SupplyResponse]:
        """根据ID获取简历"""
        async for db in get_db_session():
            supply = await SupplyDAO.get_by_id(db, supply_id)
            if supply:
                return SupplyResponse(
                    id=supply.id,
                    vendor_id=supply.vendor_id,
                    name=supply.name,
                    path=supply.path,
                    file_name=supply.file_name,
                    file_id=supply.file_id,
                    owner_id=supply.owner_id,
                    content_confirm=supply.content_confirm,
                    version=supply.version,
                    acdtc=supply.acdtc,
                    contracted_member=supply.contracted_member,
                    task_status=supply.task_status,
                    price_update_task_date=supply.price_update_task_date,
                    price_update=supply.price_update,
                    price_original=supply.price_original,
                    created_at=supply.created_at,
                    updated_at=supply.updated_at
                )
            return None
    
    @staticmethod
    async def create_supply(supply_data: dict) -> SupplyResponse:
        """创建简历"""
        async for db in get_db_session():
            supply = await SupplyDAO.create(db, supply_data)
            return SupplyResponse(
                id=supply.id,
                vendor_id=supply.vendor_id,
                name=supply.name,
                path=supply.path,
                file_name=supply.file_name,
                file_id=supply.file_id,
                owner_id=supply.owner_id,
                content_confirm=supply.content_confirm,
                version=supply.version,
                acdtc=supply.acdtc,
                contracted_member=supply.contracted_member,
                task_status=supply.task_status,
                price_update_task_date=supply.price_update_task_date,
                price_update=supply.price_update,
                price_original=supply.price_original,
                created_at=supply.created_at,
                updated_at=supply.updated_at
            )
    
    @staticmethod
    async def update_supply(supply_id: int, update_data: dict) -> Optional[SupplyResponse]:
        """更新简历"""
        async for db in get_db_session():
            supply = await SupplyDAO.update(db, supply_id, update_data)
            if supply:
                return SupplyResponse(
                    id=supply.id,
                    vendor_id=supply.vendor_id,
                    name=supply.name,
                    path=supply.path,
                    file_name=supply.file_name,
                    file_id=supply.file_id,
                    owner_id=supply.owner_id,
                    content_confirm=supply.content_confirm,
                    version=supply.version,
                    acdtc=supply.acdtc,
                    contracted_member=supply.contracted_member,
                    task_status=supply.task_status,
                    price_update_task_date=supply.price_update_task_date,
                    price_update=supply.price_update,
                    price_original=supply.price_original,
                    created_at=supply.created_at,
                    updated_at=supply.updated_at
                )
            return None
    
    @staticmethod
    async def delete_supply(supply_id: int) -> bool:
        """删除简历"""
        async for db in get_db_session():
            return await SupplyDAO.delete(db, supply_id)
    
    @staticmethod
    async def trigger_analysis(supply_id: int) -> AnalysisResponse:
        """触发简历分析"""
        try:
            # 调用第三方分析服务
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.THIRD_PARTY_ANALYSIS_URL}/v1/supply/resume_analysis",
                    json={"supply_id": supply_id},
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    return AnalysisResponse(success=True, message="分析已触发")
                else:
                    return AnalysisResponse(success=False, message=f"分析触发失败: {response.text}")
        except Exception as e:
            return AnalysisResponse(success=False, message=f"分析触发异常: {str(e)}")


class DemandService:
    """需求服务"""
    
    @staticmethod
    async def get_demand_by_id(demand_id: int) -> Optional[DemandResponse]:
        """根据ID获取需求"""
        async for db in get_db_session():
            demand = await DemandDAO.get_by_id(db, demand_id)
            if demand:
                return DemandResponse(
                    id=demand.id,
                    customer_id=demand.customer_id,
                    name=demand.name,
                    remark=demand.remark,
                    unit_price_max=demand.unit_price_max,
                    japanese_level=demand.japanese_level,
                    english_level=demand.english_level,
                    citizenship=demand.citizenship,
                    work_location=demand.work_location,
                    work_percent=demand.work_percent,
                    owner_id=demand.owner_id,
                    version=demand.version,
                    analysis_status=demand.analysis_status,
                    created_at=demand.created_at,
                    updated_at=demand.updated_at
                )
            return None
    
    @staticmethod
    async def create_demand(demand_data: dict) -> DemandResponse:
        """创建需求"""
        async for db in get_db_session():
            demand = await DemandDAO.create(db, demand_data)
            return DemandResponse(
                id=demand.id,
                customer_id=demand.customer_id,
                name=demand.name,
                remark=demand.remark,
                unit_price_max=demand.unit_price_max,
                japanese_level=demand.japanese_level,
                english_level=demand.english_level,
                citizenship=demand.citizenship,
                work_location=demand.work_location,
                work_percent=demand.work_percent,
                owner_id=demand.owner_id,
                version=demand.version,
                analysis_status=demand.analysis_status,
                created_at=demand.created_at,
                updated_at=demand.updated_at
            )
    
    @staticmethod
    async def update_demand(demand_id: int, update_data: dict) -> Optional[DemandResponse]:
        """更新需求"""
        async for db in get_db_session():
            demand = await DemandDAO.update(db, demand_id, update_data)
            if demand:
                return DemandResponse(
                    id=demand.id,
                    customer_id=demand.customer_id,
                    name=demand.name,
                    remark=demand.remark,
                    unit_price_max=demand.unit_price_max,
                    japanese_level=demand.japanese_level,
                    english_level=demand.english_level,
                    citizenship=demand.citizenship,
                    work_location=demand.work_location,
                    work_percent=demand.work_percent,
                    owner_id=demand.owner_id,
                    version=demand.version,
                    analysis_status=demand.analysis_status,
                    created_at=demand.created_at,
                    updated_at=demand.updated_at
                )
            return None
    
    @staticmethod
    async def delete_demand(demand_id: int) -> bool:
        """删除需求"""
        async for db in get_db_session():
            return await DemandDAO.delete(db, demand_id)


class MatchService:
    """匹配服务"""
    
    @staticmethod
    async def perform_match(match_request: MatchRequest) -> MatchResponse:
        """执行匹配"""
        try:
            # 调用第三方匹配服务
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.THIRD_PARTY_ANALYSIS_URL}/v1/supply/match_start",
                    json={
                        "demand_id": match_request.demand_id,
                        "supply_ids": match_request.supply_ids,
                        "role_list": match_request.role_list,
                        "flag_data": match_request.flag_data
                    },
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    return MatchResponse(success=True, message="匹配已触发", match_results=[])
                else:
                    return MatchResponse(success=False, message=f"匹配触发失败: {response.text}")
        except Exception as e:
            return MatchResponse(success=False, message=f"匹配触发异常: {str(e)}")