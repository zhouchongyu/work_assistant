/**
 * Vendor API.
 */
import { http } from '../request'

export interface Vendor {
  id: number
  name: string
  shortName?: string
  type?: string
  address?: string
  website?: string
  remark?: string
  createTime?: string
  updateTime?: string
}

export interface VendorListParams {
  page?: number
  size?: number
  keyWord?: string
  type?: string
}

export const vendorApi = {
  /**
   * Get vendor list with pagination.
   */
  getList(params?: VendorListParams): Promise<any> {
    return http.post('/v1/rk/vendor/page', params)
  },

  /**
   * Get all vendors (for select).
   */
  getAll(): Promise<Vendor[]> {
    return http.post('/v1/rk/vendor/list')
  },

  /**
   * Get vendor detail by ID.
   */
  getDetail(id: number): Promise<Vendor> {
    return http.post('/v1/rk/vendor/info', { id })
  },

  /**
   * Create new vendor.
   */
  create(data: Partial<Vendor>): Promise<{ id: number }> {
    return http.post('/v1/rk/vendor/add', data)
  },

  /**
   * Update vendor.
   */
  update(data: Partial<Vendor> & { id: number }): Promise<void> {
    return http.post('/v1/rk/vendor/update', data)
  },

  /**
   * Delete vendors by IDs.
   */
  delete(ids: number | number[]): Promise<void> {
    const idList = Array.isArray(ids) ? ids : [ids]
    return http.post('/v1/rk/vendor/delete', { ids: idList })
  },
}

export default vendorApi
