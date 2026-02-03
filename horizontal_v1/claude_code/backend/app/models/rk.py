"""
RK (Core Business) entities.

Supply, Demand, Case, Customer, Vendor and related entities.

Reference:
- assistant_py/app/v1/entity/supply.py
- assistant_py/app/v1/entity/demand.py
- assistant_py/app/v1/entity/case.py
- Wiki: 数据管理/实体模型/核心业务实体/核心业务实体.md
"""

import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import BusinessBase, TimestampMixin


# ==================== Enums ====================


class AnalysisStatus(enum.Enum):
    """Analysis status enum for Supply/Demand."""

    ANALYSIS_START = "analysis_start"
    ANALYSIS_DONE = "analysis_done"
    ANALYSIS_ERROR = "analysis_error"
    CONTACT_ANALYSIS_START = "contact_analysis_start"
    CONTACT_ANALYSIS_DONE = "contact_analysis_done"
    CONTACT_ANALYSIS_ERROR = "contact_analysis_error"
    MATCH_START = "match_start"
    MATCH_DONE = "match_done"
    MATCH_ERROR = "match_error"


# Case status level mapping (for status machine)
CASE_STATUS_LEVEL = {
    "待确认": 1,
    "提案可否确认": 2,
    "提案济": 3,
    "1/2提案济": 4,
    "1/3提案济": 5,
    "面试调整中": 6,
    "1/2面试调整中": 7,
    "1/3面试调整中": 8,
    "面试设定济": 9,
    "1/2面试设定济": 10,
    "1/3面试设定济": 11,
    "结果等待": 12,
    "1/2结果等待": 13,
    "1/3结果等待": 14,
    "2/2提案济": 15,
    "2/3提案济": 16,
    "2/2面试调整中": 17,
    "2/3面试调整中": 18,
    "2/2面试设定济": 19,
    "2/3面试设定济": 20,
    "2/2结果等待": 21,
    "2/3结果等待": 22,
    "3/3提案济": 23,
    "3/3面试调整中": 24,
    "3/3面试设定济": 25,
    "3/3结果等待": 26,
    "条件交涉": 27,
    "受注": 28,
    "入場処理": 29,
    "情况确认": 30,
    "退場処理": 31,
}

CASE_TIAOJIAN_LEVEL = 27
CASE_SHOUZHU_LEVEL = 28
CASE_MAX_INTERVIEW = 26
CASE_INIT_LEVEL = 1
CASE_NOT_COMPARE = [k for k, v in CASE_STATUS_LEVEL.items() if v >= 28]


# ==================== Customer & Vendor ====================


class RkCustomer(Base, BusinessBase):
    """
    Customer entity.

    Table: rk_customer
    """

    __tablename__ = "rk_customer"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="Code")
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="Name")
    director: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="Legal representative"
    )
    address: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="Address"
    )
    check: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True, comment="Needs admin confirmation"
    )
    checkRemark: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="Check remark"
    )
    remark: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Remark")
    customerStatus1: Mapped[str | None] = mapped_column(String(50), nullable=True)
    customerStatus2: Mapped[str | None] = mapped_column(String(50), nullable=True)
    customerStatus3: Mapped[str | None] = mapped_column(String(50), nullable=True)
    customerStatus4: Mapped[str | None] = mapped_column(String(50), nullable=True)
    customerStatus5: Mapped[str | None] = mapped_column(String(50), nullable=True)
    customerStatus6: Mapped[str | None] = mapped_column(String(50), nullable=True)
    customerStatus7: Mapped[str | None] = mapped_column(String(50), nullable=True)
    customerStatus8: Mapped[str | None] = mapped_column(String(50), nullable=True)
    customerStatus9: Mapped[str | None] = mapped_column(String(50), nullable=True)
    customerStatus10: Mapped[str | None] = mapped_column(String(50), nullable=True)
    enterpriseId: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="Enterprise ID"
    )


class RkCustomerContact(Base, BusinessBase):
    """
    Customer contact entity.

    Table: rk_customer_contact
    """

    __tablename__ = "rk_customer_contact"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customerId: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="Customer ID"
    )
    name: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="Name")
    email: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="Email"
    )
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="Phone")
    address: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="Address"
    )
    postal: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="Postal code"
    )
    position: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="Position"
    )
    default: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True, comment="Is default"
    )
    remark: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Remark")


