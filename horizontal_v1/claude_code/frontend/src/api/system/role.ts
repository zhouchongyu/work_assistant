/**
 * System Role API.
 */
import { http } from '../request'

export interface SysRole {
  id: number
  name: string
  label?: string
  remark?: string
  relevance?: number
  menuIds?: number[]
  departmentIds?: number[]
  createTime?: string
  updateTime?: string
}

export interface RoleListParams {
  page?: number
  size?: number
  keyWord?: string
}

export const roleApi = {
  /**
   * Get role list with pagination.
   */
  getList(params?: RoleListParams): Promise<any> {
    return http.post('/v1/base/sys/role/page', params)
  },

  /**
   * Get all roles (for select).
   */
  getAll(): Promise<SysRole[]> {
    return http.post('/v1/base/sys/role/list')
  },

  /**
   * Get role detail by ID.
   */
  getDetail(id: number): Promise<SysRole> {
    return http.post('/v1/base/sys/role/info', { id })
  },

  /**
   * Create new role.
   */
  create(data: Partial<SysRole>): Promise<{ id: number }> {
    return http.post('/v1/base/sys/role/add', data)
  },

  /**
   * Update role.
   */
  update(data: Partial<SysRole> & { id: number }): Promise<void> {
    return http.post('/v1/base/sys/role/update', data)
  },

  /**
   * Delete roles by IDs.
   */
  delete(ids: number | number[]): Promise<void> {
    const idList = Array.isArray(ids) ? ids : [ids]
    return http.post('/v1/base/sys/role/delete', { ids: idList })
  },
}

export default roleApi
