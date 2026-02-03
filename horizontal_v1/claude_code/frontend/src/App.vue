<script setup lang="ts">
/**
 * Root application component.
 *
 * Handles:
 * - Global loading state
 * - Router view rendering
 */
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

// Try to restore user session on app load
onMounted(async () => {
  if (userStore.token) {
    try {
      await userStore.fetchUserInfo()
    } catch (e) {
      // Token expired or invalid, clear and redirect to login
      userStore.logout()
    }
  }
})
</script>

<template>
  <el-config-provider :locale="zhCn">
    <router-view />
  </el-config-provider>
</template>

<script lang="ts">
import zhCn from 'element-plus/es/locale/lang/zh-cn'
export default {
  name: 'App',
  setup() {
    return { zhCn }
  }
}
</script>

<style>
#app {
  width: 100%;
  height: 100%;
}
</style>
