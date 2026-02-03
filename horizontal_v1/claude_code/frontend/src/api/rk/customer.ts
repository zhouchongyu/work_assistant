/**
 * Customer API.
 */
import { http } from '../request'

export interface Customer {
  id: number
  name: string
  shortName?: string
  industry?: string
  scale?: string
  address?: string
  website?: string
  remark?: string
  createTime?: string
  updateTime?: string
}

export interface CustomerListParams {
  page?: number
  size?: number
  keyWord?: string
}

export const customerApi = {
  /**
   * Get customer list with pagination.
   */
  getList(params?: CustomerListParams): Promise<any> {
    return http.post('/v1/rk/customer/page', params)
  },

  /**
   * Get all customers (for select).
   */
  getAll(): Promise<Customer[]> {
    return http.post('/v1/rk/customer/list')
  },

  /**
   * Get customer detail by ID.
   */
  getDetail(id: number): Promise<Customer> {
    return http.post('/v1/rk/customer/info', { id })
  },

  /**
   * Create new customer.
   */
  create(data: Partial<Customer>): Promise<{ id: number }> {
    return http.post('/v1/rk/customer/add', data)
  },

  /**
   * Update customer.
   */
  update(data: Partial<Customer> & { id: number }): Promise<void> {
    return http.post('/v1/rk/customer/update', data)
  },

  /**
   * Delete customers by IDs.
   */
  delete(ids: number | number[]): Promise<void> {
    const idList = Array.isArray(ids) ? ids : [ids]
    return http.post('/v1/rk/customer/delete', { ids: idList })
  },
}

export default customerApi
