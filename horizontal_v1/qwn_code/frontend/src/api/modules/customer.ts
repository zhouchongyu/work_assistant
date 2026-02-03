// frontend/src/api/modules/customer.ts
import http from '../http';
import { AxiosPromise } from 'axios';

// 客户请求参数类型
export interface CustomerRequest {
  name: string;
  code: string;
  address?: string;
  postcode?: string;
  description?: string;
}

// 客户响应类型
export interface CustomerResponse {
  id: number;
  name: string;
  code: string;
  address?: string;
  postcode?: string;
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
 * 创建客户
 * @param data 客户数据
 * @returns 创建结果
 */
export const createCustomer = (data: CustomerRequest): AxiosPromise<CustomerResponse> => {
  return http.post('/rk/customer', data);
};

/**
 * 获取客户详情
 * @param customerId 客户ID
 * @returns 客户详情
 */
export const getCustomerById = (customerId: number): AxiosPromise<CustomerResponse> => {
  return http.get(`/rk/customer/${customerId}`);
};

/**
 * 更新客户
 * @param customerId 客户ID
 * @param data 更新数据
 * @returns 更新结果
 */
export const updateCustomer = (customerId: number, data: Partial<CustomerRequest>): AxiosPromise<CustomerResponse> => {
  return http.put(`/rk/customer/${customerId}`, data);
};

/**
 * 删除客户
 * @param customerId 客户ID
 * @returns 删除结果
 */
export const deleteCustomer = (customerId: number): AxiosPromise<void> => {
  return http.delete(`/rk/customer/${customerId}`);
};

/**
 * 获取客户列表
 * @param params 查询参数
 * @returns 客户列表
 */
export const getCustomerList = (params?: PageRequest): AxiosPromise<PageResponse<CustomerResponse>> => {
  return http.get('/rk/customer/list', { params });
};