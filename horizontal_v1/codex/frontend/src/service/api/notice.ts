import http from '../http'
import type { PageResult } from '../types'

export interface NoticeItem {
  id: number
  content: string
  isRead: boolean
  type?: string | null
  model?: string | null
  createdAt?: string
}

export interface NoticeQuery {
  page?: number
  size?: number
  isRead?: boolean
}

export const fetchNotices = (payload: NoticeQuery = { page: 1, size: 10 }) =>
  http.post<PageResult<NoticeItem>>('/notice/page', { page: 1, size: 10, ...payload })

export const markRead = (ids: number[]) => http.post('/notice/mark_read', { ids })

export const unreadCount = () => http.get<number>('/notice/unread_count')
