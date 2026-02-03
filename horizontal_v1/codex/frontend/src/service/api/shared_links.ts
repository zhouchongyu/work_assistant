import http from '../http'

export interface SharedLinksListRequest {
  type: 'supply' | 'demand'
  shareToken: string
}

export interface SharedSupplyItem {
  id: number
  name?: string | null
  path?: string | null
  url?: string | null
  downloadUrl?: string | null
}

export interface SharedDemandItem {
  id: number
  remark?: string | null
}

export const fetchSharedList = (payload: SharedLinksListRequest) =>
  http.post<SharedSupplyItem[] | SharedDemandItem[]>('/shared_links/shared_links_list', payload)
