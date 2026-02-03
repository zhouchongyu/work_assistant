import axios from 'axios'
import { useAuthStore } from '@/store/auth'
import router from '@/router'

const http = axios.create({ baseURL: '/api/v1' })

http.interceptors.request.use((config) => {
  const auth = useAuthStore()
  config.headers = config.headers || {}
  if (auth.token) {
    config.headers.Authorization = `Bearer ${auth.token}`
  }
  if (!config.headers['x-request-id']) {
    config.headers['x-request-id'] = crypto.randomUUID()
  }
  return config
})

http.interceptors.response.use(
  (resp) => {
    const data = resp.data
    if (data && typeof data === 'object' && 'code' in data) {
      if (data.code === 1000) return data.result
      return Promise.reject(new Error(data.message || '业务错误'))
    }
    return data
  },
  (error) => {
    const status = error?.response?.status
    if (status === 401 || status === 403) {
      const auth = useAuthStore()
      auth.logout()
      router.push('/login')
    }
    return Promise.reject(error)
  }
)

export default http
