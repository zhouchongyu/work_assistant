import { defineStore } from 'pinia'

interface UserInfo {
  id: number
  username?: string
  name?: string | null
  nickName?: string | null
}

const TOKEN_KEY = 'wa_token'
const USER_KEY = 'wa_user'
const REFRESH_TOKEN_KEY = 'wa_refresh_token'
const TOKEN_EXPIRE_KEY = 'wa_token_expire'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: (localStorage.getItem(TOKEN_KEY) as string) || '',
    refreshToken: (localStorage.getItem(REFRESH_TOKEN_KEY) as string) || '',
    expire: Number(localStorage.getItem(TOKEN_EXPIRE_KEY) || 0),
    user: (localStorage.getItem(USER_KEY) ? JSON.parse(localStorage.getItem(USER_KEY)!) : null) as UserInfo | null,
  }),
  actions: {
    setToken(token: string, refreshToken?: string, expire?: number) {
      this.token = token
      localStorage.setItem(TOKEN_KEY, token)
      if (refreshToken) {
        this.refreshToken = refreshToken
        localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken)
      }
      if (expire !== undefined) {
        this.expire = expire
        localStorage.setItem(TOKEN_EXPIRE_KEY, String(expire))
      }
    },
    setUser(user: UserInfo | null) {
      this.user = user
      if (user) localStorage.setItem(USER_KEY, JSON.stringify(user))
      else localStorage.removeItem(USER_KEY)
    },
    logout() {
      this.token = ''
      this.refreshToken = ''
      this.expire = 0
      this.user = null
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(REFRESH_TOKEN_KEY)
      localStorage.removeItem(TOKEN_EXPIRE_KEY)
      localStorage.removeItem(USER_KEY)
    },
  },
})