class RkVendor(Base, BusinessBase):
    """
    Vendor entity.

    Table: rk_vendor
    """

    __tablename__ = "rk_vendor"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="Corporate number"
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="Name")
    director: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="Legal representative"
    )
    address: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="Address"
    )
    check: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True, comment="Needs admin confirmation"
    )
    checkRemark: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="Check remark"
    )
    remark: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Remark")
    vendorStatus1: Mapped[str | None] = mapped_column(String(50), nullable=True)
    vendorStatus2: Mapped[str | None] = mapped_column(String(50), nullable=True)
    vendorStatus3: Mapped[str | None] = mapped_column(String(50), nullable=True)
    vendorStatus4: Mapped[str | None] = mapped_column(String(50), nullable=True)
    vendorStatus5: Mapped[str | None] = mapped_column(String(50), nullable=True)
    vendorStatus6: Mapped[str | None] = mapped_column(String(50), nullable=True)
    vendorStatus7: Mapped[str | None] = mapped_column(String(50), nullable=True)
    vendorStatus8: Mapped[str | None] = mapped_column(String(50), nullable=True)
    vendorStatus9: Mapped[str | None] = mapped_column(String(50), nullable=True)
    vendorStatus10: Mapped[str | None] = mapped_column(String(50), nullable=True)
    enterpriseId: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="Enterprise ID"
    )
    folderId: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="SharePoint folder ID"
    )
    folderUrl: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="SharePoint folder URL"
    )
    deltaLink: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="Delta link for updates"
    )
    folderUpdate: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, comment="Folder update time"
    )


class RkVendorContact(Base, BusinessBase):
    """
    Vendor contact entity.

    Table: rk_vendor_contact
    """

    __tablename__ = "rk_vendor_contact"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vendorId: Mapped[int] = mapped_column(Integer, nullable=False, comment="Vendor ID")
    name: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="Name")
    email: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="Email"
    )
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="Phone")
    address: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="Address"
    )
    postal: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="Postal code"
    )
    position: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="Position"
    )
    default: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True, comment="Is default"
    )
    remark: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Remark")


# ==================== Supply (Resume) ====================


