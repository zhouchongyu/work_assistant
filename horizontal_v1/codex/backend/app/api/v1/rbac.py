from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.responses import success
from backend.app.core.security import CurrentUser, get_current_user
from backend.app.db.deps import get_db_session
from backend.app.models.sys_menu import SysMenu
from backend.app.models.sys_role_menu import SysRoleMenu

router = APIRouter(prefix="/rbac", tags=["rbac"])


def _build_menu_tree(menus: list[SysMenu]) -> list[dict]:
    nodes: dict[int, dict] = {}
    roots: list[dict] = []

    for menu in sorted(menus, key=lambda m: (m.order_num, int(m.id))):
        node = {
            "id": int(menu.id),
            "parentId": int(menu.parent_id) if menu.parent_id else None,
            "name": menu.name,
            "router": menu.router,
            "perms": menu.perms,
            "type": int(menu.type),
            "icon": menu.icon,
            "orderNum": int(menu.order_num),
            "viewPath": menu.view_path,
            "keepAlive": bool(menu.keep_alive),
            "isShow": bool(menu.is_show),
            "childMenus": [],
        }
        nodes[int(menu.id)] = node

    for node in nodes.values():
        parent_id = node["parentId"]
        if parent_id and parent_id in nodes:
            nodes[parent_id]["childMenus"].append(node)
        else:
            roots.append(node)

    return roots


@router.get("/perms")
async def perms(
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    if not current.role_ids:
        return success([])

    result = await session.execute(
        select(SysMenu.perms)
        .join(SysRoleMenu, SysRoleMenu.menu_id == SysMenu.id)
        .where(SysRoleMenu.role_id.in_(current.role_ids))
    )
    perms_set: set[str] = set()
    for (perms_str,) in result.all():
        if not perms_str:
            continue
        for p in perms_str.split(","):
            p = p.strip()
            if p:
                perms_set.add(p)
    return success(sorted(perms_set))


@router.get("/menus")
async def menus(
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    if not current.role_ids:
        return success([])

    result = await session.execute(
        select(SysMenu)
        .join(SysRoleMenu, SysRoleMenu.menu_id == SysMenu.id)
        .where(SysRoleMenu.role_id.in_(current.role_ids))
    )
    menu_list = list({int(m.id): m for m in result.scalars().all()}.values())
    return success(_build_menu_tree(menu_list))

