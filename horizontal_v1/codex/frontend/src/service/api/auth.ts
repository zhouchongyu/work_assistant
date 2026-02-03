import http from '../http'

export interface LoginPayload {
  username: string
  password: string
  captchaId: string
  verifyCode: string
}

export interface TokenPair {
  token: string
  expire: number
  refreshToken: string
  refreshExpire: number
}

export interface MeResponse {
  id: number
  username: string
  name?: string | null
  nickName?: string | null
  departmentId?: number | null
  roleIdList: number[]
}

export interface CaptchaResponse {
  captchaId: string
  data: string
}

export const login = (payload: LoginPayload) => http.post<TokenPair>('/auth/login', payload)

export const fetchMe = () => http.get<MeResponse>('/auth/me')

export const fetchCaptcha = () => http.get<CaptchaResponse>('/auth/captcha')
