// frontend/src/api/modules/supply.ts
import http from '../http';
import { AxiosPromise } from 'axios';

// 简历请求参数类型
export interface SupplyRequest {
  vendorId: number;
  name: string;
  filePath: string;
  fileName: string;
  fileId: string;
  ownerId: number;
  contentConfirm?: number;
  version?: number;
  acdtc?: string;
  contractedMember?: string;
  taskStatus?: string;
  priceUpdateTaskDate?: string;
  priceUpdate?: number;
  priceOriginal?: number;
}

// 简历响应类型
export interface SupplyResponse {
  id: number;
  vendorId: number;
  name: string;
  path: string;
  fileName: string;
  fileId: string;
  ownerId: number;
  vendorName?: string;
  contactName?: string;
  uploadName?: string;
  contactPosition?: string;
  contentConfirm?: number;
  version: number;
  acdtc?: string;
  contractedMember?: string;
  taskStatus: string;
  priceUpdateTaskDate?: string;
  priceUpdate?: number;
  priceOriginal?: number;
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

// 简历分析请求类型
export interface AnalysisRequest {
  supplyId: number;
}

// 简历分析响应类型
export interface AnalysisResponse {
  success: boolean;
  message: string;
}

/**
 * 创建简历
 * @param data 简历数据
 * @returns 创建结果
 */
export const createSupply = (data: SupplyRequest): AxiosPromise<SupplyResponse> => {
  return http.post('/rk/supply', data);
};

/**
 * 获取简历详情
 * @param supplyId 简历ID
 * @returns 简历详情
 */
export const getSupplyById = (supplyId: number): AxiosPromise<SupplyResponse> => {
  return http.get(`/rk/supply/${supplyId}`);
};

/**
 * 更新简历
 * @param supplyId 简历ID
 * @param data 更新数据
 * @returns 更新结果
 */
export const updateSupply = (supplyId: number, data: Partial<SupplyRequest>): AxiosPromise<SupplyResponse> => {
  return http.put(`/rk/supply/${supplyId}`, data);
};

/**
 * 删除简历
 * @param supplyId 简历ID
 * @returns 删除结果
 */
export const deleteSupply = (supplyId: number): AxiosPromise<void> => {
  return http.delete(`/rk/supply/${supplyId}`);
};

/**
 * 获取简历列表
 * @param params 查询参数
 * @returns 简历列表
 */
export const getSupplyList = (params?: PageRequest): AxiosPromise<PageResponse<SupplyResponse>> => {
  return http.get('/rk/supply/list', { params });
};

/**
 * 触发简历分析
 * @param data 分析请求数据
 * @returns 分析结果
 */
export const triggerSupplyAnalysis = (data: AnalysisRequest): AxiosPromise<AnalysisResponse> => {
  return http.post('/rk/supply/analysis', data);
};