class RkSupply(Base, BusinessBase):
    """
    Supply (Resume) entity.

    Table: rk_supply
    """

    __tablename__ = "rk_supply"
    __table_args__ = (
        Index("ix_rk_supply_code", "code", unique=True),
        Index("ix_rk_supply_vendor_id", "vendorId"),
        Index("ix_rk_supply_user_id", "userId"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    path: Mapped[str | None] = mapped_column(Text, nullable=True, comment="SharePoint path")
    price: Mapped[float | None] = mapped_column(Float, nullable=True, comment="Price")
    skillScores: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Skill analysis scores"
    )
    resumeRes: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Resume extraction result"
    )
    vendorId: Mapped[int | None] = mapped_column(Integer, nullable=True)
    vendorContactId: Mapped[int | None] = mapped_column(Integer, nullable=True)
    userId: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="Uploader ID"
    )
    supplyUserName: Mapped[str | None] = mapped_column(
        String(100), default="", nullable=True, comment="Resume owner name"
    )
    namePinyin: Mapped[str | None] = mapped_column(String(50), default="", nullable=True)
    lastName: Mapped[str | None] = mapped_column(String(50), default="", nullable=True)
    firstName: Mapped[str | None] = mapped_column(String(50), default="", nullable=True)
    supplyUserAge: Mapped[str | None] = mapped_column(String(20), default="", nullable=True)
    supplyUserGender: Mapped[str | None] = mapped_column(
        String(20), default="", nullable=True
    )
    supplyUserCitizenship: Mapped[str | None] = mapped_column(
        String(50), default="", nullable=True
    )
    supplyBirthday: Mapped[str | None] = mapped_column(
        String(20), default="", nullable=True
    )
    score: Mapped[float | None] = mapped_column(Float, nullable=True, comment="Resume score")
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    fileName: Mapped[str | None] = mapped_column(String(255), default="", nullable=True)
    fileId: Mapped[str | None] = mapped_column(String(255), default="", nullable=True)
    fileUpdate: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    duplicateStatus: Mapped[int | None] = mapped_column(Integer, default=0, nullable=True)
    duplicateContent: Mapped[str | None] = mapped_column(
        String(255), default="", nullable=True
    )
    startWorkDate: Mapped[str | None] = mapped_column(String(20), nullable=True)
    nearestStation: Mapped[str | None] = mapped_column(
        String(100), default="", nullable=True
    )
    workMode: Mapped[str | None] = mapped_column(String(100), default="", nullable=True)
    specialty: Mapped[str | None] = mapped_column(String(200), default="", nullable=True)
    yearsOfWork: Mapped[float | None] = mapped_column(Float, nullable=True)
    availableDate: Mapped[str | None] = mapped_column(
        String(100), default="", nullable=True
    )
    skillx: Mapped[str | None] = mapped_column(
        Text, default="", nullable=True, comment="X-axis skill"
    )
    skilly: Mapped[str | None] = mapped_column(
        Text, default="", nullable=True, comment="Y-axis skill"
    )
    skillz: Mapped[str | None] = mapped_column(
        Text, default="", nullable=True, comment="Z-axis skill"
    )
    japaneseLevel: Mapped[str | None] = mapped_column(String(20), default="", nullable=True)
    englishLevel: Mapped[str | None] = mapped_column(String(20), default="", nullable=True)
    errorStatus: Mapped[str | None] = mapped_column(String(255), default="", nullable=True)
    fatherSkill: Mapped[str | None] = mapped_column(String(255), nullable=True)
    fileMd5: Mapped[str | None] = mapped_column(String(255), default="", nullable=True)
    contentConfirm: Mapped[int | None] = mapped_column(Integer, default=0, nullable=True)
    role: Mapped[str | None] = mapped_column(String(100), default="", nullable=True)
    analysisVersion: Mapped[str | None] = mapped_column(
        String(100), default="", nullable=True
    )
    japaneseLevelAi: Mapped[str | None] = mapped_column(
        String(100), default="", nullable=True
    )
    englishLevelAi: Mapped[str | None] = mapped_column(
        String(100), default="", nullable=True
    )
    statusDetail: Mapped[str | None] = mapped_column(
        String(100), default="", nullable=True
    )
    caseStatus: Mapped[str | None] = mapped_column(String(100), default="", nullable=True)
    auditionDate: Mapped[str | None] = mapped_column(
        String(100), default="", nullable=True
    )
    auditionIdea: Mapped[str | None] = mapped_column(
        String(100), default="", nullable=True
    )
    resultExpectedDate: Mapped[str | None] = mapped_column(
        String(100), default="", nullable=True
    )
    auditionTime: Mapped[str | None] = mapped_column(
        String(100), default="", nullable=True
    )
    work_percent: Mapped[int | None] = mapped_column(Integer, nullable=True)
    version: Mapped[int | None] = mapped_column(Integer, default=1, nullable=True)
    analysis_status: Mapped[str | None] = mapped_column(
        String(100), default="", nullable=True
    )
    contact_analysis_status: Mapped[str | None] = mapped_column(
        String(100), default="", nullable=True
    )
    role_level: Mapped[str | None] = mapped_column(String(100), default="", nullable=True)
    role_level_reason: Mapped[str | None] = mapped_column(Text, default="", nullable=True)
    acdtc: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    contractedMember: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    price_update: Mapped[int | None] = mapped_column(Integer, nullable=True)
    price_original: Mapped[int | None] = mapped_column(Integer, default=0, nullable=True)
    price_update_task_date: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )
    task_status: Mapped[str | None] = mapped_column(
        String(50), default="0000000000000000", nullable=True
    )


class RkSupplyAi(Base, TimestampMixin):
    """
    Supply AI data entity.

    Stores AI-extracted data from resume.
    Table: rk_supply_ai
    """

    __tablename__ = "rk_supply_ai"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    supplyId: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    workExperience: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    basic: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    xRaw: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    yRaw: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    zRaw: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    xData: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    yData: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    zData: Mapped[dict | None] = mapped_column(JSONB, nullable=True)


