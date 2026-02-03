from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.responses import business_error, success
from backend.app.core.security import CurrentUser, get_current_user
from backend.app.db.deps import get_db_session
from backend.app.models.sys_role import SysRole
from backend.app.schemas.rbac import EmptyRequest, PageRequest, PageResult, Pagination, RoleCreateRequest, RoleOut

router = APIRouter(prefix="/rbac/roles", tags=["rbac"])


@router.post("/add")
async def add_role(
    payload: RoleCreateRequest,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    _ = current
    exists = (
        await session.execute(select(func.count()).select_from(SysRole).where(SysRole.name == payload.name))
    ).scalar_one()
    if int(exists) > 0:
        return business_error("角色名称已存在")

    role = SysRole(name=payload.name, label=payload.label, remark=payload.remark, relevance=payload.relevance)
    session.add(role)
    await session.flush()

    return success(
        RoleOut(
            id=int(role.id),
            name=role.name,
            label=role.label,
            remark=role.remark,
            relevance=bool(role.relevance),
        )
    )


@router.post("/page")
async def page_roles(
    payload: PageRequest,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    _ = current
    page = max(1, int(payload.page))
    size = min(200, max(1, int(payload.size)))

    base = select(SysRole)
    count_base = select(func.count()).select_from(SysRole)
    if payload.key_word:
        like = f"%{payload.key_word}%"
        base = base.where(SysRole.name.ilike(like))
        count_base = count_base.where(SysRole.name.ilike(like))

    total = (await session.execute(count_base)).scalar_one()
    rows = (
        await session.execute(base.order_by(SysRole.id.desc()).offset((page - 1) * size).limit(size))
    ).scalars().all()

    items = [
        RoleOut(
            id=int(r.id),
            name=r.name,
            label=r.label,
            remark=r.remark,
            relevance=bool(r.relevance),
        )
        for r in rows
    ]

    return success(PageResult(list=items, pagination=Pagination(total=int(total), page=page, size=size)))


@router.post("/list")
async def list_roles(
    payload: EmptyRequest,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    _ = current
    _ = payload
    rows = (await session.execute(select(SysRole).order_by(SysRole.id.asc()))).scalars().all()
    return success(
        [
            RoleOut(id=int(r.id), name=r.name, label=r.label, remark=r.remark, relevance=bool(r.relevance))
            for r in rows
        ]
    )

