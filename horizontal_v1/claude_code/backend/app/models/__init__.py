"""SQLAlchemy models module."""

from app.models.base import (
    BusinessBase,
    SoftDeleteMixin,
    TimestampMixin,
    VersionMixin,
    to_dict,
)
from app.models.dict import DictInfo, DictType
from app.models.rk import (
    CASE_STATUS_LEVEL,
    AnalysisStatus,
    RkActiveSwitch,
    RkCase,
    RkCaseStatus,
    RkCustomer,
    RkCustomerColumn,
    RkCustomerContact,
    RkDemand,
    RkDemandAi,
    RkDemandCondition,
    RkLlmData,
    RkMatchResult,
    RkNotice,
    RkSharedLinks,
    RkSupply,
    RkSupplyAi,
    RkSupplyEditRecord,
    RkVendor,
    RkVendorContact,
)
from app.models.sys import (
    BaseSysConf,
    BaseSysDepartment,
    BaseSysLog,
    BaseSysMenu,
    BaseSysParam,
    BaseSysRole,
    BaseSysUser,
    BaseSysUserRole,
)

__all__ = [
    # Base mixins
    "TimestampMixin",
    "SoftDeleteMixin",
    "BusinessBase",
    "VersionMixin",
    "to_dict",
    # System models
    "BaseSysUser",
    "BaseSysRole",
    "BaseSysMenu",
    "BaseSysDepartment",
    "BaseSysUserRole",
    "BaseSysLog",
    "BaseSysParam",
    "BaseSysConf",
    # Dict models
    "DictType",
    "DictInfo",
    # RK models
    "AnalysisStatus",
    "CASE_STATUS_LEVEL",
    "RkCustomer",
    "RkCustomerContact",
    "RkVendor",
    "RkVendorContact",
    "RkSupply",
    "RkSupplyAi",
    "RkSupplyEditRecord",
    "RkDemand",
    "RkDemandAi",
    "RkDemandCondition",
    "RkCase",
    "RkCaseStatus",
    "RkMatchResult",
    "RkNotice",
    "RkSharedLinks",
    "RkLlmData",
    "RkActiveSwitch",
    "RkCustomerColumn",
]
