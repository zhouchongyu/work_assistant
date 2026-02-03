<template>
  <div class="page">
    <el-card>
      <template #header>共享链接查看</template>
      <el-form :model="form" inline>
        <el-form-item label="类型">
          <el-select v-model="form.type" placeholder="类型">
            <el-option label="Supply" value="supply" />
            <el-option label="Demand" value="demand" />
          </el-select>
        </el-form-item>
        <el-form-item label="ShareToken">
          <el-input v-model="form.shareToken" placeholder="输入分享 token" style="width: 260px" />
        </el-form-item>
        <el-button type="primary" :loading="loading" @click="load">查询</el-button>
      </el-form>

      <el-alert type="info" show-icon :closable="false" class="mb-2"
        title="提示：需从后端生成的分享 token 查询共享列表；若为 Supply 且文件非 PDF 将跳转 Office Viewer。" />

      <el-table :data="rows" v-loading="loading" border stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="名称/备注" />
        <el-table-column v-if="form.type === 'supply'" prop="url" label="预览链接">
          <template #default="{ row }">
            <el-link v-if="row.url" :href="row.url" target="_blank">预览</el-link>
          </template>
        </el-table-column>
        <el-table-column v-if="form.type === 'supply'" prop="downloadUrl" label="下载">
          <template #default="{ row }">
            <el-link v-if="row.downloadUrl" :href="row.downloadUrl" target="_blank">下载</el-link>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { fetchSharedList, type SharedDemandItem, type SharedSupplyItem } from '@/service/api/shared_links'

const form = reactive<{ type: 'supply' | 'demand'; shareToken: string }>({ type: 'supply', shareToken: '' })
const rows = ref<(SharedSupplyItem | SharedDemandItem)[]>([])
const loading = ref(false)

const load = async () => {
  if (!form.shareToken) {
    ElMessage.warning('请输入 shareToken')
    return
  }
  loading.value = true
  try {
    rows.value = await fetchSharedList({ ...form })
  } catch (e: any) {
    ElMessage.error(e.message || '查询失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.page {
  padding: 8px;
}
.mb-2 {
  margin-bottom: 12px;
}
</style>
