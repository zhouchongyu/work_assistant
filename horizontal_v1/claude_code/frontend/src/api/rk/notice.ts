/**
 * Notice API.
 */
import { http } from '../request'

export interface Notice {
  id: number
  title: string
  content: string
  type: string
  targetType: string
  targetId?: number
  isRead: boolean
  userId: number
  createTime?: string
}

export interface NoticeListParams {
  page?: number
  size?: number
  type?: string
  isRead?: boolean
}

export const noticeApi = {
  /**
   * Get notice list with pagination.
   */
  getList(params?: NoticeListParams): Promise<any> {
    return http.post('/v1/rk/notice/page', params)
  },

  /**
   * Get notice detail by ID.
   */
  getDetail(id: number): Promise<Notice> {
    return http.post('/v1/rk/notice/info', { id })
  },

  /**
   * Mark notice as read.
   */
  markRead(id: number): Promise<void> {
    return http.post('/v1/rk/notice/read', { id })
  },

  /**
   * Mark all notices as read.
   */
  markAllRead(): Promise<void> {
    return http.post('/v1/rk/notice/readAll')
  },

  /**
   * Delete notices by IDs.
   */
  delete(ids: number | number[]): Promise<void> {
    const idList = Array.isArray(ids) ? ids : [ids]
    return http.post('/v1/rk/notice/delete', { ids: idList })
  },

  /**
   * Get unread count.
   */
  getUnreadCount(): Promise<number> {
    return http.post('/v1/rk/notice/unreadCount')
  },
}

export default noticeApi
