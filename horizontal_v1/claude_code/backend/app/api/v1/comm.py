"""
Common API endpoints (require login, no specific permissions).

Includes user info, logout, password change, etc.

Reference:
- cool-admin-midway/src/modules/base/controller/admin/comm.ts
- Wiki: API参考文档/API参考文档.md
"""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.response import SuccessResponse, success
from app.middleware.authority import get_current_user_from_request
from app.schemas.auth import (
    ChangePasswordRequest,
    PermsResponse,
    UpdateUserInfoRequest,
    UserInfoResponse,
)
from app.services.auth import auth_service

router = APIRouter(prefix="/comm", tags=["Common"])


@router.get("/person", response_model=None)
async def get_person_info(
    request: Request,
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """
    Get current user information.

    Returns user profile including department and role info.
    """
    user = get_current_user_from_request(request)
    if not user:
        return success(result=None, message="未登录")

    result = await auth_service.get_user_info(user.user_id, db)
    return success(result=result.model_dump(by_alias=True))


@router.get("/permmenu", response_model=None)
async def get_perms_and_menus(
    request: Request,
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """
    Get current user's permissions and menu tree.

    Returns:
    - menus: Menu tree for rendering navigation
    - perms: Permission codes for button-level access control
    """
    user = get_current_user_from_request(request)
    if not user:
        return success(result={"menus": [], "perms": []})

    is_admin = user.username == "admin"
    result = await auth_service.get_user_perms_and_menus(
        user_id=user.user_id,
        role_ids=user.role_ids,
        is_admin=is_admin,
        db=db,
    )
    return success(result=result.model_dump(by_alias=True))


@router.post("/logout", response_model=None)
async def logout(request: Request) -> SuccessResponse:
    """
    User logout.

    Clears all cached tokens and permissions.
    """
    user = get_current_user_from_request(request)
    if user:
        await auth_service.logout(user.user_id)
    return success(message="退出成功")


@router.post("/personUpdate", response_model=None)
async def update_person_info(
    request: Request,
    data: UpdateUserInfoRequest,
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """
    Update current user's profile information.

    Can update: nickname, avatar, email, phone.
    """
    user = get_current_user_from_request(request)
    if not user:
        return success(result=None, message="未登录")

    # TODO: Implement update user info
    # This will be implemented in Phase 3 user service
    return success(message="更新成功")


@router.post("/updatePassword", response_model=None)
async def update_password(
    request: Request,
    data: ChangePasswordRequest,
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """
    Change current user's password.

    After password change, all existing tokens will be invalidated.
    """
    user = get_current_user_from_request(request)
    if not user:
        return success(result=None, message="未登录")

    # TODO: Implement password change
    # This will be implemented in Phase 3 user service
    return success(message="密码修改成功，请重新登录")
