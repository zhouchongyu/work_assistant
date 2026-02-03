/**
 * System Department API.
 */
import { http } from '../request'

export interface SysDepartment {
  id: number
  parentId?: number
  name: string
  orderNum: number
  children?: SysDepartment[]
  createTime?: string
  updateTime?: string
}

export interface DepartmentListParams {
  keyWord?: string
}

export const departmentApi = {
  /**
   * Get department tree list.
   */
  getList(params?: DepartmentListParams): Promise<SysDepartment[]> {
    return http.post('/v1/base/sys/department/list', params)
  },

  /**
   * Get department detail by ID.
   */
  getDetail(id: number): Promise<SysDepartment> {
    return http.post('/v1/base/sys/department/info', { id })
  },

  /**
   * Create new department.
   */
  create(data: Partial<SysDepartment>): Promise<{ id: number }> {
    return http.post('/v1/base/sys/department/add', data)
  },

  /**
   * Update department.
   */
  update(data: Partial<SysDepartment> & { id: number }): Promise<void> {
    return http.post('/v1/base/sys/department/update', data)
  },

  /**
   * Delete department by ID.
   */
  delete(ids: number | number[]): Promise<void> {
    const idList = Array.isArray(ids) ? ids : [ids]
    return http.post('/v1/base/sys/department/delete', { ids: idList })
  },
}

export default departmentApi
