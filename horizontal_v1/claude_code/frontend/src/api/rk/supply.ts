/**
 * Supply (Resume) API.
 */
import { http } from '../request'

export interface Supply {
  id: number
  name: string
  gender?: string
  birthDate?: string
  phone?: string
  email?: string
  currentLocation?: string
  workYears?: number
  education?: string
  japaneseLevel?: string
  englishLevel?: string
  status?: number
  createTime?: string
  updateTime?: string
}

export interface SupplyListParams {
  page?: number
  size?: number
  keyWord?: string
  status?: number
  japaneseLevel?: string
  englishLevel?: string
  workYearsMin?: number
  workYearsMax?: number
}

export const supplyApi = {
  /**
   * Get supply list with pagination.
   */
  getList(params?: SupplyListParams): Promise<any> {
    return http.post('/v1/rk/supply/page', params)
  },

  /**
   * Get supply detail by ID.
   */
  getDetail(id: number): Promise<Supply> {
    return http.post('/v1/rk/supply/info', { id })
  },

  /**
   * Create new supply.
   */
  create(data: Partial<Supply>): Promise<{ id: number }> {
    return http.post('/v1/rk/supply/add', data)
  },

  /**
   * Update supply.
   */
  update(data: Partial<Supply> & { id: number }): Promise<void> {
    return http.post('/v1/rk/supply/update', data)
  },

  /**
   * Delete supplies by IDs.
   */
  delete(ids: number | number[]): Promise<void> {
    const idList = Array.isArray(ids) ? ids : [ids]
    return http.post('/v1/rk/supply/delete', { ids: idList })
  },

  /**
   * Trigger resume extraction.
   */
  extract(id: number): Promise<void> {
    return http.post('/v1/rk/supply/extract', { id })
  },

  /**
   * Get AI analysis data.
   */
  getAiData(id: number): Promise<any> {
    return http.post('/v1/rk/supply/aiData', { id })
  },
}

export default supplyApi
