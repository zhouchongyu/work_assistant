<script setup lang="ts">
/**
 * Notice management page.
 */
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import CrudTable from '@/components/crud/CrudTable.vue'
import type { Column, Pagination } from '@/components/crud/CrudTable.vue'
import { noticeApi, type Notice, type NoticeListParams } from '@/api/rk/notice'

// Table columns
const columns: Column[] = [
  { prop: 'id', label: 'ID', width: 80 },
  { prop: 'title', label: '标题', minWidth: 200 },
  { prop: 'type', label: '类型', width: 100, slot: 'type' },
  { prop: 'isRead', label: '状态', width: 100, slot: 'isRead' },
  { prop: 'createTime', label: '创建时间', width: 180 },
]

// State
const loading = ref(false)
const tableData = ref<Notice[]>([])
const selectedRows = ref<Notice[]>([])
const pagination = reactive<Pagination>({
  page: 1,
  size: 20,
  total: 0,
})
const searchParams = reactive<NoticeListParams>({
  type: undefined,
  isRead: undefined,
})

// Dialog state
const detailDialogVisible = ref(false)
const currentNotice = ref<Notice | null>(null)

// Load data
async function loadData() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      size: pagination.size,
      ...searchParams,
    }
    const { list, pagination: pager } = await noticeApi.getList(params)
    tableData.value = list || []
    pagination.total = pager?.total || 0
  } catch (e) {
    console.error('Failed to load notice list:', e)
  } finally {
    loading.value = false
  }
}

// Search
function handleSearch() {
  pagination.page = 1
  loadData()
}

// Reset search
function handleReset() {
  searchParams.type = undefined
  searchParams.isRead = undefined
  handleSearch()
}

// Page change
function handlePageChange(page: number) {
  pagination.page = page
  loadData()
}

// Size change
function handleSizeChange(size: number) {
  pagination.size = size
  pagination.page = 1
  loadData()
}

// Selection change
function handleSelectionChange(rows: Notice[]) {
  selectedRows.value = rows
}

// View detail
async function handleView(row: Notice) {
  currentNotice.value = row
  detailDialogVisible.value = true

  // Mark as read if not already
  if (!row.isRead) {
    try {
      await noticeApi.markRead(row.id)
      row.isRead = true
    } catch (e) {
      console.error('Failed to mark as read:', e)
    }
  }
}

// Mark all as read
async function handleMarkAllRead() {
  try {
    await noticeApi.markAllRead()
    ElMessage.success('全部标记为已读')
    loadData()
  } catch (e) {
    console.error('Failed to mark all as read:', e)
  }
}

// Delete
async function handleDelete(row?: Notice) {
  const ids = row ? [row.id] : selectedRows.value.map(r => r.id)
  if (ids.length === 0) {
    ElMessage.warning('请选择要删除的数据')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${ids.length} 条数据吗？`,
      '提示',
      { type: 'warning' }
    )
    await noticeApi.delete(ids)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    // User cancelled
  }
}

// Type map
const typeMap: Record<string, { label: string; type: string }> = {
  system: { label: '系统通知', type: 'primary' },
  extract: { label: '解析通知', type: 'success' },
  match: { label: '匹配通知', type: 'warning' },
  case: { label: '案例通知', type: '' },
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="notice-list">
    <!-- Search form -->
    <div class="page-card search-form">
      <el-form :model="searchParams" inline>
        <el-form-item label="类型">
          <el-select v-model="searchParams.type" placeholder="全部" clearable>
            <el-option label="系统通知" value="system" />
            <el-option label="解析通知" value="extract" />
            <el-option label="匹配通知" value="match" />
            <el-option label="案例通知" value="case" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchParams.isRead" placeholder="全部" clearable>
            <el-option label="未读" :value="false" />
            <el-option label="已读" :value="true" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- Table -->
    <div class="page-card">
      <!-- Toolbar -->
      <div class="table-toolbar">
        <div class="toolbar-left">
          <el-button type="primary" @click="handleMarkAllRead">
            <el-icon><Check /></el-icon>
            全部已读
          </el-button>
          <el-button
            type="danger"
            :disabled="selectedRows.length === 0"
            @click="handleDelete()"
          >
            <el-icon><Delete /></el-icon>
            批量删除
          </el-button>
        </div>
        <div class="toolbar-right">
          <el-button @click="loadData">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </div>

      <!-- Table -->
      <CrudTable
        :data="tableData"
        :columns="columns"
        :loading="loading"
        :pagination="pagination"
        selection
        @page-change="handlePageChange"
        @size-change="handleSizeChange"
        @selection-change="handleSelectionChange"
      >
        <!-- Type slot -->
        <template #type="{ row }">
          <el-tag :type="typeMap[row.type]?.type as any || 'info'" size="small">
            {{ typeMap[row.type]?.label || row.type }}
          </el-tag>
        </template>

        <!-- Read status slot -->
        <template #isRead="{ row }">
          <el-tag :type="row.isRead ? 'info' : 'danger'" size="small">
            {{ row.isRead ? '已读' : '未读' }}
          </el-tag>
        </template>

        <!-- Actions column -->
        <template #actions>
          <el-table-column label="操作" width="150" fixed="right" align="center">
            <template #default="{ row }">
              <el-button
                type="primary"
                link
                size="small"
                @click="handleView(row)"
              >
                查看
              </el-button>
              <el-button
                type="danger"
                link
                size="small"
                @click="handleDelete(row)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </template>
      </CrudTable>
    </div>

    <!-- Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" title="通知详情" width="600px">
      <div v-if="currentNotice" class="notice-detail">
        <h3>{{ currentNotice.title }}</h3>
        <div class="notice-meta">
          <el-tag :type="typeMap[currentNotice.type]?.type as any || 'info'" size="small">
            {{ typeMap[currentNotice.type]?.label || currentNotice.type }}
          </el-tag>
          <span class="time">{{ currentNotice.createTime }}</span>
        </div>
        <div class="notice-content">
          {{ currentNotice.content }}
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style lang="scss" scoped>
.notice-list {
  .table-toolbar {
    display: flex;
    justify-content: space-between;
    margin-bottom: 16px;

    .toolbar-left,
    .toolbar-right {
      display: flex;
      gap: 8px;
    }
  }

  .notice-detail {
    h3 {
      margin: 0 0 16px 0;
      font-size: 18px;
    }

    .notice-meta {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 16px;
      color: #999;

      .time {
        font-size: 14px;
      }
    }

    .notice-content {
      padding: 16px;
      background: #f5f7fa;
      border-radius: 4px;
      line-height: 1.6;
      white-space: pre-wrap;
    }
  }
}
</style>
