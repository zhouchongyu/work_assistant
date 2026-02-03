"""RK (Core Business) API router."""

from fastapi import APIRouter

from app.api.v1.rk.case import router as case_router
from app.api.v1.rk.customer import router as customer_router
from app.api.v1.rk.demand import router as demand_router
from app.api.v1.rk.notice import router as notice_router
from app.api.v1.rk.supply import router as supply_router
from app.api.v1.rk.vendor import router as vendor_router

router = APIRouter(prefix="/rk", tags=["RK"])

router.include_router(supply_router)
router.include_router(demand_router)
router.include_router(case_router)
router.include_router(customer_router)
router.include_router(vendor_router)
router.include_router(notice_router)
