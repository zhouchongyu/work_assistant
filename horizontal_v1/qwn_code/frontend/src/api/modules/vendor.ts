// frontend/src/api/modules/vendor.ts
import http from '../http';
import { AxiosPromise } from 'axios';

// 供应商请求参数类型
export interface VendorRequest {
  name: string;
  code: string;
  folderId?: string;
  description?: string;
}

// 供应商响应类型
export interface VendorResponse {
  id: number;
  name: string;
  code: string;
  folderId?: string;
  description?: string;
  createdAt: string;
  updatedAt: string;
}

// 分页请求参数类型
export interface PageRequest {
  page: number;
  size: number;
  sort?: string;
  [key: string]: any; // 支持其他查询参数
}

// 分页响应类型
export interface PageResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
}

/**
 * 创建供应商
 * @param data 供应商数据
 * @returns 创建结果
 */
export const createVendor = (data: VendorRequest): AxiosPromise<VendorResponse> => {
  return http.post('/rk/vendor', data);
};

/**
 * 获取供应商详情
 * @param vendorId 供应商ID
 * @returns 供应商详情
 */
export const getVendorById = (vendorId: number): AxiosPromise<VendorResponse> => {
  return http.get(`/rk/vendor/${vendorId}`);
};

/**
 * 更新供应商
 * @param vendorId 供应商ID
 * @param data 更新数据
 * @returns 更新结果
 */
export const updateVendor = (vendorId: number, data: Partial<VendorRequest>): AxiosPromise<VendorResponse> => {
  return http.put(`/rk/vendor/${vendorId}`, data);
};

/**
 * 删除供应商
 * @param vendorId 供应商ID
 * @returns 删除结果
 */
export const deleteVendor = (vendorId: number): AxiosPromise<void> => {
  return http.delete(`/rk/vendor/${vendorId}`);
};

/**
 * 获取供应商列表
 * @param params 查询参数
 * @returns 供应商列表
 */
export const getVendorList = (params?: PageRequest): AxiosPromise<PageResponse<VendorResponse>> => {
  return http.get('/rk/vendor/list', { params });
};