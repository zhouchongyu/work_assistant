<script setup lang="ts">
/**
 * Default application layout.
 *
 * Contains:
 * - Sidebar menu
 * - Header with user info
 * - Main content area
 */
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useMenuStore } from '@/stores/menu'
import { useUserStore } from '@/stores/user'
import SidebarMenu from '@/components/layout/SidebarMenu.vue'
import AppHeader from '@/components/layout/AppHeader.vue'

const route = useRoute()
const menuStore = useMenuStore()
const userStore = useUserStore()

const sidebarWidth = computed(() => (menuStore.isCollapsed ? '64px' : '220px'))
const activeMenu = computed(() => route.path)
</script>

<template>
  <el-container class="layout-container">
    <!-- Sidebar -->
    <el-aside :width="sidebarWidth" class="sidebar">
      <div class="logo">
        <img src="@/assets/logo.svg" alt="Logo" class="logo-img" />
        <span v-show="!menuStore.isCollapsed" class="logo-text">Work Assistant</span>
      </div>
      <SidebarMenu
        :menus="menuStore.visibleMenus"
        :collapse="menuStore.isCollapsed"
        :active="activeMenu"
      />
    </el-aside>

    <!-- Main container -->
    <el-container class="main-container">
      <!-- Header -->
      <el-header class="header">
        <AppHeader />
      </el-header>

      <!-- Content -->
      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <keep-alive>
            <component :is="Component" v-if="route.meta.keepAlive" />
          </keep-alive>
          <component :is="Component" v-if="!route.meta.keepAlive" />
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<style lang="scss" scoped>
.layout-container {
  height: 100vh;
  width: 100%;
}

.sidebar {
  background: #304156;
  transition: width 0.3s;
  overflow: hidden;

  .logo {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0 16px;
    background: #263445;

    .logo-img {
      width: 32px;
      height: 32px;
    }

    .logo-text {
      margin-left: 12px;
      color: #fff;
      font-size: 18px;
      font-weight: 600;
      white-space: nowrap;
    }
  }
}

.main-container {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.header {
  height: 60px;
  background: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  padding: 0 20px;
}

.main-content {
  flex: 1;
  padding: 20px;
  overflow: auto;
  background: #f5f7fa;
}
</style>
