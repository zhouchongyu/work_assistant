import http from '../http'

export interface VendorCreatePayload {
  name: string
  code: string
}

export interface VendorOut {
  id: number
  name: string
  code: string
}

export interface VendorContact {
  id: number
  vendorId: number
  name?: string | null
  email?: string | null
  phone?: string | null
  default: boolean
}

export interface VendorContactPayload {
  vendorId: number
  name: string
  email?: string
  phone?: string
  default?: boolean
}

export interface VendorContactUpdatePayload extends VendorContactPayload {
  id: number
}

export const addVendor = (payload: VendorCreatePayload) => http.post<VendorOut>('/rk/vendor/add', payload)

export const updateVendor = (payload: VendorOut) => http.post<VendorOut>('/rk/vendor/update', payload)

export const listVendorContacts = (vendorId: number) =>
  http.get<VendorContact[]>('/rk/vendor_contact/list', { params: { vendorId } })

export const addVendorContact = (payload: VendorContactPayload) =>
  http.post<VendorContact>('/rk/vendor_contact/add', payload)

export const updateVendorContact = (payload: VendorContactUpdatePayload) =>
  http.post<boolean>('/rk/vendor_contact/update', payload)
