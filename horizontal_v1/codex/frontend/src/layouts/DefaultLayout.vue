<template>
  <div class="layout">
    <aside class="sider">
      <div class="logo">Work Assistant v3</div>
      <el-menu :default-active="active" router>
        <el-menu-item index="/">仪表盘</el-menu-item>
        <el-menu-item index="/rbac/users">用户管理</el-menu-item>
        <el-menu-item index="/rbac/roles">角色管理</el-menu-item>
        <el-menu-item index="/rbac/depts">部门管理</el-menu-item>
        <el-menu-item index="/rbac/perms">权限集合</el-menu-item>
        <el-menu-item index="/dict">字典管理</el-menu-item>
        <el-sub-menu index="/rk">
          <template #title>RK 核心</template>
          <el-menu-item index="/rk/vendor">供应商</el-menu-item>
          <el-menu-item index="/rk/customer">客户</el-menu-item>
          <el-menu-item index="/rk/vendor-contact">供应商联系人</el-menu-item>
          <el-menu-item index="/rk/customer-contact">客户联系人</el-menu-item>
        </el-sub-menu>
        <el-menu-item index="/supply">Supply/Match</el-menu-item>
        <el-menu-item index="/notice">通知</el-menu-item>
        <el-menu-item index="/shared-links">共享链接</el-menu-item>
      </el-menu>
    </aside>
    <div class="main">
      <header class="header">
        <div class="spacer" />
        <el-button type="text" @click="onLogout">退出</el-button>
      </header>
      <main class="content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const active = computed(() => route.path)

const onLogout = () => {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.layout { display: grid; grid-template-columns: 220px 1fr; min-height: 100vh; }
.sider { background: #1f2d3d; color: #fff; padding: 12px; }
.logo { font-weight: 600; margin: 8px 0 16px; }
.main { background: #f5f7fa; display: flex; flex-direction: column; min-height: 100vh; }
.header { height: 56px; display: flex; align-items: center; justify-content: flex-end; padding: 0 16px; background: #fff; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
.content { padding: 16px; }
</style>
