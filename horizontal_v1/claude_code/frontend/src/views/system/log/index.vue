<script setup lang="ts">
/**
 * System Log page.
 */
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import CrudTable from '@/components/crud/CrudTable.vue'
import type { Column, Pagination } from '@/components/crud/CrudTable.vue'
import { logApi, type SysLog, type LogListParams } from '@/api/system/log'

// Table columns
const columns: Column[] = [
  { prop: 'id', label: 'ID', width: 80 },
  { prop: 'userName', label: '用户', width: 100 },
  { prop: 'action', label: '操作', minWidth: 200 },
  { prop: 'ip', label: 'IP', width: 130 },
  { prop: 'ipAddr', label: 'IP地址', width: 150 },
  { prop: 'params', label: '参数', minWidth: 200, slot: 'params' },
  { prop: 'createTime', label: '时间', width: 180 },
]

// State
const loading = ref(false)
const tableData = ref<SysLog[]>([])
const pagination = reactive<Pagination>({
  page: 1,
  size: 20,
  total: 0,
})
const searchParams = reactive<LogListParams>({
  keyWord: '',
  action: '',
  startTime: undefined,
  endTime: undefined,
})
const dateRange = ref<[string, string] | null>(null)

// Load data
async function loadData() {
  loading.value = true
  try {
    const params: LogListParams = {
      page: pagination.page,
      size: pagination.size,
      ...searchParams,
    }
    if (dateRange.value) {
      params.startTime = dateRange.value[0]
      params.endTime = dateRange.value[1]
    }
    const { list, pagination: pager } = await logApi.getList(params)
    tableData.value = list || []
    pagination.total = pager?.total || 0
  } catch (e) {
    console.error('Failed to load log list:', e)
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
  searchParams.keyWord = ''
  searchParams.action = ''
  dateRange.value = null
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

// Clear logs
async function handleClear() {
  try {
    const { value } = await ElMessageBox.prompt('请输入要清理的日期（清理该日期之前的日志）', '清理日志', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputType: 'date',
    })
    await logApi.clear(value)
    ElMessage.success('清理成功')
    loadData()
  } catch (e) {
    // User cancelled
  }
}

// View params detail
const paramsDialogVisible = ref(false)
const currentParams = ref('')

function handleViewParams(row: SysLog) {
  currentParams.value = row.params || ''
  paramsDialogVisible.value = true
}

// Format params for display
function formatParams(params: string | undefined): string {
  if (!params) return '-'
  try {
    const obj = JSON.parse(params)
    return JSON.stringify(obj, null, 2)
  } catch {
    return params
  }
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="log-list">
    <!-- Search form -->
    <div class="page-card search-form">
      <el-form :model="searchParams" inline>
        <el-form-item label="关键词">
          <el-input
            v-model="searchParams.keyWord"
            placeholder="用户名/操作"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
          />
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
          <el-button
            v-permission="'base:sys:log:clear'"
            type="danger"
            @click="handleClear"
          >
            <el-icon><Delete /></el-icon>
            清理日志
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
        @page-change="handlePageChange"
        @size-change="handleSizeChange"
      >
        <!-- Params slot -->
        <template #params="{ row }">
          <el-button
            v-if="row.params"
            type="primary"
            link
            size="small"
            @click="handleViewParams(row)"
          >
            查看
          </el-button>
          <span v-else>-</span>
        </template>
      </CrudTable>
    </div>

    <!-- Params Dialog -->
    <el-dialog v-model="paramsDialogVisible" title="请求参数" width="600px">
      <pre class="params-content">{{ formatParams(currentParams) }}</pre>
      <template #footer>
        <el-button @click="paramsDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style lang="scss" scoped>
.log-list {
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

  .params-content {
    background: #f5f7fa;
    padding: 16px;
    border-radius: 4px;
    max-height: 400px;
    overflow: auto;
    font-family: monospace;
    font-size: 13px;
    line-height: 1.5;
    white-space: pre-wrap;
    word-break: break-all;
  }
}
</style>
