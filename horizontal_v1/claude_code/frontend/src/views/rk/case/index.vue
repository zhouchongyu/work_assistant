<script setup lang="ts">
/**
 * Case (Supply-Demand Link) management page.
 */
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import CrudTable from '@/components/crud/CrudTable.vue'
import type { Column, Pagination } from '@/components/crud/CrudTable.vue'
import { caseApi, CASE_STATUS, type Case, type CaseListParams } from '@/api/rk/case'

const router = useRouter()

// Table columns
const columns: Column[] = [
  { prop: 'id', label: 'ID', width: 80 },
  { prop: 'supplyName', label: '候选人', minWidth: 100 },
  { prop: 'demandTitle', label: '职位', minWidth: 150 },
  { prop: 'customerName', label: '客户', minWidth: 120 },
  { prop: 'status', label: '状态', width: 120, slot: 'status' },
  { prop: 'ownerName', label: '负责人', width: 100 },
  { prop: 'createTime', label: '创建时间', width: 180 },
  { prop: 'updateTime', label: '更新时间', width: 180 },
]

// State
const loading = ref(false)
const tableData = ref<Case[]>([])
const selectedRows = ref<Case[]>([])
const pagination = reactive<Pagination>({
  page: 1,
  size: 20,
  total: 0,
})
const searchParams = reactive<CaseListParams>({
  keyWord: '',
  status: undefined,
  customerId: undefined,
})

// Load data
async function loadData() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      size: pagination.size,
      ...searchParams,
    }
    const { list, pagination: pager } = await caseApi.getList(params)
    tableData.value = list || []
    pagination.total = pager?.total || 0
  } catch (e) {
    console.error('Failed to load case list:', e)
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
  searchParams.status = undefined
  searchParams.customerId = undefined
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
function handleSelectionChange(rows: Case[]) {
  selectedRows.value = rows
}

// Add new
function handleAdd() {
  router.push('/rk/case/add')
}

// Edit
function handleEdit(row: Case) {
  router.push(`/rk/case/edit/${row.id}`)
}

// View detail
function handleView(row: Case) {
  router.push(`/rk/case/detail/${row.id}`)
}

// Delete
async function handleDelete(row?: Case) {
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
    await caseApi.delete(ids)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    // User cancelled
  }
}

// Update status
async function handleUpdateStatus(row: Case, newStatus: number) {
  try {
    await ElMessageBox.confirm(
      `确定要将状态更改为"${statusMap[newStatus]?.label}"吗？`,
      '提示',
      { type: 'warning' }
    )
    await caseApi.updateStatus(row.id, newStatus)
    ElMessage.success('状态更新成功')
    loadData()
  } catch (e) {
    // User cancelled or error
  }
}

// Status map
const statusMap: Record<number, { label: string; type: string }> = {
  [CASE_STATUS.CREATED]: { label: '新建', type: 'info' },
  [CASE_STATUS.SUBMITTED]: { label: '已提交', type: '' },
  [CASE_STATUS.SHORTLISTED]: { label: '入围', type: 'warning' },
  [CASE_STATUS.INTERVIEW_SCHEDULED]: { label: '已约面试', type: '' },
  [CASE_STATUS.INTERVIEW_COMPLETED]: { label: '面试完成', type: '' },
  [CASE_STATUS.OFFER_PENDING]: { label: '待Offer', type: 'warning' },
  [CASE_STATUS.OFFER_ACCEPTED]: { label: '已接受Offer', type: 'success' },
  [CASE_STATUS.ONBOARDED]: { label: '已入职', type: 'success' },
  [CASE_STATUS.REJECTED]: { label: '已拒绝', type: 'danger' },
  [CASE_STATUS.WITHDRAWN]: { label: '已撤回', type: 'danger' },
}

// Status options for dropdown
const statusOptions = Object.entries(statusMap).map(([value, { label }]) => ({
  value: Number(value),
  label,
}))

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="case-list">
    <!-- Search form -->
    <div class="page-card search-form">
      <el-form :model="searchParams" inline>
        <el-form-item label="关键词">
          <el-input
            v-model="searchParams.keyWord"
            placeholder="候选人/职位"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchParams.status" placeholder="全部" clearable>
            <el-option
              v-for="opt in statusOptions"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
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
          <el-button
            v-permission="'rk:case:add'"
            type="primary"
            @click="handleAdd"
          >
            <el-icon><Plus /></el-icon>
            新增
          </el-button>
          <el-button
            v-permission="'rk:case:delete'"
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
        <!-- Status slot -->
        <template #status="{ row }">
          <el-dropdown
            v-permission="'rk:case:updateStatus'"
            trigger="click"
            @command="(cmd: number) => handleUpdateStatus(row, cmd)"
          >
            <el-tag
              :type="statusMap[row.status]?.type as any || 'info'"
              size="small"
              class="status-tag"
            >
              {{ statusMap[row.status]?.label || '未知' }}
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </el-tag>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item
                  v-for="opt in statusOptions"
                  :key="opt.value"
                  :command="opt.value"
                  :disabled="opt.value === row.status"
                >
                  {{ opt.label }}
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>

        <!-- Actions column -->
        <template #actions>
          <el-table-column label="操作" width="180" fixed="right" align="center">
            <template #default="{ row }">
              <el-button
                v-permission="'rk:case:info'"
                type="primary"
                link
                size="small"
                @click="handleView(row)"
              >
                查看
              </el-button>
              <el-button
                v-permission="'rk:case:update'"
                type="primary"
                link
                size="small"
                @click="handleEdit(row)"
              >
                编辑
              </el-button>
              <el-button
                v-permission="'rk:case:delete'"
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
  </div>
</template>

<style lang="scss" scoped>
.case-list {
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

  .status-tag {
    cursor: pointer;
  }
}
</style>
