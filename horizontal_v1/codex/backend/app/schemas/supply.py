from __future__ import annotations

from typing import Any

from backend.app.schemas.base import Schema


class InvalidWithdrawRequest(Schema):
    unique_id: int
    table_name: str


class SupplyAnalysisRequest(Schema):
    supply_id: int


class DeleteFileRequest(Schema):
    file_id: str


class UpdateResumeProposalRequest(Schema):
    supply_id: int
    proposal_document: str


class UpdateDemandTxtRequest(Schema):
    demand_id: int
    demand_txt: str
    version: int


class MatchStartRequest(Schema):
    demand_id: int
    supply_ids: list[int]
    role_list: list[dict[str, Any]]
    flag_data: list[dict[str, Any]]


class UpdateCaseHardConditionRequest(Schema):
    demand_id: int
    supply_id: int


class ChangeSupplyFileNameRequest(Schema):
    supply_id: int
    new_name: str


class CaseChangeStatusRequest(Schema):
    case_id: int
    before_status: str
    after_status: str
    user_id: int | None = None


class CaseChangeStatusCheckRequest(Schema):
    case_id: int | None = None
    before_status: str
    after_status: str


class UpdateCaseStatusRemarkRequest(Schema):
    case_id: int
    case_status_id: int
    remark_text: str = ""


class CaseInvalidBatchRequest(Schema):
    case_ids: list[int]
    unique_id: int
    table_name: str


class GetAllDuplicateResumesRequest(Schema):
    supply_id: int


class UploadFileInfo(Schema):
    supply_id: int
    url: str


class UpdateFileInfo(Schema):
    file_id: str
    url: str