# ==================== Demand ====================


class RkDemand(Base, BusinessBase):
    """
    Demand entity.

    Table: rk_demand
    """

    __tablename__ = "rk_demand"
    __table_args__ = (Index("ix_rk_demand_customer_id", "customerId"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    customerId: Mapped[int | None] = mapped_column(Integer, nullable=True)
    price: Mapped[int | None] = mapped_column(Integer, nullable=True)
    customerContactId: Mapped[int | None] = mapped_column(Integer, nullable=True)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
    workLocation: Mapped[str | None] = mapped_column(String(255), nullable=True)
    workMode: Mapped[str | None] = mapped_column(String(255), nullable=True)
    skillx: Mapped[str | None] = mapped_column(String(255), nullable=True)
    skilly: Mapped[str | None] = mapped_column(String(255), nullable=True)
    skillz: Mapped[str | None] = mapped_column(String(255), nullable=True)
    japaneseLevel: Mapped[str | None] = mapped_column(String(255), nullable=True)
    englishLevel: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[str | None] = mapped_column(String(255), nullable=True)
    changeStatus: Mapped[int | None] = mapped_column(Integer, default=1, nullable=True)
    fatherSkill: Mapped[str | None] = mapped_column(String(255), nullable=True)
    unitPriceMax: Mapped[int | None] = mapped_column(Integer, nullable=True)
    work_percent: Mapped[int | None] = mapped_column(Integer, nullable=True)
    citizenship: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role_list: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    version: Mapped[int | None] = mapped_column(Integer, default=1, nullable=True)
    have_match: Mapped[bool | None] = mapped_column(Boolean, default=False, nullable=True)
    analysis_status: Mapped[str | None] = mapped_column(
        String(100), default="", nullable=True
    )
    toBeConfirmed: Mapped[bool | None] = mapped_column(
        Boolean, default=False, nullable=True
    )


class RkDemandAi(Base, TimestampMixin):
    """
    Demand AI data entity.

    Table: rk_demand_ai
    """

    __tablename__ = "rk_demand_ai"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    demandId: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)


class RkDemandCondition(Base, TimestampMixin):
    """
    Demand condition entity.

    Table: rk_demand_condition
    """

    __tablename__ = "rk_demand_condition"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    demandId: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    conditionKey: Mapped[str | None] = mapped_column(String(100), nullable=True)
    conditionValue: Mapped[str | None] = mapped_column(Text, nullable=True)


# ==================== Case (Supply-Demand Link) ====================


class RkCase(Base, BusinessBase):
    """
    Case entity (Supply-Demand Link).

    Table: rk_supply_demand_link
    """

    __tablename__ = "rk_supply_demand_link"
    __table_args__ = (
        Index("ix_rk_case_supply_id", "supplyId"),
        Index("ix_rk_case_demand_id", "demandId"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    supplyId: Mapped[int | None] = mapped_column(Integer, nullable=True)
    demandId: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
    result: Mapped[str | None] = mapped_column(Text, nullable=True)
    k: Mapped[int | None] = mapped_column(Integer, nullable=True)
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    supplyDemandStatus1: Mapped[str | None] = mapped_column(String(50), nullable=True)
    supplyDemandStatus2: Mapped[str | None] = mapped_column(String(50), nullable=True)
    supplyDemandStatus3: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="Case status"
    )
    supplyDemandStatus4: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="Hidden status"
    )
    supplyDemandStatus5: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="Auto match status"
    )
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    tag: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    tagReason: Mapped[str | None] = mapped_column(Text, nullable=True)
    demandText: Mapped[str | None] = mapped_column(Text, nullable=True)
    years: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fatherSkill: Mapped[str | None] = mapped_column(String(255), nullable=True)
    demand_role: Mapped[str | None] = mapped_column(String(255), nullable=True)
    demand_version: Mapped[int | None] = mapped_column(Integer, default=0, nullable=True)
    supply_version: Mapped[int | None] = mapped_column(Integer, default=0, nullable=True)
    warning_msg: Mapped[dict | None] = mapped_column(JSONB, nullable=True)


