/**
 * System User API.
 */
import { http } from '../request'

export interface SysUser {
  id: number
  username: string
  nickName?: string
  name?: string
  email?: string
  phone?: string
  avatar?: string
  status: number
  departmentId?: number
  departmentName?: string
  roleIds?: number[]
  remark?: string
  createTime?: string
  updateTime?: string
}

export interface UserListParams {
  page?: number
  size?: number
  keyWord?: string
  status?: number
  departmentId?: number
}

export const userApi = {
  /**
   * Get user list with pagination.
   */
  getList(params?: UserListParams): Promise<any> {
    return http.post('/v1/base/sys/user/page', params)
  },

  /**
   * Get user detail by ID.
   */
  getDetail(id: number): Promise<SysUser> {
    return http.post('/v1/base/sys/user/info', { id })
  },

  /**
   * Create new user.
   */
  create(data: Partial<SysUser> & { password: string }): Promise<{ id: number }> {
    return http.post('/v1/base/sys/user/add', data)
  },

  /**
   * Update user.
   */
  update(data: Partial<SysUser> & { id: number }): Promise<void> {
    return http.post('/v1/base/sys/user/update', data)
  },

  /**
   * Delete users by IDs.
   */
  delete(ids: number | number[]): Promise<void> {
    const idList = Array.isArray(ids) ? ids : [ids]
    return http.post('/v1/base/sys/user/delete', { ids: idList })
  },

  /**
   * Reset user password.
   */
  resetPassword(id: number, password: string): Promise<void> {
    return http.post('/v1/base/sys/user/resetPassword', { id, password })
  },

  /**
   * Update user status.
   */
  updateStatus(id: number, status: number): Promise<void> {
    return http.post('/v1/base/sys/user/updateStatus', { id, status })
  },
}

export default userApi
