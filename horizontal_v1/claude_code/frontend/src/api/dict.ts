/**
 * Dictionary API.
 */
import { http } from './request'

export interface DictType {
  id: number
  name: string
  key: string
  remark?: string
  createTime?: string
  updateTime?: string
}

export interface DictInfo {
  id: number
  typeId: number
  name: string
  value: string
  orderNum: number
  remark?: string
  createTime?: string
  updateTime?: string
}

export const dictApi = {
  /**
   * Get dictionary data by types.
   * @param types - Array of dict type keys (empty for all)
   */
  getData(types?: string[]): Promise<Record<string, DictInfo[]>> {
    return http.post('/v1/dict/info/data', { types: types || [] })
  },

  // === Dict Type APIs ===

  /**
   * Get dictionary types list.
   */
  getTypes(params?: { page?: number; size?: number; keyWord?: string }): Promise<any> {
    return http.post('/v1/dict/type/page', params)
  },

  /**
   * Get all dict types.
   */
  getAllTypes(): Promise<DictType[]> {
    return http.post('/v1/dict/type/list')
  },

  /**
   * Create dict type.
   */
  createType(data: Partial<DictType>): Promise<{ id: number }> {
    return http.post('/v1/dict/type/add', data)
  },

  /**
   * Update dict type.
   */
  updateType(data: Partial<DictType> & { id: number }): Promise<void> {
    return http.post('/v1/dict/type/update', data)
  },

  /**
   * Delete dict types.
   */
  deleteType(ids: number | number[]): Promise<void> {
    const idList = Array.isArray(ids) ? ids : [ids]
    return http.post('/v1/dict/type/delete', { ids: idList })
  },

  // === Dict Info APIs ===

  /**
   * Get dictionary info list.
   */
  getInfoList(params?: { page?: number; size?: number; typeId?: number }): Promise<any> {
    return http.post('/v1/dict/info/page', params)
  },

  /**
   * Create dict info.
   */
  createInfo(data: Partial<DictInfo>): Promise<{ id: number }> {
    return http.post('/v1/dict/info/add', data)
  },

  /**
   * Update dict info.
   */
  updateInfo(data: Partial<DictInfo> & { id: number }): Promise<void> {
    return http.post('/v1/dict/info/update', data)
  },

  /**
   * Delete dict infos.
   */
  deleteInfo(ids: number | number[]): Promise<void> {
    const idList = Array.isArray(ids) ? ids : [ids]
    return http.post('/v1/dict/info/delete', { ids: idList })
  },
}

export default dictApi
