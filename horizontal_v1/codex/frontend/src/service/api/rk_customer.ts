import http from '../http'
import type { PageResult } from '../types'

export interface CustomerItem {
  id: number
  name: string
  code: string
}

export interface CustomerPageQuery {
  page?: number
  size?: number
  activeSwitch?: boolean
}

export interface CustomerCreatePayload {
  name: string
  code: string
}

export interface CustomerUpdatePayload extends CustomerCreatePayload {
  id: number
}

export interface CustomerContact {
  id: number
  customerId: number
  name?: string | null
  email?: string | null
  phone?: string | null
  default: boolean
}

export interface CustomerContactPayload {
  customerId: number
  name: string
  email?: string
  phone?: string
  default?: boolean
}

export interface CustomerContactUpdatePayload extends CustomerContactPayload {
  id: number
}

export const fetchCustomers = (payload: CustomerPageQuery = { page: 1, size: 10 }) =>
  http.post<PageResult<CustomerItem>>('/rk/customer/page', { page: 1, size: 10, ...payload })

export const addCustomer = (payload: CustomerCreatePayload) => http.post<CustomerItem>('/rk/customer/add', payload)

export const updateCustomer = (payload: CustomerUpdatePayload) =>
  http.post<CustomerItem>('/rk/customer/update', payload)

export const listCustomerContacts = (customerId: number) =>
  http.get<CustomerContact[]>('/rk/customer_contact/list', { params: { customerId } })

export const addCustomerContact = (payload: CustomerContactPayload) =>
  http.post<CustomerContact>('/rk/customer_contact/add', payload)

export const updateCustomerContact = (payload: CustomerContactUpdatePayload) =>
  http.post<boolean>('/rk/customer_contact/update', payload)
