/**
 * User store for authentication and user state.
 *
 * Manages:
 * - Access/Refresh tokens
 * - User info and permissions
 * - Login/Logout operations
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { http } from '@/api/request'
import router from '@/router'

export interface UserInfo {
  userId: number
  username: string
  nickName: string
  email?: string
  phone?: string
  avatar?: string
  departmentId?: number
  departmentName?: string
  roleIds: number[]
  roles: string[]
}

const TOKEN_KEY = 'wa_token'
const REFRESH_TOKEN_KEY = 'wa_refresh_token'
const USER_INFO_KEY = 'wa_user_info'

export const useUserStore = defineStore('user', () => {
  // State
  const token = ref<string>(localStorage.getItem(TOKEN_KEY) || '')
  const refreshToken = ref<string>(localStorage.getItem(REFRESH_TOKEN_KEY) || '')
  const userInfo = ref<UserInfo | null>(
    JSON.parse(localStorage.getItem(USER_INFO_KEY) || 'null')
  )
  const permissions = ref<string[]>([])

  // Getters
  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => userInfo.value?.username === 'admin')
  const userId = computed(() => userInfo.value?.userId)
  const username = computed(() => userInfo.value?.username)
  const nickName = computed(() => userInfo.value?.nickName)

  // Actions
  async function login(username: string, password: string, captchaId?: string, verifyCode?: string) {
    const data = await http.post('/v1/open/login', {
      username,
      password,
      captchaId,
      verifyCode,
    })

    // Save tokens
    token.value = data.token
    refreshToken.value = data.refreshToken || ''
    localStorage.setItem(TOKEN_KEY, data.token)
    if (data.refreshToken) {
      localStorage.setItem(REFRESH_TOKEN_KEY, data.refreshToken)
    }

    // Fetch user info after login
    await fetchUserInfo()

    return data
  }

  async function fetchUserInfo() {
    const data = await http.post('/v1/comm/person')

    userInfo.value = {
      userId: data.id,
      username: data.username,
      nickName: data.nickName || data.username,
      email: data.email,
      phone: data.phone,
      avatar: data.avatar,
      departmentId: data.departmentId,
      departmentName: data.departmentName,
      roleIds: data.roleIds || [],
      roles: data.roles || [],
    }

    // Get permissions
    const permsData = await http.post('/v1/comm/perms')
    permissions.value = permsData.perms || []

    // Save to localStorage
    localStorage.setItem(USER_INFO_KEY, JSON.stringify(userInfo.value))

    return userInfo.value
  }

  async function refreshUserToken() {
    if (!refreshToken.value) {
      throw new Error('No refresh token')
    }

    const data = await http.post('/v1/open/refreshToken', {
      refreshToken: refreshToken.value,
    })

    token.value = data.token
    refreshToken.value = data.refreshToken || refreshToken.value
    localStorage.setItem(TOKEN_KEY, data.token)
    if (data.refreshToken) {
      localStorage.setItem(REFRESH_TOKEN_KEY, data.refreshToken)
    }

    return data
  }

  function logout() {
    // Clear state
    token.value = ''
    refreshToken.value = ''
    userInfo.value = null
    permissions.value = []

    // Clear localStorage
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
    localStorage.removeItem(USER_INFO_KEY)

    // Redirect to login
    router.push('/login')
  }

  function hasPermission(permission: string): boolean {
    // Admin has all permissions
    if (isAdmin.value) return true
    // Check permission list
    return permissions.value.includes(permission)
  }

  function hasAnyPermission(perms: string[]): boolean {
    if (isAdmin.value) return true
    return perms.some(p => permissions.value.includes(p))
  }

  function hasAllPermissions(perms: string[]): boolean {
    if (isAdmin.value) return true
    return perms.every(p => permissions.value.includes(p))
  }

  return {
    // State
    token,
    refreshToken,
    userInfo,
    permissions,

    // Getters
    isLoggedIn,
    isAdmin,
    userId,
    username,
    nickName,

    // Actions
    login,
    fetchUserInfo,
    refreshUserToken,
    logout,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
  }
})
