<template>
  <div class="page">
    <el-card class="mb-2">
      <template #header>新增客户</template>
      <el-form :model="form" inline>
        <el-form-item label="名称">
          <el-input v-model="form.name" placeholder="客户名称" />
        </el-form-item>
        <el-form-item label="编码">
          <el-input v-model="form.code" placeholder="编码/编号" />
        </el-form-item>
        <el-button type="primary" :loading="creating" @click="create">创建</el-button>
      </el-form>
    </el-card>

    <el-card>
      <template #header>客户列表</template>
      <div class="toolbar">
        <el-switch v-model="query.activeSwitch" active-text="仅显示启用" inactive-text="全部" @change="load" />
        <el-button type="primary" size="small" :loading="loading" @click="load">刷新</el-button>
      </div>
      <el-table :data="rows" v-loading="loading" border stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="code" label="编码" />
      </el-table>
      <div class="pagination">
        <el-pagination
          layout="prev, pager, next, jumper, ->, total"
          :page-size="query.size"
          :current-page="query.page"
          :total="total"
          @current-change="(p:number)=>{query.page=p;load();}"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { addCustomer, fetchCustomers, type CustomerItem } from '@/service/api/rk_customer'

const form = reactive({ name: '', code: '' })
const creating = ref(false)
const loading = ref(false)
const rows = ref<CustomerItem[]>([])
const total = ref(0)
const query = reactive({ page: 1, size: 10, activeSwitch: false })

const load = async () => {
  loading.value = true
  try {
    const res = await fetchCustomers({ ...query })
    rows.value = res.list
    total.value = res.pagination.total
  } catch (e: any) {
    ElMessage.error(e.message || '加载客户失败')
  } finally {
    loading.value = false
  }
}

const create = async () => {
  if (!form.name || !form.code) {
    ElMessage.warning('请填写名称和编码')
    return
  }
  creating.value = true
  try {
    await addCustomer({ name: form.name, code: form.code })
    ElMessage.success('创建成功')
    load()
  } catch (e: any) {
    ElMessage.error(e.message || '创建失败')
  } finally {
    creating.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.page {
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.pagination {
  margin-top: 8px;
  display: flex;
  justify-content: flex-end;
}
.mb-2 {
  margin-bottom: 12px;
}
</style>
