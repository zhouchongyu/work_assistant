<template>
  <div class="page">
    <div class="toolbar">
      <el-input v-model="query.keyWord" placeholder="搜索角色名" clearable @change="onSearch" />
      <el-button type="primary" @click="loadData">刷新</el-button>
    </div>
    <el-table :data="rows" v-loading="loading" border stripe>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="角色标识" width="180" />
      <el-table-column prop="label" label="显示名" />
      <el-table-column prop="remark" label="备注" />
      <el-table-column prop="relevance" label="关联权限" width="120">
        <template #default="{ row }">
          <el-tag :type="row.relevance ? 'success' : 'info'">{{ row.relevance ? '是' : '否' }}</el-tag>
        </template>
      </el-table-column>
    </el-table>
    <div class="pagination">
      <el-pagination
        layout="prev, pager, next, jumper, ->, total"
        :page-size="query.size"
        :current-page="query.page"
        :total="total"
        @current-change="onPageChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { fetchRoles, type RoleItem } from '@/service/api/rbac'

const loading = ref(false)
const rows = ref<RoleItem[]>([])
const total = ref(0)
const query = reactive({ page: 1, size: 10, keyWord: '' })

const loadData = async () => {
  loading.value = true
  try {
    const res = await fetchRoles({ ...query })
    rows.value = res.list
    total.value = res.pagination.total
  } catch (e: any) {
    ElMessage.error(e.message || '加载角色失败')
  } finally {
    loading.value = false
  }
}

const onSearch = () => {
  query.page = 1
  loadData()
}

const onPageChange = (page: number) => {
  query.page = page
  loadData()
}

onMounted(() => {
  loadData()
})
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
  gap: 12px;
  margin-bottom: 12px;
}
.pagination {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
}
</style>
