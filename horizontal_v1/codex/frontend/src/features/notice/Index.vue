<template>
  <div class="page">
    <div class="toolbar">
      <el-select v-model="query.isRead" placeholder="全部" clearable @change="load">
        <el-option label="未读" :value="false" />
        <el-option label="已读" :value="true" />
      </el-select>
      <el-button type="primary" :loading="loading" @click="load">刷新</el-button>
      <el-tag type="danger" v-if="unread > 0">未读 {{ unread }}</el-tag>
    </div>
    <el-table :data="rows" v-loading="loading" border stripe>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="content" label="内容" />
      <el-table-column prop="type" label="类型" width="100" />
      <el-table-column prop="model" label="模块" width="120" />
      <el-table-column prop="createdAt" label="时间" width="180" />
      <el-table-column prop="isRead" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.isRead ? 'success' : 'warning'">{{ row.isRead ? '已读' : '未读' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column width="120" label="操作">
        <template #default="{ row }">
          <el-button v-if="!row.isRead" size="small" type="primary" text @click="mark([row.id])">标记已读</el-button>
        </template>
      </el-table-column>
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
    <div class="actions">
      <el-button type="success" plain :disabled="!unreadIds.length" @click="mark(unreadIds)">全部标记已读</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { fetchNotices, markRead, unreadCount, type NoticeItem } from '@/service/api/notice'

const loading = ref(false)
const rows = ref<NoticeItem[]>([])
const total = ref(0)
const unread = ref(0)
const query = reactive<{ page: number; size: number; isRead?: boolean | null }>({ page: 1, size: 10, isRead: null })

const unreadIds = computed(() => rows.value.filter((n) => !n.isRead).map((n) => n.id))

const load = async () => {
  loading.value = true
  try {
    const res = await fetchNotices({ ...query, isRead: query.isRead === null ? undefined : query.isRead ?? undefined })
    rows.value = res.list
    total.value = res.pagination.total
    unread.value = await unreadCount()
  } catch (e: any) {
    ElMessage.error(e.message || '加载通知失败')
  } finally {
    loading.value = false
  }
}

const mark = async (ids: number[]) => {
  if (!ids.length) return
  try {
    await markRead(ids)
    ElMessage.success('已标记已读')
    load()
  } catch (e: any) {
    ElMessage.error(e.message || '标记失败')
  }
}

onMounted(load)
</script>

<style scoped>
.page {
  padding: 8px;
}
.toolbar {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 12px;
}
.pagination {
  margin-top: 8px;
  display: flex;
  justify-content: flex-end;
}
.actions {
  margin-top: 8px;
}
</style>
