<script setup lang="ts">
/**
 * Sidebar menu component.
 *
 * Renders menu tree with support for:
 * - Nested menus
 * - Icons
 * - Collapse mode
 */
import type { MenuItem } from '@/stores/menu'

defineProps<{
  menus: MenuItem[]
  collapse: boolean
  active: string
}>()

function getMenuIcon(icon?: string) {
  // Return Element Plus icon name if provided
  return icon || 'Menu'
}
</script>

<template>
  <el-menu
    :default-active="active"
    :collapse="collapse"
    :unique-opened="true"
    :collapse-transition="false"
    router
    background-color="#304156"
    text-color="#bfcbd9"
    active-text-color="#409eff"
    class="sidebar-menu"
  >
    <template v-for="menu in menus" :key="menu.id">
      <!-- Menu with children -->
      <el-sub-menu v-if="menu.children?.length" :index="menu.router || String(menu.id)">
        <template #title>
          <el-icon><component :is="getMenuIcon(menu.icon)" /></el-icon>
          <span>{{ menu.name }}</span>
        </template>
        <template v-for="child in menu.children" :key="child.id">
          <!-- Nested submenu -->
          <el-sub-menu
            v-if="child.children?.length"
            :index="child.router || String(child.id)"
          >
            <template #title>
              <el-icon><component :is="getMenuIcon(child.icon)" /></el-icon>
              <span>{{ child.name }}</span>
            </template>
            <el-menu-item
              v-for="grandchild in child.children"
              :key="grandchild.id"
              :index="grandchild.router || ''"
            >
              <el-icon><component :is="getMenuIcon(grandchild.icon)" /></el-icon>
              <span>{{ grandchild.name }}</span>
            </el-menu-item>
          </el-sub-menu>
          <!-- Child menu item -->
          <el-menu-item v-else :index="child.router || ''">
            <el-icon><component :is="getMenuIcon(child.icon)" /></el-icon>
            <span>{{ child.name }}</span>
          </el-menu-item>
        </template>
      </el-sub-menu>

      <!-- Menu without children -->
      <el-menu-item v-else :index="menu.router || ''">
        <el-icon><component :is="getMenuIcon(menu.icon)" /></el-icon>
        <span>{{ menu.name }}</span>
      </el-menu-item>
    </template>
  </el-menu>
</template>

<style lang="scss" scoped>
.sidebar-menu {
  border-right: none;
  height: calc(100% - 60px);
  overflow-y: auto;
  overflow-x: hidden;

  &:not(.el-menu--collapse) {
    width: 220px;
  }
}

:deep(.el-menu-item),
:deep(.el-sub-menu__title) {
  &:hover {
    background-color: #263445 !important;
  }
}

:deep(.el-menu-item.is-active) {
  background-color: #409eff !important;
  color: #fff !important;
}
</style>
