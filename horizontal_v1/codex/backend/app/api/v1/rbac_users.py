from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.responses import business_error, success
from backend.app.core.security import CurrentUser, get_current_user
from backend.app.db.deps import get_db_session
from backend.app.models.sys_department import SysDepartment
from backend.app.models.sys_role import SysRole
from backend.app.models.sys_user import SysUser
from backend.app.models.sys_user_role import SysUserRole
from backend.app.schemas.rbac import (
    PageResult,
    Pagination,
    UserCreateRequest,
    UserDisableRequest,
    UserMoveRequest,
    UserOut,
    UserPageRequest,
    UserUpdateRequest,
)
from backend.app.services.auth_service import hash_password

router = APIRouter(prefix="/rbac/users", tags=["rbac"])


@router.post("/add")
async def add_user(
    payload: UserCreateRequest,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    _ = current
    exists = (
        await session.execute(select(func.count()).select_from(SysUser).where(SysUser.username == payload.username))
    ).scalar_one()
    if int(exists) > 0:
        return business_error("用户名已经存在")

    user = SysUser(
        username=payload.username,
        password_hash=hash_password(payload.password),
        status=int(payload.status),
        password_version=1,
        name=payload.name,
        nick_name=payload.nick_name,
        head_img=payload.head_img,
        phone=payload.phone,
        email=payload.email,
        remark=payload.remark,
        department_id=payload.department_id,
    )
    session.add(user)
    await session.flush()

    for role_id in payload.role_id_list:
        session.add(SysUserRole(user_id=int(user.id), role_id=int(role_id)))

    await session.flush()

    return success(UserOut(id=int(user.id), username=user.username, status=int(user.status)))


@router.post("/page")
async def page_users(
    payload: UserPageRequest,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    _ = current
    page = max(1, int(payload.page))
    size = min(200, max(1, int(payload.size)))

    conditions = [SysUser.username != "admin"]
    if payload.key_word:
        like = f"%{payload.key_word}%"
        conditions.append((SysUser.username.ilike(like)) | (SysUser.name.ilike(like)))
    if payload.status is not None:
        conditions.append(SysUser.status == int(payload.status))
    if payload.department_ids:
        conditions.append(SysUser.department_id.in_([int(i) for i in payload.department_ids]))

    total = (
        await session.execute(select(func.count()).select_from(SysUser).where(*conditions))
    ).scalar_one()

    rows = (
        await session.execute(
            select(SysUser, SysDepartment.name.label("department_name"))
            .select_from(SysUser)
            .join(SysDepartment, SysDepartment.id == SysUser.department_id, isouter=True)
            .where(*conditions)
            .order_by(SysUser.id.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
    ).all()

    user_ids = [int(u.id) for (u, _) in rows]
    role_rows = []
    if user_ids:
        role_rows = (
            await session.execute(
                select(SysUserRole.user_id, SysRole.name)
                .select_from(SysUserRole)
                .join(SysRole, SysRole.id == SysUserRole.role_id)
                .where(SysUserRole.user_id.in_(user_ids))
            )
        ).all()
    roles_by_user: dict[int, list[str]] = {}
    for user_id, role_name in role_rows:
        roles_by_user.setdefault(int(user_id), []).append(role_name)

    items: list[UserOut] = []
    for user, dept_name in rows:
        items.append(
            UserOut(
                id=int(user.id),
                username=user.username,
                name=user.name,
                nick_name=user.nick_name,
                head_img=user.head_img,
                phone=user.phone,
                email=user.email,
                remark=user.remark,
                status=int(user.status),
                department_id=int(user.department_id) if user.department_id is not None else None,
                department_name=dept_name,
                role_name=",".join(roles_by_user.get(int(user.id), [])) or None,
            )
        )

    return success(PageResult(list=items, pagination=Pagination(total=int(total), page=page, size=size)))


@router.post("/update")
async def update_user(
    payload: UserUpdateRequest,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    _ = current
    result = await session.execute(select(SysUser).where(SysUser.id == payload.id))
    user = result.scalar_one_or_none()
    if not user:
        return business_error("用户不存在")

    if user.username == "admin":
        return business_error("非法操作")

    if payload.password:
        user.password_hash = hash_password(payload.password)
        user.password_version = int(user.password_version) + 1

    for field in ("name", "nick_name", "head_img", "phone", "email", "remark"):
        value = getattr(payload, field)
        if value is not None:
            setattr(user, field, value)

    if payload.status is not None:
        new_status = int(payload.status)
        if user.status != new_status and new_status == 0:
            user.password_version = int(user.password_version) + 1
        user.status = new_status

    if payload.department_id is not None:
        user.department_id = payload.department_id

    if payload.role_id_list is not None:
        await session.execute(delete(SysUserRole).where(SysUserRole.user_id == payload.id))
        for role_id in payload.role_id_list:
            session.add(SysUserRole(user_id=int(user.id), role_id=int(role_id)))

    await session.flush()
    return success(UserOut(id=int(user.id), username=user.username, status=int(user.status)))


@router.post("/move")
async def move_users(
    payload: UserMoveRequest,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    _ = current
    await session.execute(
        update(SysUser)
        .where(SysUser.id.in_([int(i) for i in payload.user_ids]))
        .values(department_id=int(payload.department_id))
    )
    await session.flush()
    return success(True)


@router.post("/disable")
async def disable_user(
    payload: UserDisableRequest,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    _ = current
    result = await session.execute(select(SysUser).where(SysUser.id == payload.id))
    user = result.scalar_one_or_none()
    if not user:
        return business_error("用户不存在")
    if user.username == "admin":
        return business_error("非法操作")

    new_status = int(payload.status)
    if user.status != new_status and new_status == 0:
        user.password_version = int(user.password_version) + 1
    user.status = new_status
    await session.flush()
    return success(True)
