import http from '../http'

export interface UploadResponse {
  supplyId: number
  url: string
}

export interface UpdateDemandTxtPayload {
  demandId: number
  demandTxt: string
  version: number
}

export interface MatchStartPayload {
  demandId: number
  supplyIds: number[]
  roleList: Record<string, any>[]
  flagData: Record<string, any>[]
}

export interface CaseStatusChangePayload {
  caseId: number
  beforeStatus: string
  afterStatus: string
  userId?: number | null
}

export const uploadSupply = (formData: FormData) =>
  http.post<UploadResponse>('/supply/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })

export const updateDemandTxt = (payload: UpdateDemandTxtPayload) =>
  http.post('/supply/update_demand_txt', payload)

export const matchStart = (payload: MatchStartPayload) => http.post('/supply/match_start', payload)

export const caseChangeStatusCheck = (payload: { caseId?: number | null; beforeStatus: string; afterStatus: string }) =>
  http.post('/supply/case_change_status_check', payload)

export const caseChangeStatus = (payload: CaseStatusChangePayload) =>
  http.post('/supply/case_change_status', payload)
