/**
 * Authentication API.
 */
import { http } from './request'

export interface LoginRequest {
  username: string
  password: string
  captchaId?: string
  verifyCode?: string
}

export interface LoginResponse {
  token: string
  refreshToken?: string
  expire?: number
}

export interface CaptchaResponse {
  id: string
  data: string
}

export const authApi = {
  /**
   * User login.
   */
  login(data: LoginRequest): Promise<LoginResponse> {
    return http.post('/v1/open/login', data)
  },

  /**
   * Get captcha.
   */
  getCaptcha(params?: { width?: number; height?: number; type?: string }): Promise<CaptchaResponse> {
    return http.get('/v1/open/captcha', params)
  },

  /**
   * Refresh token.
   */
  refreshToken(refreshToken: string): Promise<LoginResponse> {
    return http.post('/v1/open/refreshToken', { refreshToken })
  },

  /**
   * Logout.
   */
  logout(): Promise<void> {
    return http.post('/v1/open/logout')
  },

  /**
   * Get current user info.
   */
  getUserInfo(): Promise<any> {
    return http.post('/v1/comm/person')
  },

  /**
   * Get current user permissions.
   */
  getPermissions(): Promise<{ perms: string[] }> {
    return http.post('/v1/comm/perms')
  },

  /**
   * Get current user menus.
   */
  getMenus(): Promise<any[]> {
    return http.post('/v1/comm/menu')
  },

  /**
   * Update password.
   */
  updatePassword(oldPassword: string, newPassword: string): Promise<void> {
    return http.post('/v1/comm/updatePassword', { oldPassword, newPassword })
  },
}

export default authApi
