import { createRouter, createWebHistory } from 'vue-router';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('./views/Home.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('./views/Login.vue')
  },
  {
    path: '/rk',
    name: 'RK',
    component: () => import('./views/rk/Index.vue')
  },
  {
    path: '/chat',
    name: 'Chat',
    component: () => import('./views/Chat.vue')
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;