// frontend/src/api/modules/demand.ts
import http from '../http';
import { AxiosPromise } from 'axios';

// 需求请求参数类型
export interface DemandRequest {
  customerId: number;
  name: string;
  remark: string;
  unitPriceMax?: number;
  japaneseLevel?: string;
  englishLevel?: string;
  citizenship?: string;
  workLocation?: string;
  workPercent?: number;
  ownerId: number;
  version?: number;
  analysisStatus?: string;
}

// 需求响应类型
export interface DemandResponse {
  id: number;
  customerId: number;
  name: string;
  remark: string;
  unitPriceMax?: number;
  japaneseLevel?: string;
  englishLevel?: string;
  citizenship?: string;
  workLocation?: string;
  workPercent?: number;
  ownerId: number;
  customerName?: string;
  contactName?: string;
  contactPosition?: string;
  ownerNickName?: string;
  version: number;
  analysisStatus: string;
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

// 匹配请求类型
export interface MatchRequest {
  demandId: number;
  supplyIds: number[];
  roleList?: Array<{ [key: string]: any }>;
  flagData?: { [key: string]: any };
}

// 匹配响应类型
export interface MatchResponse {
  success: boolean;
  message: string;
  matchResults?: Array<{ [key: string]: any }>;
}

/**
 * 创建需求
 * @param data 需求数据
 * @returns 创建结果
 */
export const createDemand = (data: DemandRequest): AxiosPromise<DemandResponse> => {
  return http.post('/rk/demand', data);
};

/**
 * 获取需求详情
 * @param demandId 需求ID
 * @returns 需求详情
 */
export const getDemandById = (demandId: number): AxiosPromise<DemandResponse> => {
  return http.get(`/rk/demand/${demandId}`);
};

/**
 * 更新需求
 * @param demandId 需求ID
 * @param data 更新数据
 * @returns 更新结果
 */
export const updateDemand = (demandId: number, data: Partial<DemandRequest>): AxiosPromise<DemandResponse> => {
  return http.put(`/rk/demand/${demandId}`, data);
};

/**
 * 删除需求
 * @param demandId 需求ID
 * @returns 删除结果
 */
export const deleteDemand = (demandId: number): AxiosPromise<void> => {
  return http.delete(`/rk/demand/${demandId}`);
};

/**
 * 获取需求列表
 * @param params 查询参数
 * @returns 需求列表
 */
export const getDemandList = (params?: PageRequest): AxiosPromise<PageResponse<DemandResponse>> => {
  return http.get('/rk/demand/list', { params });
};

/**
 * 执行匹配
 * @param data 匹配请求数据
 * @returns 匹配结果
 */
export const performMatch = (data: MatchRequest): AxiosPromise<MatchResponse> => {
  return http.post('/rk/match', data);
};