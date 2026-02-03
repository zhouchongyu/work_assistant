from __future__ import annotations

import hashlib
from datetime import datetime

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.responses import business_error, success
from backend.app.core.security import CurrentUser, get_current_user
from backend.app.db.deps import get_db_session
from backend.app.integrations.sharepoint_graph.client import GraphClient, get_graph_client
from backend.app.integrations.third_party_analyze.client import ThirdPartyAnalyzeClient, get_third_party_analyze_client
from backend.app.models.rk_demand import RkDemand
from backend.app.models.rk_supply import RkSupply
from backend.app.models.rk_supply_demand_link import RkSupplyDemandLink
from backend.app.models.rk_vendor import RkVendor
from backend.app.schemas.supply import (
    CaseChangeStatusCheckRequest,
    CaseChangeStatusRequest,
    CaseInvalidBatchRequest,
    ChangeSupplyFileNameRequest,
    DeleteFileRequest,
    GetAllDuplicateResumesRequest,
    InvalidWithdrawRequest,
    MatchStartRequest,
    SupplyAnalysisRequest,
    UpdateCaseHardConditionRequest,
    UpdateCaseStatusRemarkRequest,
    UpdateDemandTxtRequest,
    UpdateFileInfo,
    UpdateResumeProposalRequest,
    UploadFileInfo,
)
from backend.app.services.case_service import CaseService, CaseServiceError

router = APIRouter(prefix="/supply", tags=["supply"])


