// frontend/src/api/modules/auth.ts
import http from '../http';
import { AxiosPromise } from 'axios';

// 登录请求参数类型
export interface LoginRequest {
  phone: string;
  password: string;
}

// 登录响应类型
export interface LoginResponse {
  code: number;
  message: string;
  result: {
    accessToken: string;
    refreshToken: string;
    userInfo: {
      id: number;
      phone: string;
      name: string;
    };
  };
  requestId?: string;
}

// 刷新令牌请求参数类型
export interface RefreshTokenRequest {
  refreshToken: string;
}

// 刷新令牌响应类型
export interface RefreshTokenResponse {
  code: number;
  message: string;
  result: {
    accessToken: string;
  };
  requestId?: string;
}

/**
 * 用户登录
 * @param data 登录参数
 * @returns 登录响应
 */
export const login = (data: LoginRequest): AxiosPromise<LoginResponse> => {
  return http.post('/auth/login', data);
};

/**
 * 刷新访问令牌
 * @param data 刷新令牌参数
 * @returns 刷新令牌响应
 */
export const refreshToken = (data: RefreshTokenRequest): AxiosPromise<RefreshTokenResponse> => {
  return http.post('/auth/refresh-token', data);
};

/**
 * 获取当前用户信息
 * @returns 用户信息
 */
export const getCurrentUser = (): AxiosPromise<any> => {
  return http.get('/auth/current-user');
};