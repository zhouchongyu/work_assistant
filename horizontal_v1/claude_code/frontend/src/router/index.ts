/**
 * Vue Router configuration.
 *
 * Features:
 * - Static and dynamic routes
 * - Navigation guards for auth
 * - Progress bar
 */
import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import NProgress from 'nprogress'
import { useUserStore } from '@/stores/user'
import { useMenuStore } from '@/stores/menu'

// Static routes (no auth required)
const staticRoutes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: { title: '登录', public: true },
  },
  {
    path: '/403',
    name: '403',
    component: () => import('@/views/error/403.vue'),
    meta: { title: '无权限', public: true },
  },
  {
    path: '/404',
    name: '404',
    component: () => import('@/views/error/404.vue'),
    meta: { title: '页面不存在', public: true },
  },
  {
    path: '/500',
    name: '500',
    component: () => import('@/views/error/500.vue'),
    meta: { title: '服务器错误', public: true },
  },
]

// Layout route (auth required)
const layoutRoute: RouteRecordRaw = {
  path: '/',
  name: 'Layout',
  component: () => import('@/layouts/DefaultLayout.vue'),
  redirect: '/dashboard',
  children: [
    {
      path: 'dashboard',
      name: 'Dashboard',
      component: () => import('@/views/dashboard/index.vue'),
      meta: { title: '工作台', icon: 'HomeFilled' },
    },
    // RK Business Routes
    {
      path: 'rk/supply',
      name: 'RkSupply',
      component: () => import('@/views/rk/supply/index.vue'),
      meta: { title: '简历管理', icon: 'Document' },
    },
    {
      path: 'rk/demand',
      name: 'RkDemand',
      component: () => import('@/views/rk/demand/index.vue'),
      meta: { title: '需求管理', icon: 'List' },
    },
    {
      path: 'rk/case',
      name: 'RkCase',
      component: () => import('@/views/rk/case/index.vue'),
      meta: { title: '案例管理', icon: 'Connection' },
    },
    {
      path: 'rk/customer',
      name: 'RkCustomer',
      component: () => import('@/views/rk/customer/index.vue'),
      meta: { title: '客户管理', icon: 'OfficeBuilding' },
    },
    {
      path: 'rk/vendor',
      name: 'RkVendor',
      component: () => import('@/views/rk/vendor/index.vue'),
      meta: { title: '供应商管理', icon: 'Shop' },
    },
    {
      path: 'rk/notice',
      name: 'RkNotice',
      component: () => import('@/views/rk/notice/index.vue'),
      meta: { title: '通知管理', icon: 'Bell' },
    },
    // System Routes
    {
      path: 'system/user',
      name: 'SystemUser',
      component: () => import('@/views/system/user/index.vue'),
      meta: { title: '用户管理', icon: 'User' },
    },
    {
      path: 'system/role',
      name: 'SystemRole',
      component: () => import('@/views/system/role/index.vue'),
      meta: { title: '角色管理', icon: 'UserFilled' },
    },
    {
      path: 'system/menu',
      name: 'SystemMenu',
      component: () => import('@/views/system/menu/index.vue'),
      meta: { title: '菜单管理', icon: 'Menu' },
    },
    {
      path: 'system/department',
      name: 'SystemDepartment',
      component: () => import('@/views/system/department/index.vue'),
      meta: { title: '部门管理', icon: 'Histogram' },
    },
    {
      path: 'system/dict',
      name: 'SystemDict',
      component: () => import('@/views/system/dict/index.vue'),
      meta: { title: '字典管理', icon: 'Collection' },
    },
    {
      path: 'system/log',
      name: 'SystemLog',
      component: () => import('@/views/system/log/index.vue'),
      meta: { title: '系统日志', icon: 'Tickets' },
    },
  ],
}

// 404 catch-all
const notFoundRoute: RouteRecordRaw = {
  path: '/:pathMatch(.*)*',
  redirect: '/404',
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [...staticRoutes, layoutRoute, notFoundRoute],
  scrollBehavior: () => ({ top: 0 }),
})

// Navigation guard
router.beforeEach(async (to, from, next) => {
  NProgress.start()

  // Set page title
  document.title = to.meta.title
    ? `${to.meta.title} - Work Assistant`
    : 'Work Assistant'

  const userStore = useUserStore()
  const menuStore = useMenuStore()

  // Public pages don't need auth
  if (to.meta.public) {
    // If already logged in, redirect to home
    if (to.path === '/login' && userStore.isLoggedIn) {
      next('/')
      return
    }
    next()
    return
  }

  // Check login status
  if (!userStore.isLoggedIn) {
    next({
      path: '/login',
      query: { redirect: to.fullPath },
    })
    return
  }

  // Fetch user info and menus if not loaded
  if (!userStore.userInfo) {
    try {
      await userStore.fetchUserInfo()
      await menuStore.fetchMenus()

      // Add dynamic routes
      const dynamicRoutes = menuStore.generateRoutes()
      dynamicRoutes.forEach(route => {
        router.addRoute('Layout', route)
      })

      // Retry navigation with new routes
      next({ ...to, replace: true })
      return
    } catch (error) {
      console.error('Failed to load user info:', error)
      userStore.logout()
      next('/login')
      return
    }
  }

  // Check permission if required
  if (to.meta.perms) {
    const perms = to.meta.perms as string
    if (!userStore.hasPermission(perms)) {
      next('/403')
      return
    }
  }

  next()
})

router.afterEach(() => {
  NProgress.done()
})

export default router

// Route meta type declaration
declare module 'vue-router' {
  interface RouteMeta {
    title?: string
    icon?: string
    public?: boolean
    keepAlive?: boolean
    perms?: string
  }
}
