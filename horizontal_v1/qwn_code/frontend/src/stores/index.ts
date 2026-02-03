import { defineStore } from 'pinia';

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null as any,
    isAuthenticated: false,
    token: localStorage.getItem('access_token') || '',
  }),

  getters: {
    getUser: (state) => state.user,
    getIsAuthenticated: (state) => state.isAuthenticated,
    getToken: (state) => state.token,
  },

  actions: {
    setUser(userData: any) {
      this.user = userData;
      this.isAuthenticated = true;
    },

    setToken(token: string) {
      this.token = token;
      localStorage.setItem('access_token', token);
    },

    clearUser() {
      this.user = null;
      this.isAuthenticated = false;
      this.token = '';
      localStorage.removeItem('access_token');
    },
  },
});

export const useDictStore = defineStore('dict', {
  state: () => ({
    dicts: {} as Record<string, any[]>,
  }),

  actions: {
    setDict(dictType: string, dictData: any[]) {
      this.dicts[dictType] = dictData;
    },

    getDict(dictType: string) {
      return this.dicts[dictType] || [];
    },
  },
});