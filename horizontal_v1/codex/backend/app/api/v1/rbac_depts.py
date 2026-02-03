from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import asc, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.responses import success
from backend.app.core.security import CurrentUser, get_current_user
from backend.app.db.deps import get_db_session
from backend.app.models.sys_department import SysDepartment
from backend.app.schemas.rbac import DeptCreateRequest, DeptOrderItem, DeptOut, DeptTreeNode, EmptyRequest

router = APIRouter(prefix="/rbac/depts", tags=["rbac"])


@router.post("/add")
async def add_dept(
    payload: DeptCreateRequest,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    _ = current
    dept = SysDepartment(name=payload.name, parent_id=payload.parent_id, order_num=payload.order_num)
    session.add(dept)
    await session.flush()
    return success(
        DeptOut(
            id=int(dept.id),
            name=dept.name,
            parent_id=int(dept.parent_id) if dept.parent_id is not None else None,
            order_num=int(dept.order_num),
            parent_name=None,
        )
    )


@router.post("/list")
async def list_depts(
    payload: EmptyRequest,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    _ = current
    _ = payload
    rows = (
        await session.execute(select(SysDepartment).order_by(asc(SysDepartment.order_num), asc(SysDepartment.id)))
    ).scalars().all()

    by_id = {int(r.id): r for r in rows}
    out: list[DeptOut] = []
    for r in rows:
        parent_name = None
        if r.parent_id is not None:
            parent = by_id.get(int(r.parent_id))
            parent_name = parent.name if parent else None

        out.append(
            DeptOut(
                id=int(r.id),
                name=r.name,
                parent_id=int(r.parent_id) if r.parent_id is not None else None,
                order_num=int(r.order_num),
                parent_name=parent_name,
            )
        )
    return success(out)


def _build_dept_tree(rows: list[SysDepartment]) -> list[dict]:
    nodes: dict[int, dict] = {}
    roots: list[dict] = []

    for dept in sorted(rows, key=lambda d: (int(d.order_num), int(d.id))):
        nodes[int(dept.id)] = {
            "id": int(dept.id),
            "name": dept.name,
            "parentId": int(dept.parent_id) if dept.parent_id is not None else None,
            "orderNum": int(dept.order_num),
            "children": [],
        }

    for node in nodes.values():
        parent_id = node["parentId"]
        if parent_id is not None and parent_id in nodes:
            nodes[parent_id]["children"].append(node)
        else:
            roots.append(node)

    return roots


@router.post("/tree")
async def dept_tree(
    payload: EmptyRequest,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    _ = current
    _ = payload
    rows = (
        await session.execute(select(SysDepartment).order_by(asc(SysDepartment.order_num), asc(SysDepartment.id)))
    ).scalars().all()
    tree = _build_dept_tree(rows)
    return success([DeptTreeNode.model_validate(n) for n in tree])


@router.post("/order")
async def order_depts(
    payload: list[DeptOrderItem],
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    _ = current
    for item in payload:
        await session.execute(
            update(SysDepartment)
            .where(SysDepartment.id == item.id)
            .values(parent_id=item.parent_id, order_num=item.order_num)
        )
    await session.flush()
    return success(True)