class RkCaseStatus(Base, TimestampMixin):
    """
    Case status history entity.

    Table: rk_case_status
    """

    __tablename__ = "rk_case_status"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    remark: Mapped[str | None] = mapped_column(String(500), default="", nullable=True)
    active: Mapped[bool | None] = mapped_column(Boolean, default=True)


# ==================== Match Result ====================


class RkMatchResult(Base, BusinessBase):
    """
    Match result entity.

    Table: rk_match_res
    """

    __tablename__ = "rk_match_res"
    __table_args__ = (
        Index("ix_rk_match_res_demand_id", "demand_id"),
        Index("ix_rk_match_res_supply_id", "supply_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    demand_id: Mapped[int] = mapped_column(Integer, nullable=False)
    supply_id: Mapped[int] = mapped_column(Integer, nullable=False)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    warning_msg: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    demand_role: Mapped[str | None] = mapped_column(String(255), nullable=True)
    years_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    demand_version: Mapped[int | None] = mapped_column(Integer, default=0, nullable=True)
    supply_version: Mapped[int | None] = mapped_column(Integer, default=0, nullable=True)
    type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    msg: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    reject_type: Mapped[str | None] = mapped_column(String(50), default="", nullable=True)
    reject_reason: Mapped[str | None] = mapped_column(
        String(255), default="", nullable=True
    )


# ==================== Notice ====================


class RkNotice(Base, TimestampMixin):
    """
    Notice entity.

    Table: rk_notice
    """

    __tablename__ = "rk_notice"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    createdBy: Mapped[int | None] = mapped_column(Integer, nullable=True)
    departmentId: Mapped[int | None] = mapped_column(Integer, nullable=True)
    updatedBy: Mapped[int | None] = mapped_column(Integer, nullable=True)
    active: Mapped[bool | None] = mapped_column(Boolean, default=True)
    recieverId: Mapped[int | None] = mapped_column(Integer, nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    isRead: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    ownerId: Mapped[int | None] = mapped_column(Integer, nullable=True)
    toBeConfirmed: Mapped[bool | None] = mapped_column(Boolean, default=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    model: Mapped[str | None] = mapped_column(String(50), nullable=True)
    fromUser: Mapped[int | None] = mapped_column("from", Integer, nullable=True)
    type: Mapped[str | None] = mapped_column(String(50), default="", nullable=True)


# ==================== Shared Links ====================


class RkSharedLinks(Base, BusinessBase):
    """
    Shared links entity.

    Table: rk_shared_links
    """

    __tablename__ = "rk_shared_links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    resourceType: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="Resource type"
    )
    resourceId: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True, comment="Resource IDs"
    )
    shareToken: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="Share token"
    )
    expireAt: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="Expiration time"
    )


# ==================== Edit Record ====================


class RkSupplyEditRecord(Base, TimestampMixin):
    """
    Supply edit record entity.

    Table: rk_supply_edit_record
    """

    __tablename__ = "rk_supply_edit_record"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    supplyId: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    userId: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fieldName: Mapped[str | None] = mapped_column(String(100), nullable=True)
    oldValue: Mapped[str | None] = mapped_column(Text, nullable=True)
    newValue: Mapped[str | None] = mapped_column(Text, nullable=True)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)


# ==================== LLM Data ====================


class RkLlmData(Base, TimestampMixin):
    """
    LLM data entity for storing AI request/response.

    Table: rk_llm_data
    """

    __tablename__ = "rk_llm_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    requestId: Mapped[str | None] = mapped_column(
        String(100), nullable=True, index=True
    )
    requestType: Mapped[str | None] = mapped_column(String(50), nullable=True)
    requestData: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    responseData: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)


# ==================== Active Switch ====================


class RkActiveSwitch(Base, TimestampMixin):
    """
    Active switch entity for global data filtering.

    Table: rk_active
    """

    __tablename__ = "rk_active"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    userId: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


# ==================== Customer Column (Preferences) ====================


class RkCustomerColumn(Base, TimestampMixin):
    """
    Customer column preferences entity.

    Table: rk_customer_column
    """

    __tablename__ = "rk_customer_column"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    userId: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    tableName: Mapped[str | None] = mapped_column(String(100), nullable=True)
    columns: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
