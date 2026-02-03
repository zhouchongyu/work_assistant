/**
 * Axios request wrapper with interceptors.
 *
 * Features:
 * - Automatic token handling
 * - Response code normalization (code: 1000 = success)
 * - Error handling and user feedback
 * - Request/response logging (development)
 */
import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse } from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import router from '@/router'

// Response interface matching backend
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
  timestamp?: number
}

// Success code
const SUCCESS_CODE = 1000
// Business error code
const BUSINESS_ERROR_CODE = 1001
// Auth error codes
const AUTH_ERROR_CODES = [401, 403]

// Create axios instance
const request: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
request.interceptors.request.use(
  (config) => {
    const userStore = useUserStore()

    // Add token to headers
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }

    // Development logging
    if (import.meta.env.DEV) {
      console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`, config.data || config.params)
    }

    return config
  },
  (error) => {
    console.error('[API] Request error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor
request.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    const { data } = response

    // Development logging
    if (import.meta.env.DEV) {
      console.log(`[API] Response:`, data)
    }

    // Handle standard response format
    if (typeof data.code === 'number') {
      // Success
      if (data.code === SUCCESS_CODE) {
        return data.data
      }

      // Business error
      if (data.code === BUSINESS_ERROR_CODE) {
        ElMessage.error(data.message || '操作失败')
        return Promise.reject(new Error(data.message || '操作失败'))
      }

      // Other errors
      ElMessage.error(data.message || '请求失败')
      return Promise.reject(new Error(data.message || '请求失败'))
    }

    // Non-standard response, return as-is
    return data
  },
  (error) => {
    console.error('[API] Response error:', error)

    const { response } = error
    const userStore = useUserStore()

    if (response) {
      const { status, data } = response

      // Handle auth errors
      if (AUTH_ERROR_CODES.includes(status)) {
        // Avoid multiple prompts
        if (!window.__authErrorShowing) {
          window.__authErrorShowing = true
          ElMessageBox.confirm(
            '登录状态已过期，请重新登录',
            '系统提示',
            {
              confirmButtonText: '重新登录',
              cancelButtonText: '取消',
              type: 'warning',
            }
          )
            .then(() => {
              userStore.logout()
              router.push('/login')
            })
            .finally(() => {
              window.__authErrorShowing = false
            })
        }
        return Promise.reject(error)
      }

      // Other HTTP errors
      const message = data?.message || getHttpErrorMessage(status)
      ElMessage.error(message)
    } else if (error.message.includes('timeout')) {
      ElMessage.error('请求超时，请稍后重试')
    } else if (error.message.includes('Network Error')) {
      ElMessage.error('网络错误，请检查网络连接')
    } else {
      ElMessage.error('请求失败，请稍后重试')
    }

    return Promise.reject(error)
  }
)

/**
 * Get user-friendly HTTP error message.
 */
function getHttpErrorMessage(status: number): string {
  const messages: Record<number, string> = {
    400: '请求参数错误',
    401: '未授权，请登录',
    403: '拒绝访问',
    404: '请求地址不存在',
    405: '请求方法不允许',
    408: '请求超时',
    500: '服务器内部错误',
    501: '服务未实现',
    502: '网关错误',
    503: '服务不可用',
    504: '网关超时',
    505: 'HTTP版本不支持',
  }
  return messages[status] || `请求失败 (${status})`
}

// Type declaration for window
declare global {
  interface Window {
    __authErrorShowing?: boolean
  }
}

export default request

/**
 * Convenience methods for common HTTP operations.
 */
export const http = {
  get<T = any>(url: string, params?: any, config?: AxiosRequestConfig): Promise<T> {
    return request.get(url, { params, ...config })
  },

  post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return request.post(url, data, config)
  },

  put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return request.put(url, data, config)
  },

  delete<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return request.delete(url, { data, ...config })
  },

  patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return request.patch(url, data, config)
  },
}
