import type { Router } from 'vue-router'
import { useAuthStore } from '@/store/auth'

export function setupGuards(router: Router) {
  router.beforeEach((to, _from, next) => {
    const auth = useAuthStore()
    if (to.meta?.title) {
      document.title = `Work Assistant | ${to.meta.title as string}`
    }
    if (to.meta.public) {
      if (auth.token && to.path === '/login') {
        return next({ path: '/' })
      }
      return next()
    }
    if (!auth.token) {
      return next({ path: '/login', query: { redirect: to.fullPath } })
    }
    next()
  })
}
