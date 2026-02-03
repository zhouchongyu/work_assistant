/**
 * Demand API.
 */
import { http } from '../request'

export interface Demand {
  id: number
  title: string
  customerId?: number
  customerName?: string
  positionType?: string
  workLocation?: string
  salary?: string
  requirements?: string
  status?: number
  createTime?: string
  updateTime?: string
}

export interface DemandListParams {
  page?: number
  size?: number
  keyWord?: string
  status?: number
  customerId?: number
}

export const demandApi = {
  /**
   * Get demand list with pagination.
   */
  getList(params?: DemandListParams): Promise<any> {
    return http.post('/v1/rk/demand/page', params)
  },

  /**
   * Get demand detail by ID.
   */
  getDetail(id: number): Promise<Demand> {
    return http.post('/v1/rk/demand/info', { id })
  },

  /**
   * Create new demand.
   */
  create(data: Partial<Demand>): Promise<{ id: number }> {
    return http.post('/v1/rk/demand/add', data)
  },

  /**
   * Update demand.
   */
  update(data: Partial<Demand> & { id: number }): Promise<void> {
    return http.post('/v1/rk/demand/update', data)
  },

  /**
   * Delete demands by IDs.
   */
  delete(ids: number | number[]): Promise<void> {
    const idList = Array.isArray(ids) ? ids : [ids]
    return http.post('/v1/rk/demand/delete', { ids: idList })
  },

  /**
   * Trigger demand matching.
   */
  match(id: number, params?: any): Promise<void> {
    return http.post('/v1/rk/demand/match', { id, ...params })
  },
}

export default demandApi
