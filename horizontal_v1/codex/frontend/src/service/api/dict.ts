import http from '../http'
import type { PageResult } from '../types'

export interface DictTypeItem {
  id: number
  name: string
  key: string
  page?: string | null
}

export interface DictInfoItem {
  id: number
  typeId: number
  name: string
  value?: string | number | null
  orderNum: number
  remark?: string | null
  parentId?: number | null
  fieldName?: string | null
  isShow: boolean
  isProcess: boolean
}

export interface DictTypePageQuery {
  page?: number
  size?: number
  keyWord?: string
}

export interface DictInfoPageQuery {
  page?: number
  size?: number
  keyWord?: string
  typeId?: number
}

export type DictDataResponse = Record<string, DictInfoItem[]>

export const fetchDictTypes = (payload: DictTypePageQuery = { page: 1, size: 20 }) =>
  http.post<PageResult<DictTypeItem>>('/dict/type/page', {
    page: 1,
    size: 20,
    ...payload,
  })

export const fetchDictInfos = (payload: DictInfoPageQuery = { page: 1, size: 20 }) =>
  http.post<PageResult<DictInfoItem>>('/dict/info/page', {
    page: 1,
    size: 20,
    ...payload,
  })

export const fetchDictData = (types: string[]) =>
  http.post<DictDataResponse>('/dict/info/data', { types })
