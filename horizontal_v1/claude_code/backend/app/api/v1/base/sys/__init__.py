"""System management API router."""

from fastapi import APIRouter

from app.api.v1.base.sys.log import router as log_router
from app.api.v1.base.sys.param import router as param_router

router = APIRouter(prefix="/sys", tags=["System"])

router.include_router(param_router)
router.include_router(log_router)

# Additional routers will be added:
# - user router
# - role router
# - menu router
# - department router
