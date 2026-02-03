from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.rk import Vendor, VendorContact, Customer, CustomerContact, Supply, Demand, MatchResult
from typing import Optional, List


class VendorDAO:
    """供应商数据访问对象"""
    
    @staticmethod
    async def get_by_id(db: AsyncSession, vendor_id: int) -> Optional[Vendor]:
        """根据ID获取供应商"""
        stmt = select(Vendor).where(Vendor.id == vendor_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_code(db: AsyncSession, code: str) -> Optional[Vendor]:
        """根据编码获取供应商"""
        stmt = select(Vendor).where(Vendor.code == code)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all(db: AsyncSession) -> List[Vendor]:
        """获取所有供应商"""
        stmt = select(Vendor)
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def create(db: AsyncSession, vendor_data: dict) -> Vendor:
        """创建供应商"""
        db_vendor = Vendor(**vendor_data)
        db.add(db_vendor)
        await db.commit()
        await db.refresh(db_vendor)
        return db_vendor
    
    @staticmethod
    async def update(db: AsyncSession, vendor_id: int, update_data: dict) -> Vendor:
        """更新供应商"""
        db_vendor = await VendorDAO.get_by_id(db, vendor_id)
        if not db_vendor:
            return None
        
        for key, value in update_data.items():
            setattr(db_vendor, key, value)
        
        await db.commit()
        await db.refresh(db_vendor)
        return db_vendor
    
    @staticmethod
    async def delete(db: AsyncSession, vendor_id: int) -> bool:
        """删除供应商"""
        db_vendor = await VendorDAO.get_by_id(db, vendor_id)
        if not db_vendor:
            return False
        
        await db.delete(db_vendor)
        await db.commit()
        return True


class VendorContactDAO:
    """供应商联系人数据访问对象"""
    
    @staticmethod
    async def get_by_id(db: AsyncSession, contact_id: int) -> Optional[VendorContact]:
        """根据ID获取供应商联系人"""
        stmt = select(VendorContact).where(VendorContact.id == contact_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_vendor_id(db: AsyncSession, vendor_id: int) -> List[VendorContact]:
        """根据供应商ID获取联系人"""
        stmt = select(VendorContact).where(VendorContact.vendor_id == vendor_id)
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def create(db: AsyncSession, contact_data: dict) -> VendorContact:
        """创建供应商联系人"""
        db_contact = VendorContact(**contact_data)
        db.add(db_contact)
        await db.commit()
        await db.refresh(db_contact)
        return db_contact
    
    @staticmethod
    async def update(db: AsyncSession, contact_id: int, update_data: dict) -> VendorContact:
        """更新供应商联系人"""
        db_contact = await VendorContactDAO.get_by_id(db, contact_id)
        if not db_contact:
            return None
        
        for key, value in update_data.items():
            setattr(db_contact, key, value)
        
        await db.commit()
        await db.refresh(db_contact)
        return db_contact
    
    @staticmethod
    async def delete(db: AsyncSession, contact_id: int) -> bool:
        """删除供应商联系人"""
        db_contact = await VendorContactDAO.get_by_id(db, contact_id)
        if not db_contact:
            return False
        
        await db.delete(db_contact)
        await db.commit()
        return True


class CustomerDAO:
    """客户数据访问对象"""
    
    @staticmethod
    async def get_by_id(db: AsyncSession, customer_id: int) -> Optional[Customer]:
        """根据ID获取客户"""
        stmt = select(Customer).where(Customer.id == customer_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_code(db: AsyncSession, code: str) -> Optional[Customer]:
        """根据编码获取客户"""
        stmt = select(Customer).where(Customer.code == code)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all(db: AsyncSession) -> List[Customer]:
        """获取所有客户"""
        stmt = select(Customer)
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def create(db: AsyncSession, customer_data: dict) -> Customer:
        """创建客户"""
        db_customer = Customer(**customer_data)
        db.add(db_customer)
        await db.commit()
        await db.refresh(db_customer)
        return db_customer
    
    @staticmethod
    async def update(db: AsyncSession, customer_id: int, update_data: dict) -> Customer:
        """更新客户"""
        db_customer = await CustomerDAO.get_by_id(db, customer_id)
        if not db_customer:
            return None
        
        for key, value in update_data.items():
            setattr(db_customer, key, value)
        
        await db.commit()
        await db.refresh(db_customer)
        return db_customer
    
    @staticmethod
    async def delete(db: AsyncSession, customer_id: int) -> bool:
        """删除客户"""
        db_customer = await CustomerDAO.get_by_id(db, customer_id)
        if not db_customer:
            return False
        
        await db.delete(db_customer)
        await db.commit()
        return True


class CustomerContactDAO:
    """客户联系人数据访问对象"""
    
    @staticmethod
    async def get_by_id(db: AsyncSession, contact_id: int) -> Optional[CustomerContact]:
        """根据ID获取客户联系人"""
        stmt = select(CustomerContact).where(CustomerContact.id == contact_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_customer_id(db: AsyncSession, customer_id: int) -> List[CustomerContact]:
        """根据客户ID获取联系人"""
        stmt = select(CustomerContact).where(CustomerContact.customer_id == customer_id)
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def create(db: AsyncSession, contact_data: dict) -> CustomerContact:
        """创建客户联系人"""
        db_contact = CustomerContact(**contact_data)
        db.add(db_contact)
        await db.commit()
        await db.refresh(db_contact)
        return db_contact
    
    @staticmethod
    async def update(db: AsyncSession, contact_id: int, update_data: dict) -> CustomerContact:
        """更新客户联系人"""
        db_contact = await CustomerContactDAO.get_by_id(db, contact_id)
        if not db_contact:
            return None
        
        for key, value in update_data.items():
            setattr(db_contact, key, value)
        
        await db.commit()
        await db.refresh(db_contact)
        return db_contact
    
    @staticmethod
    async def delete(db: AsyncSession, contact_id: int) -> bool:
        """删除客户联系人"""
        db_contact = await CustomerContactDAO.get_by_id(db, contact_id)
        if not db_contact:
            return False
        
        await db.delete(db_contact)
        await db.commit()
        return True


class SupplyDAO:
    """简历数据访问对象"""
    
    @staticmethod
    async def get_by_id(db: AsyncSession, supply_id: int) -> Optional[Supply]:
        """根据ID获取简历"""
        stmt = select(Supply).where(Supply.id == supply_id).options(
            selectinload(Supply.vendor)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all(db: AsyncSession) -> List[Supply]:
        """获取所有简历"""
        stmt = select(Supply).options(selectinload(Supply.vendor))
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def get_by_vendor_id(db: AsyncSession, vendor_id: int) -> List[Supply]:
        """根据供应商ID获取简历"""
        stmt = select(Supply).where(Supply.vendor_id == vendor_id).options(
            selectinload(Supply.vendor)
        )
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def create(db: AsyncSession, supply_data: dict) -> Supply:
        """创建简历"""
        db_supply = Supply(**supply_data)
        db.add(db_supply)
        await db.commit()
        await db.refresh(db_supply)
        return db_supply
    
    @staticmethod
    async def update(db: AsyncSession, supply_id: int, update_data: dict) -> Supply:
        """更新简历"""
        db_supply = await SupplyDAO.get_by_id(db, supply_id)
        if not db_supply:
            return None
        
        for key, value in update_data.items():
            setattr(db_supply, key, value)
        
        await db.commit()
        await db.refresh(db_supply)
        return db_supply
    
    @staticmethod
    async def delete(db: AsyncSession, supply_id: int) -> bool:
        """删除简历"""
        db_supply = await SupplyDAO.get_by_id(db, supply_id)
        if not db_supply:
            return False
        
        await db.delete(db_supply)
        await db.commit()
        return True


class DemandDAO:
    """需求数据访问对象"""
    
    @staticmethod
    async def get_by_id(db: AsyncSession, demand_id: int) -> Optional[Demand]:
        """根据ID获取需求"""
        stmt = select(Demand).where(Demand.id == demand_id).options(
            selectinload(Demand.customer)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all(db: AsyncSession) -> List[Demand]:
        """获取所有需求"""
        stmt = select(Demand).options(selectinload(Demand.customer))
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def get_by_customer_id(db: AsyncSession, customer_id: int) -> List[Demand]:
        """根据客户ID获取需求"""
        stmt = select(Demand).where(Demand.customer_id == customer_id).options(
            selectinload(Demand.customer)
        )
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def create(db: AsyncSession, demand_data: dict) -> Demand:
        """创建需求"""
        db_demand = Demand(**demand_data)
        db.add(db_demand)
        await db.commit()
        await db.refresh(db_demand)
        return db_demand
    
    @staticmethod
    async def update(db: AsyncSession, demand_id: int, update_data: dict) -> Demand:
        """更新需求"""
        db_demand = await DemandDAO.get_by_id(db, demand_id)
        if not db_demand:
            return None
        
        for key, value in update_data.items():
            setattr(db_demand, key, value)
        
        await db.commit()
        await db.refresh(db_demand)
        return db_demand
    
    @staticmethod
    async def delete(db: AsyncSession, demand_id: int) -> bool:
        """删除需求"""
        db_demand = await DemandDAO.get_by_id(db, demand_id)
        if not db_demand:
            return False
        
        await db.delete(db_demand)
        await db.commit()
        return True


class MatchResultDAO:
    """匹配结果数据访问对象"""
    
    @staticmethod
    async def get_by_id(db: AsyncSession, match_id: int) -> Optional[MatchResult]:
        """根据ID获取匹配结果"""
        stmt = select(MatchResult).where(MatchResult.id == match_id).options(
            selectinload(MatchResult.demand), selectinload(MatchResult.supply)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_demand_id(db: AsyncSession, demand_id: int) -> List[MatchResult]:
        """根据需求ID获取匹配结果"""
        stmt = select(MatchResult).where(MatchResult.demand_id == demand_id).options(
            selectinload(MatchResult.demand), selectinload(MatchResult.supply)
        )
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def get_by_supply_id(db: AsyncSession, supply_id: int) -> List[MatchResult]:
        """根据简历ID获取匹配结果"""
        stmt = select(MatchResult).where(MatchResult.supply_id == supply_id).options(
            selectinload(MatchResult.demand), selectinload(MatchResult.supply)
        )
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def create(db: AsyncSession, match_data: dict) -> MatchResult:
        """创建匹配结果"""
        db_match = MatchResult(**match_data)
        db.add(db_match)
        await db.commit()
        await db.refresh(db_match)
        return db_match
    
    @staticmethod
    async def update(db: AsyncSession, match_id: int, update_data: dict) -> MatchResult:
        """更新匹配结果"""
        db_match = await MatchResultDAO.get_by_id(db, match_id)
        if not db_match:
            return None
        
        for key, value in update_data.items():
            setattr(db_match, key, value)
        
        await db.commit()
        await db.refresh(db_match)
        return db_match
    
    @staticmethod
    async def delete(db: AsyncSession, match_id: int) -> bool:
        """删除匹配结果"""
        db_match = await MatchResultDAO.get_by_id(db, match_id)
        if not db_match:
            return False
        
        await db.delete(db_match)
        await db.commit()
        return True