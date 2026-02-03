/**
 * Case (Supply-Demand Link) API.
 */
import { http } from '../request'

export interface Case {
  id: number
  supplyId: number
  demandId: number
  supplyName?: string
  demandTitle?: string
  customerName?: string
  status: number
  statusName?: string
  createTime?: string
  updateTime?: string
}

export interface CaseListParams {
  page?: number
  size?: number
  keyWord?: string
  status?: number
  supplyId?: number
  demandId?: number
  customerId?: number
}

// Case status constants
export const CASE_STATUS = {
  CREATED: 0,       // 新建
  SUBMITTED: 1,     // 已提交
  INTERVIEWING: 2,  // 面试中
  OFFERED: 3,       // 已offer
  ONBOARD: 4,       // 已入职
  REJECTED: 5,      // 已拒绝
  WITHDRAWN: 6,     // 已撤回
}

export const caseApi = {
  /**
   * Get case list with pagination.
   */
  getList(params?: CaseListParams): Promise<any> {
    return http.post('/v1/rk/case/page', params)
  },

  /**
   * Get case detail by ID.
   */
  getDetail(id: number): Promise<Case> {
    return http.post('/v1/rk/case/info', { id })
  },

  /**
   * Create new case.
   */
  create(data: Partial<Case>): Promise<{ id: number }> {
    return http.post('/v1/rk/case/add', data)
  },

  /**
   * Update case.
   */
  update(data: Partial<Case> & { id: number }): Promise<void> {
    return http.post('/v1/rk/case/update', data)
  },

  /**
   * Delete cases by IDs.
   */
  delete(ids: number | number[]): Promise<void> {
    const idList = Array.isArray(ids) ? ids : [ids]
    return http.post('/v1/rk/case/delete', { ids: idList })
  },

  /**
   * Update case status.
   */
  updateStatus(id: number, status: number, reason?: string): Promise<void> {
    return http.post('/v1/rk/case/updateStatus', { id, status, reason })
  },

  /**
   * Get case status history.
   */
  getStatusHistory(caseId: number): Promise<any[]> {
    return http.post('/v1/rk/caseStatus/list', { caseId })
  },
}

export default caseApi