@router.post("/invalid_withdraw")
async def invalid_withdraw(
    payload: InvalidWithdrawRequest,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    _ = current, session, payload
    return success(None)


@router.post("/upload")
async def upload(
    file: UploadFile = File(...),
    vendor_id: int = Form(...),
    user_id: int = Form(...),
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    graph: GraphClient = Depends(get_graph_client),
    third_party: ThirdPartyAnalyzeClient = Depends(get_third_party_analyze_client),
):
    _ = user_id
    vendor = (
        await session.execute(select(RkVendor).where(RkVendor.id == vendor_id))
    ).scalar_one_or_none()
    if not vendor:
        return business_error("供应商不存在")

    file_content = await file.read()
    md5 = hashlib.md5(file_content).hexdigest()
    now = datetime.now().astimezone()

    supply = RkSupply(
        name=file.filename or "resume",
        vendor_id=vendor_id,
        user_id=int(current.user.id),
        file_name=file.filename,
        file_md5=md5,
        file_update=now,
        version=1,
        analysis_status="analysis_start",
        created_by=int(current.user.id),
        updated_by=int(current.user.id),
        owner_id=int(current.user.id),
        department_id=current.user.department_id,
        active=True,
        to_be_confirmed=False,
    )
    session.add(supply)
    await session.flush()

    resume_folder = await graph.ensure_child_folder(
        str(vendor.folder_id),
        f"{int(supply.id)}_{int(supply.version or 1)}",
    )
    resume_folder_id = (resume_folder or {}).get("id")
    if not resume_folder_id:
        await session.rollback()
        return business_error("涓婁紶鏂囦欢澶辫触")

    original_filename = file.filename or "resume"
    upload_info = await graph.upload_file(resume_folder_id, original_filename, file_content, file.content_type)
    file_id = (upload_info or {}).get("id")
    if not file_id:
        await session.rollback()
        return business_error("涓婁紶鏂囦欢澶辫触")

    web_url = await graph.create_link(str(file_id)) or (upload_info or {}).get("webUrl") or ""
    if not web_url:
        await session.rollback()
        return business_error("上传文件失败")

    supply.name = original_filename
    supply.path = web_url
    supply.file_name = original_filename
    supply.file_id = str(file_id)
    supply.file_update = now
    supply.updated_by = int(current.user.id)
    await session.flush()

    try:
        await third_party.analyze_resume(
            file_content=file_content,
            filename=original_filename,
            content_type=file.content_type,
            supply_id=int(supply.id),
            version=int(supply.version or 1),
        )
    except Exception:
        pass
    await file.close()

    return success(UploadFileInfo(supply_id=int(supply.id), url=web_url))


@router.post("/resume_analysis")
async def resume_analysis(
    payload: SupplyAnalysisRequest,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    graph: GraphClient = Depends(get_graph_client),
    third_party: ThirdPartyAnalyzeClient = Depends(get_third_party_analyze_client),
):
    _ = current
    supply = (
        await session.execute(select(RkSupply).where(RkSupply.id == payload.supply_id))
    ).scalar_one_or_none()
    if not supply:
        return business_error("简历不存在")
    if not supply.file_id:
        return business_error("File not found")

    try:
        drive_item = await graph.get_drive_item(str(supply.file_id))
        chunks = bytearray()
        async for chunk in await graph.stream_file_content(str(supply.file_id)):
            chunks.extend(chunk)
        file_content = bytes(chunks)
        await third_party.analyze_resume(
            file_content=file_content,
            filename=supply.file_name or supply.name,
            content_type=drive_item.content_type,
            supply_id=int(supply.id),
            version=int(supply.version or 1),
        )
    except Exception:
        return business_error("Analyze request failed")

    supply.analysis_status = "analysis_start"
    supply.updated_by = int(current.user.id)
    await session.flush()
    return success(None)


@router.post("/update_file")
async def update_file(
    file: UploadFile = File(...),
    supply_id: int = Form(...),
    version: int = Form(...),
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    graph: GraphClient = Depends(get_graph_client),
    third_party: ThirdPartyAnalyzeClient = Depends(get_third_party_analyze_client),
):
    _ = current
    supply = (
        await session.execute(select(RkSupply).where(RkSupply.id == supply_id))
    ).scalar_one_or_none()
    if not supply:
        return business_error("简历不存在")

    vendor = None
    if supply.vendor_id is not None:
        vendor = (
            await session.execute(select(RkVendor).where(RkVendor.id == int(supply.vendor_id)))
        ).scalar_one_or_none()
    if not vendor or not vendor.folder_id:
        return business_error("供应商文件夹不存在")

    file_content = await file.read()
    md5 = hashlib.md5(file_content).hexdigest()
    now = datetime.now().astimezone()

    resume_folder = await graph.ensure_child_folder(str(vendor.folder_id), f"{int(supply.id)}_{int(version)}")
    resume_folder_id = (resume_folder or {}).get("id")
    if not resume_folder_id:
        await session.rollback()
        return business_error("上传文件失败")

    original_filename = file.filename or (supply.file_name or supply.name)
    upload_info = await graph.upload_file(resume_folder_id, original_filename, file_content, file.content_type)
    file_id = (upload_info or {}).get("id")
    if not file_id:
        await session.rollback()
        return business_error("上传文件失败")

    web_url = await graph.create_link(str(file_id)) or (upload_info or {}).get("webUrl") or ""
    if not web_url:
        await session.rollback()
        return business_error("上传文件失败")

    supply.file_name = original_filename
    supply.file_id = str(file_id)
    supply.file_md5 = md5
    supply.file_update = now
    supply.path = web_url
    supply.version = int(version)
    supply.analysis_status = "analysis_start"
    supply.updated_by = int(current.user.id)
    await session.flush()

    try:
        await third_party.analyze_resume(
            file_content=file_content,
            filename=original_filename,
            content_type=file.content_type,
            supply_id=int(supply.id),
            version=int(version),
        )
    except Exception:
        pass
    await file.close()

    return success(UpdateFileInfo(file_id=str(file_id), url=web_url))


@router.post("/delete_file")
async def delete_file(
    payload: DeleteFileRequest,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    graph: GraphClient = Depends(get_graph_client),
):
    _ = current
    supply = (
        await session.execute(select(RkSupply).where(RkSupply.file_id == payload.file_id))
    ).scalar_one_or_none()
    if not supply:
        return business_error("文件不存在")

    try:
        await graph.delete_file(payload.file_id)
    except Exception:
        await session.rollback()
        return business_error("删除文件失败")
    supply.file_id = None
    supply.file_name = None
    supply.path = None
    await session.flush()
    return success(UpdateFileInfo(file_id=payload.file_id, url=""))


@router.post("/update_resume_proposal")
async def update_resume_proposal(
    payload: UpdateResumeProposalRequest,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    third_party: ThirdPartyAnalyzeClient = Depends(get_third_party_analyze_client),
):
    supply = (
        await session.execute(select(RkSupply).where(RkSupply.id == payload.supply_id))
    ).scalar_one_or_none()
    if not supply:
        return business_error("简历不存在")
    try:
        await third_party.analyze_resume_proposal(
            proposal_document=payload.proposal_document,
            supply_id=int(payload.supply_id),
        )
    except Exception:
        pass
    supply.contact_analysis_status = "contact_analysis_start"
    supply.updated_by = int(current.user.id)
    await session.flush()
    return success(None)


@router.post("/update_demand_txt")
async def update_demand_txt(
    payload: UpdateDemandTxtRequest,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    third_party: ThirdPartyAnalyzeClient = Depends(get_third_party_analyze_client),
):
    _ = payload.demand_txt
    demand = (
        await session.execute(select(RkDemand).where(RkDemand.id == payload.demand_id))
    ).scalar_one_or_none()
    if not demand:
        return business_error("需求不存在")
    try:
        await third_party.analyze_demand_txt(
            demand_txt=payload.demand_txt,
            demand_id=int(payload.demand_id),
            version=int(payload.version),
        )
    except Exception:
        pass
    demand.analysis_status = "analysis_start"
    demand.version = int(payload.version)
    demand.updated_by = int(current.user.id)
    await session.flush()
    return success(None)


@router.post("/match_start")
async def match_start(
    payload: MatchStartRequest,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    third_party: ThirdPartyAnalyzeClient = Depends(get_third_party_analyze_client),
):
    _ = current, payload.role_list, payload.flag_data
    demand = (
        await session.execute(select(RkDemand).where(RkDemand.id == payload.demand_id))
    ).scalar_one_or_none()
    if not demand:
        return business_error("需求不存在")

    demand.analysis_status = "match_start"
    demand.updated_by = int(current.user.id)

    all_data = {
        "demand_info": {
            "id": int(demand.id),
            "remark": demand.remark,
            "version": int(demand.version or 0),
        },
        "all_supply_ids": [int(i) for i in payload.supply_ids],
        "role_list": payload.role_list,
        "flag_data": payload.flag_data,
    }
    extra_data = {"demand_version": int(demand.version or 0)}

    try:
        await third_party.analyze_match(demand_id=int(payload.demand_id), all_data=all_data, extra_data=extra_data)
    except Exception:
        # best-effort; callback will finalize
        pass

    await session.flush()
    return success(None)


@router.post("/update_case_hard_condition")
async def update_case_hard_condition(
    payload: UpdateCaseHardConditionRequest,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    third_party: ThirdPartyAnalyzeClient = Depends(get_third_party_analyze_client),
):
    _ = current
    case = (
        await session.execute(
            select(RkSupplyDemandLink).where(
                RkSupplyDemandLink.demand_id == payload.demand_id,
                RkSupplyDemandLink.supply_id == payload.supply_id,
            )
        )
    ).scalar_one_or_none()
    if not case:
        return business_error("case不存在")
    case.warning_msg = {"hardCondition": "pending"}

    demand = (
        await session.execute(select(RkDemand).where(RkDemand.id == int(payload.demand_id)))
    ).scalar_one_or_none()
    supply = (
        await session.execute(select(RkSupply).where(RkSupply.id == int(payload.supply_id)))
    ).scalar_one_or_none()

    if demand and supply:
        demand_info = {
            "id": int(demand.id),
            "price": demand.price,
            "japanese_level": demand.japanese_level,
            "english_level": demand.english_level,
            "citizenship": demand.citizenship,
            "work_percent": demand.work_percent,
        }
        supply_info = {
            "id": int(supply.id),
            "price": supply.price,
            "japanese_level": supply.japanese_level,
            "english_level": supply.english_level,
            "citizenship": supply.supply_user_citizenship,
        }
        try:
            res = await third_party.hard_condition(demand_info=demand_info, supply_info=supply_info)
        except Exception:
            res = None

        if isinstance(res, dict):
            msg = res.get("msg") or []
            if isinstance(msg, list) and msg:
                warn_list: list[str] = []
                for one in msg:
                    if isinstance(one, dict):
                        zh = one.get("zh")
                        if isinstance(zh, str) and zh:
                            warn_list.append(zh)
                    elif isinstance(one, str) and one:
                        warn_list.append(one)
                if warn_list:
                    case.warning_msg = warn_list
    await session.flush()
    return success(None)


@router.post("/change_supply_file_name")
async def change_supply_file_name(
    payload: ChangeSupplyFileNameRequest,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    graph: GraphClient = Depends(get_graph_client),
):
    _ = current
    supply = (
        await session.execute(select(RkSupply).where(RkSupply.id == payload.supply_id))
    ).scalar_one_or_none()
    if not supply:
        return business_error("简历不存在")
    if not supply.file_id:
        return business_error("文件不存在")
    try:
        await graph.change_file_name(str(supply.file_id), payload.new_name)
    except Exception:
        return business_error("文件重命名失败")
    supply.file_name = payload.new_name
    supply.name = payload.new_name
    supply.updated_by = int(current.user.id)
    await session.flush()
    return success(None)


@router.post("/case_change_status_check")
async def case_change_status_check(
    payload: CaseChangeStatusCheckRequest,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    _ = current
    try:
        checked = await CaseService.check_case_status_change(
            session,
            case_id=payload.case_id,
            before_status=payload.before_status,
            after_status=payload.after_status,
        )
    except CaseServiceError as e:
        return business_error(e.message)
    return success({"allowed": checked.allowed, "reason": checked.reason, "suggestions": checked.suggestions})


@router.post("/case_change_status")
async def case_change_status(
    payload: CaseChangeStatusRequest,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    _ = current, payload.user_id
    try:
        changed = await CaseService.change_case_status(
            session,
            case_id=int(payload.case_id),
            before_status=payload.before_status,
            after_status=payload.after_status,
        )
    except CaseServiceError as e:
        return business_error(e.message)
    return success(
        {
            "msg": changed.get("msg") or "",
            "insertId": int(changed.get("insert_id") or 0),
            "closeCaseIds": changed.get("close_case_ids") or [],
        }
    )


@router.post("/case_invalid_batch")
async def case_invalid_batch(
    payload: CaseInvalidBatchRequest,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    _ = current
    try:
        await CaseService.case_invalid_batch(
            session,
            case_ids=payload.case_ids,
            unique_id=int(payload.unique_id),
            table_name=payload.table_name,
        )
    except CaseServiceError as e:
        return business_error(e.message)
    return success(None)


@router.post("/case_status_remark_update")
async def case_status_remark_update(
    payload: UpdateCaseStatusRemarkRequest,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    _ = current
    try:
        await CaseService.update_case_status_remark(
            session,
            case_id=int(payload.case_id),
            case_status_id=int(payload.case_status_id),
            remark_text=payload.remark_text,
        )
    except CaseServiceError as e:
        return business_error(e.message)
    return success(None)


@router.post("/get_all_duplicate_resumes")
async def get_all_duplicate_resumes(
    payload: GetAllDuplicateResumesRequest,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    _ = current
    supply = (
        await session.execute(select(RkSupply).where(RkSupply.id == payload.supply_id))
    ).scalar_one_or_none()
    if not supply:
        return business_error("简历不存在")
    if not supply.file_md5:
        return success({"duplicateResumes": []})

    rows = (
        await session.execute(
            select(RkSupply).where(
                RkSupply.file_md5 == supply.file_md5,
                RkSupply.id != supply.id,
            )
        )
    ).scalars().all()
    return success({"duplicateResumes": [{"id": int(r.id), "name": r.name} for r in rows]})


@router.get("/file/{supply_id}")
async def get_supply_file(
    supply_id: int,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    graph: GraphClient = Depends(get_graph_client),
):
    _ = current
    supply = (
        await session.execute(select(RkSupply).where(RkSupply.id == supply_id))
    ).scalar_one_or_none()
    if not supply or (not supply.file_id and not supply.path):
        return business_error("文件不存在")

    if supply.file_id:
        item = await graph.get_drive_item(str(supply.file_id))
        stream = await graph.stream_file_content(str(supply.file_id))
        media_type = item.content_type or "application/octet-stream"
    else:
        stream = await graph.stream_file_content_from_share_url(str(supply.path))
        media_type = "application/octet-stream"

    return StreamingResponse(stream, media_type=media_type)
