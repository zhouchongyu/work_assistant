// frontend/src/stores/auth.ts
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { login as loginApi, refreshToken as refreshTokenApi } from '@/api/modules/auth';

interface User {
  id: number;
  phone: string;
  name: string;
}

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null);
  const accessToken = ref<string | null>(null);
  const refreshToken = ref<string | null>(null);
  const isAuthenticated = computed(() => !!accessToken.value);

  // Actions
  const login = async (phone: string, password: string) => {
    try {
      const response = await loginApi({ phone, password });
      const { result } = response.data;
      
      user.value = result.userInfo;
      accessToken.value = result.accessToken;
      refreshToken.value = result.refreshToken;
      
      // 存储到localStorage
      localStorage.setItem('access_token', result.accessToken);
      localStorage.setItem('refresh_token', result.refreshToken);
      localStorage.setItem('user_info', JSON.stringify(result.userInfo));
      
      return { success: true, data: result };
    } catch (error) {
      return { success: false, error };
    }
  };

  const logout = () => {
    user.value = null;
    accessToken.value = null;
    refreshToken.value = null;
    
    // 清除localStorage
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_info');
  };

  const initializeAuth = () => {
    // 从localStorage恢复认证状态
    const storedAccessToken = localStorage.getItem('access_token');
    const storedRefreshToken = localStorage.getItem('refresh_token');
    const storedUser = localStorage.getItem('user_info');
    
    if (storedAccessToken && storedRefreshToken) {
      accessToken.value = storedAccessToken;
      refreshToken.value = storedRefreshToken;
      if (storedUser) {
        user.value = JSON.parse(storedUser);
      }
    }
  };

  const refreshTokens = async () => {
    if (!refreshToken.value) {
      throw new Error('No refresh token available');
    }
    
    try {
      const response = await refreshTokenApi({ refreshToken: refreshToken.value });
      const { result } = response.data;
      
      accessToken.value = result.accessToken;
      localStorage.setItem('access_token', result.accessToken);
      
      return { success: true, data: result };
    } catch (error) {
      logout(); // 如果刷新失败，登出用户
      return { success: false, error };
    }
  };

  return {
    user,
    accessToken,
    refreshToken,
    isAuthenticated,
    login,
    logout,
    initializeAuth,
    refreshTokens
  };
});