<script setup lang="ts">
/**
 * Application header component.
 *
 * Contains:
 * - Menu collapse toggle
 * - Breadcrumb navigation
 * - User menu
 */
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMenuStore } from '@/stores/menu'
import { useUserStore } from '@/stores/user'
import { ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const menuStore = useMenuStore()
const userStore = useUserStore()

// Breadcrumb items from route
const breadcrumbs = computed(() => {
  const matched = route.matched.filter(item => item.meta?.title)
  return matched.map(item => ({
    title: item.meta.title as string,
    path: item.path,
  }))
})

// User avatar or default
const userAvatar = computed(() => {
  return userStore.userInfo?.avatar || ''
})

// User display name
const displayName = computed(() => {
  return userStore.userInfo?.nickName || userStore.userInfo?.username || '用户'
})

// Toggle sidebar collapse
function toggleSidebar() {
  menuStore.toggleCollapse()
}

// Handle user menu command
function handleCommand(command: string) {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'password':
      router.push('/password')
      break
    case 'logout':
      handleLogout()
      break
  }
}

// Logout confirmation
function handleLogout() {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(() => {
    userStore.logout()
  })
}
</script>

<template>
  <div class="header-content">
    <!-- Left side -->
    <div class="header-left">
      <!-- Collapse toggle -->
      <el-icon class="collapse-btn" @click="toggleSidebar">
        <Fold v-if="!menuStore.isCollapsed" />
        <Expand v-else />
      </el-icon>

      <!-- Breadcrumb -->
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/' }">
          <el-icon><HomeFilled /></el-icon>
        </el-breadcrumb-item>
        <el-breadcrumb-item v-for="item in breadcrumbs" :key="item.path">
          {{ item.title }}
        </el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <!-- Right side -->
    <div class="header-right">
      <!-- User menu -->
      <el-dropdown @command="handleCommand">
        <div class="user-info">
          <el-avatar :size="32" :src="userAvatar">
            <el-icon><User /></el-icon>
          </el-avatar>
          <span class="user-name">{{ displayName }}</span>
          <el-icon class="el-icon--right"><ArrowDown /></el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile">
              <el-icon><User /></el-icon>
              个人中心
            </el-dropdown-item>
            <el-dropdown-item command="password">
              <el-icon><Lock /></el-icon>
              修改密码
            </el-dropdown-item>
            <el-dropdown-item divided command="logout">
              <el-icon><SwitchButton /></el-icon>
              退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.header-content {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;

  .collapse-btn {
    font-size: 20px;
    cursor: pointer;
    margin-right: 16px;
    color: #606266;

    &:hover {
      color: #409eff;
    }
  }
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 0 12px;

  &:hover {
    background: #f5f7fa;
    border-radius: 4px;
  }

  .user-name {
    margin-left: 8px;
    color: #606266;
  }
}
</style>
