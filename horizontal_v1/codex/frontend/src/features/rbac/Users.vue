<template>
  <div class="page">
    <div class="toolbar">
      <el-input v-model="query.keyWord" placeholder="搜索用户名/姓名" clearable @change="onSearch" />
      <el-button type="primary" @click="loadData">刷新</el-button>
    </div>
    <el-table :data="rows" v-loading="loading" border stripe>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="username" label="用户名" width="160" />
      <el-table-column prop="name" label="姓名" width="140" />
      <el-table-column prop="departmentName" label="部门" width="160" />
      <el-table-column prop="roleName" label="角色" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 1 ? 'success' : 'info'">{{ row.status === 1 ? '启用' : '禁用' }}</el-tag>
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
import { fetchUsers, type UserItem } from '@/service/api/rbac'

const loading = ref(false)
const rows = ref<UserItem[]>([])
const total = ref(0)
const query = reactive({ page: 1, size: 10, keyWord: '' })

const loadData = async () => {
  loading.value = true
  try {
    const res = await fetchUsers({ ...query })
    rows.value = res.list
    total.value = res.pagination.total
  } catch (e: any) {
    ElMessage.error(e.message || '加载用户失败')
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
