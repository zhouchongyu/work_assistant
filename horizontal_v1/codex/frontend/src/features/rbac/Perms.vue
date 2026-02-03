<template>
  <div class="page">
    <div class="toolbar">
      <el-button type="primary" :loading="loading" @click="loadData">刷新</el-button>
    </div>
    <div class="perms" v-loading="loading">
      <el-empty v-if="!perms.length && !loading" description="暂无权限数据" />
      <el-space wrap>
        <el-tag v-for="item in perms" :key="item" type="info" effect="light">{{ item }}</el-tag>
      </el-space>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { fetchPerms } from '@/service/api/rbac'

const loading = ref(false)
const perms = ref<string[]>([])

const loadData = async () => {
  loading.value = true
  try {
    perms.value = await fetchPerms()
  } catch (e: any) {
    ElMessage.error(e.message || '加载权限失败')
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
.page {
  background: #fff;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}
.toolbar {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 12px;
}
.perms {
  min-height: 120px;
}
</style>
