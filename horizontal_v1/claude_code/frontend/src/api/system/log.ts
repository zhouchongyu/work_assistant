/**
 * System Log API.
 */
import { http } from '../request'

export interface SysLog {
  id: number
  userId?: number
  userName?: string
  action: string
  ip?: string
  ipAddr?: string
  params?: string
  createTime?: string
}

export interface LogListParams {
  page?: number
  size?: number
  keyWord?: string
  action?: string
  startTime?: string
  endTime?: string
}

export const logApi = {
  /**
   * Get log list with pagination.
   */
  getList(params?: LogListParams): Promise<any> {
    return http.post('/v1/base/sys/log/page', params)
  },

  /**
   * Clear logs before date.
   */
  clear(before?: string): Promise<void> {
    return http.post('/v1/base/sys/log/clear', { before })
  },
}

export default logApi
