/**
 * System Menu API.
 */
import { http } from '../request'

export interface SysMenu {
  id: number
  parentId?: number
  name: string
  router?: string
  perms?: string
  type: number  // 0: directory, 1: menu, 2: permission
  icon?: string
  orderNum: number
  viewPath?: string
  keepAlive?: boolean
  isShow?: boolean
  children?: SysMenu[]
  createTime?: string
  updateTime?: string
}

export interface MenuListParams {
  keyWord?: string
}

export const menuApi = {
  /**
   * Get menu tree list.
   */
  getList(params?: MenuListParams): Promise<SysMenu[]> {
    return http.post('/v1/base/sys/menu/list', params)
  },

  /**
   * Get menu detail by ID.
   */
  getDetail(id: number): Promise<SysMenu> {
    return http.post('/v1/base/sys/menu/info', { id })
  },

  /**
   * Create new menu.
   */
  create(data: Partial<SysMenu>): Promise<{ id: number }> {
    return http.post('/v1/base/sys/menu/add', data)
  },

  /**
   * Update menu.
   */
  update(data: Partial<SysMenu> & { id: number }): Promise<void> {
    return http.post('/v1/base/sys/menu/update', data)
  },

  /**
   * Delete menu by ID.
   */
  delete(ids: number | number[]): Promise<void> {
    const idList = Array.isArray(ids) ? ids : [ids]
    return http.post('/v1/base/sys/menu/delete', { ids: idList })
  },
}

export default menuApi
