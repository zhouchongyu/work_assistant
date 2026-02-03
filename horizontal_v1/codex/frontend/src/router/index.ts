import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { setupGuards } from './guards'
import DefaultLayout from '@/layouts/DefaultLayout.vue'

const routes: RouteRecordRaw[] = [
  { path: '/login', name: 'login', component: () => import('@/views/Login.vue'), meta: { public: true, title: '登录' } },
  {
    path: '/',
    component: DefaultLayout,
    children: [
      { path: '', name: 'dashboard', component: () => import('@/views/Dashboard.vue'), meta: { title: '仪表盘' } },
      { path: 'rbac/users', name: 'rbac-users', component: () => import('@/features/rbac/Users.vue'), meta: { title: '用户管理' } },
      { path: 'rbac/roles', name: 'rbac-roles', component: () => import('@/features/rbac/Roles.vue'), meta: { title: '角色管理' } },
      { path: 'rbac/depts', name: 'rbac-depts', component: () => import('@/features/rbac/Depts.vue'), meta: { title: '部门管理' } },
      { path: 'rbac/perms', name: 'rbac-perms', component: () => import('@/features/rbac/Perms.vue'), meta: { title: '权限集合' } },
      { path: 'dict', name: 'dict', component: () => import('@/features/dict/Index.vue'), meta: { title: '字典管理' } },
      { path: 'rk/vendor', name: 'rk-vendor', component: () => import('@/features/rk/Vendor.vue'), meta: { title: '供应商' } },
      { path: 'rk/customer', name: 'rk-customer', component: () => import('@/features/rk/Customer.vue'), meta: { title: '客户' } },
      { path: 'rk/vendor-contact', name: 'rk-vendor-contact', component: () => import('@/features/rk/VendorContact.vue'), meta: { title: '供应商联系人' } },
      { path: 'rk/customer-contact', name: 'rk-customer-contact', component: () => import('@/features/rk/CustomerContact.vue'), meta: { title: '客户联系人' } },
      { path: 'notice', name: 'notice', component: () => import('@/features/notice/Index.vue'), meta: { title: '通知' } },
      { path: 'shared-links', name: 'shared-links', component: () => import('@/features/shared/SharedLinks.vue'), meta: { title: '共享链接' } },
      { path: 'supply', name: 'supply', component: () => import('@/features/supply/Index.vue'), meta: { title: 'Supply/Match' } },
    ],
  },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

setupGuards(router)

export default router
