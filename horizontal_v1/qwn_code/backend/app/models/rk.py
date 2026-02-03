from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base, TimestampMixin


class Vendor(Base, TimestampMixin):
    """供应商表"""
    __tablename__ = "rk_vendor"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, comment="供应商名称")
    code = Column(String(100), unique=True, nullable=False, comment="供应商编码")
    folder_id = Column(String(200), comment="SharePoint文件夹ID")
    description = Column(Text, comment="供应商描述")


class VendorContact(Base, TimestampMixin):
    """供应商联系人表"""
    __tablename__ = "rk_vendor_contact"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("rk_vendor.id"), nullable=False, comment="供应商ID")
    name = Column(String(100), nullable=False, comment="联系人姓名")
    email = Column(String(100), comment="联系人邮箱")
    phone = Column(String(20), comment="联系人电话")
    position = Column(String(100), comment="联系人职位")
    is_primary = Column(Boolean, default=False, comment="是否为主要联系人")

    vendor = relationship("Vendor", back_populates="contacts")


class Customer(Base, TimestampMixin):
    """客户表"""
    __tablename__ = "rk_customer"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, comment="客户名称")
    code = Column(String(100), unique=True, nullable=False, comment="客户编码")
    address = Column(String(500), comment="客户地址")
    postcode = Column(String(20), comment="邮政编码")
    description = Column(Text, comment="客户描述")


class CustomerContact(Base, TimestampMixin):
    """客户联系人表"""
    __tablename__ = "rk_customer_contact"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("rk_customer.id"), nullable=False, comment="客户ID")
    name = Column(String(100), nullable=False, comment="联系人姓名")
    email = Column(String(100), comment="联系人邮箱")
    phone = Column(String(20), comment="联系人电话")
    position = Column(String(100), comment="联系人职位")
    is_primary = Column(Boolean, default=False, comment="是否为主要联系人")

    customer = relationship("Customer", back_populates="contacts")


class Supply(Base, TimestampMixin):
    """简历表"""
    __tablename__ = "rk_supply"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("rk_vendor.id"), nullable=False, comment="供应商ID")
    name = Column(String(200), comment="简历名称")
    path = Column(String(500), comment="文件路径")
    file_name = Column(String(200), comment="文件名")
    file_id = Column(String(200), comment="文件ID")
    owner_id = Column(Integer, comment="所有者ID")
    content_confirm = Column(Integer, default=1, comment="内容确认状态")
    version = Column(Integer, default=1, comment="版本号")
    acdtc = Column(String(200), comment="ACDTC字段")
    contracted_member = Column(String(200), comment="签约成员")
    task_status = Column(String(50), default="0000000000000010", comment="任务状态")
    price_update_task_date = Column(DateTime, comment="价格更新任务日期")
    price_update = Column(Float, comment="更新价格")
    price_original = Column(Float, comment="原始价格")
    active = Column(Boolean, default=True, comment="是否激活")
    analysis_status = Column(String(50), default="INIT", comment="分析状态")
    contact_analysis_status = Column(String(50), comment="联系方式分析状态")
    warning_msg = Column(Text, comment="警告信息")
    start_work_date = Column(String(20), comment="开始工作日期")
    nearest_station = Column(String(100), comment="最近车站")
    specialty = Column(String(200), comment="专业技能")
    work_percent = Column(Integer, comment="工作百分比")
    supply_user_citizenship = Column(String(100), comment="用户国籍")
    japanese_level = Column(String(50), comment="日语等级")
    english_level = Column(String(50), comment="英语等级")

    vendor = relationship("Vendor")


class Demand(Base, TimestampMixin):
    """需求表"""
    __tablename__ = "rk_demand"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("rk_customer.id"), nullable=False, comment="客户ID")
    name = Column(String(200), comment="需求名称")
    remark = Column(Text, comment="需求备注")
    unit_price_max = Column(Float, comment="最高单价")
    japanese_level = Column(String(50), comment="日语等级要求")
    english_level = Column(String(50), comment="英语等级要求")
    citizenship = Column(String(100), comment="国籍要求")
    work_location = Column(String(200), comment="工作地点")
    work_percent = Column(Integer, comment="工作占比")
    owner_id = Column(Integer, comment="所有者ID")
    version = Column(Integer, default=1, comment="版本号")
    active = Column(Boolean, default=True, comment="是否激活")
    analysis_status = Column(String(50), default="INIT", comment="分析状态")

    customer = relationship("Customer")


class MatchResult(Base, TimestampMixin):
    """匹配结果表"""
    __tablename__ = "rk_match_result"

    id = Column(Integer, primary_key=True, index=True)
    demand_id = Column(Integer, ForeignKey("rk_demand.id"), nullable=False, comment="需求ID")
    supply_id = Column(Integer, ForeignKey("rk_supply.id"), nullable=False, comment="简历ID")
    score = Column(Float, comment="匹配分数")
    reason = Column(Text, comment="匹配理由")
    status = Column(String(50), default="PENDING", comment="匹配状态")
    matched_by = Column(Integer, comment="匹配操作人ID")

    demand = relationship("Demand")
    supply = relationship("Supply")


class Notice(Base, TimestampMixin):
    """通知表"""
    __tablename__ = "rk_notice"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), comment="通知标题")
    content = Column(Text, comment="通知内容")
    type = Column(String(50), comment="通知类型")
    recipient_id = Column(Integer, comment="接收者ID")
    is_read = Column(Boolean, default=False, comment="是否已读")
    read_time = Column(DateTime, comment="阅读时间")


# 添加关系定义
Vendor.contacts = relationship("VendorContact", order_by=VendorContact.id, back_populates="vendor")
Customer.contacts = relationship("CustomerContact", order_by=CustomerContact.id, back_populates="customer")