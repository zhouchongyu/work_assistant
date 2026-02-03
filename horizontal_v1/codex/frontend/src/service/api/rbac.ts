import http from '../http'
import type { PageResult } from '../types'

export interface PageQuery {
  page?: number
  size?: number
  keyWord?: string
}

export interface UserPageQuery extends PageQuery {
  status?: number
  departmentIds?: number[]
}

export interface UserItem {
  id: number
  username: string
  name?: string | null
  nickName?: string | null
  phone?: string | null
  email?: string | null
  remark?: string | null
  status: number
  departmentId?: number | null
  departmentName?: string | null
  roleName?: string | null
}

export interface RoleItem {
  id: number
  name: string
  label?: string | null
  remark?: string | null
  relevance: boolean
}

export interface DeptItem {
  id: number
  name: string
  parentId?: number | null
  orderNum: number
  parentName?: string | null
}

export interface DeptTreeNode {
  id: number
  name: string
  parentId?: number | null
  orderNum: number
  children: DeptTreeNode[]
}

export const fetchUsers = (payload: UserPageQuery = { page: 1, size: 20 }) =>
  http.post<PageResult<UserItem>>('/rbac/users/page', {
    page: 1,
    size: 20,
    ...payload,
  })

export const fetchRoles = (payload: PageQuery = { page: 1, size: 20 }) =>
  http.post<PageResult<RoleItem>>('/rbac/roles/page', {
    page: 1,
    size: 20,
    ...payload,
  })

export const fetchDepts = () => http.post<DeptItem[]>('/rbac/depts/list', {})

export const fetchDeptTree = () => http.post<DeptTreeNode[]>('/rbac/depts/tree', {})

export const fetchPerms = () => http.get<string[]>('/rbac/perms')
