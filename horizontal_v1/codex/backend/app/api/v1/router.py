from fastapi import APIRouter

from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.dict import router as dict_router
from backend.app.api.v1.dict_info_admin import router as dict_info_admin_router
from backend.app.api.v1.dict_type_admin import router as dict_type_admin_router
from backend.app.api.v1.health import router as health_router
from backend.app.api.v1.rbac import router as rbac_router
from backend.app.api.v1.rbac_depts import router as rbac_depts_router
from backend.app.api.v1.rbac_roles import router as rbac_roles_router
from backend.app.api.v1.rbac_users import router as rbac_users_router
from backend.app.api.v1.rk_customer import router as rk_customer_router
from backend.app.api.v1.rk_customer_column import router as rk_customer_column_router
from backend.app.api.v1.rk_active import router as rk_active_router
from backend.app.api.v1.rk_vendor import router as rk_vendor_router
from backend.app.api.v1.rk_vendor_contact import router as rk_vendor_contact_router
from backend.app.api.v1.rk_customer_contact import router as rk_customer_contact_router
from backend.app.api.v1.resume_callback import router as resume_callback_router
from backend.app.api.v1.supply import router as supply_router
from backend.app.api.v1.notice import router as notice_router
from backend.app.api.v1.sharepoint import router as sharepoint_router
from backend.app.api.v1.shared_links import router as shared_links_router
from backend.app.api.v1.chat import router as chat_router

router = APIRouter()
router.include_router(health_router)
router.include_router(auth_router)
router.include_router(rbac_router)
router.include_router(rbac_depts_router)
router.include_router(rbac_roles_router)
router.include_router(rbac_users_router)
router.include_router(dict_router)
router.include_router(dict_type_admin_router)
router.include_router(dict_info_admin_router)
router.include_router(rk_customer_router)
router.include_router(rk_customer_column_router)
router.include_router(rk_active_router)
router.include_router(rk_vendor_router)
router.include_router(rk_vendor_contact_router)
router.include_router(rk_customer_contact_router)
router.include_router(resume_callback_router)
router.include_router(supply_router)
router.include_router(notice_router)
router.include_router(sharepoint_router)
router.include_router(shared_links_router)
router.include_router(chat_router)
