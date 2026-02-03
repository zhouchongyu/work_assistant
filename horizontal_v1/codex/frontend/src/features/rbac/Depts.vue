<template>
  <div class="page">
    <div class="toolbar">
      <el-button type="primary" @click="loadData" :loading="loading">刷新</el-button>
    </div>
    <el-tree
      v-loading="loading"
      :data="treeData"
      node-key="id"
      default-expand-all
      :props="treeProps"
      highlight-current
      empty-text="暂无部门数据"
    >
      <template #default="{ data }">
        <span class="tree-node">
          <strong>{{ data.name }}</strong>
          <small v-if="data.orderNum" class="muted">排序: {{ data.orderNum }}</small>
        </span>
      </template>
    </el-tree>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { fetchDeptTree, type DeptTreeNode } from '@/service/api/rbac'

const loading = ref(false)
const treeData = ref<DeptTreeNode[]>([])
const treeProps = { label: 'name', children: 'children' }

const loadData = async () => {
  loading.value = true
  try {
    treeData.value = await fetchDeptTree()
  } catch (e: any) {
    ElMessage.error(e.message || '加载部门失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => loadData())
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
.tree-node {
  display: inline-flex;
  gap: 8px;
  align-items: center;
}
.muted {
  color: #9ca3af;
}
</style>
