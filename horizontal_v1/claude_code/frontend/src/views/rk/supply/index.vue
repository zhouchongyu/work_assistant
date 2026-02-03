<script setup lang="ts">
/**
 * Supply (Resume) management page.
 */
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import CrudTable from '@/components/crud/CrudTable.vue'
import type { Column, Pagination } from '@/components/crud/CrudTable.vue'
import { supplyApi, type Supply, type SupplyListParams } from '@/api/rk/supply'
import { usePermission } from '@/composables/usePermission'

const router = useRouter()
const { hasPermission } = usePermission()

// Table columns
const columns: Column[] = [
  { prop: 'id', label: 'ID', width: 80 },
  { prop: 'name', label: '姓名', minWidth: 100 },
  { prop: 'gender', label: '性别', width: 80 },
  { prop: 'phone', label: '手机号', minWidth: 120 },
  { prop: 'workYears', label: '工作年限', width: 100 },
  { prop: 'japaneseLevel', label: '日语等级', width: 100 },
  { prop: 'englishLevel', label: '英语等级', width: 100 },
  { prop: 'status', label: '状态', width: 100, slot: 'status' },
  { prop: 'createTime', label: '创建时间', width: 180 },
]

// State
const loading = ref(false)
const tableData = ref<Supply[]>([])
const selectedRows = ref<Supply[]>([])
const pagination = reactive<Pagination>({
  page: 1,
  size: 20,
  total: 0,
})
const searchParams = reactive<SupplyListParams>({
  keyWord: '',
  status: undefined,
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
    const { list, pagination: pager } = await supplyApi.getList(params)
    tableData.value = list || []
    pagination.total = pager?.total || 0
  } catch (e) {
    console.error('Failed to load supply list:', e)
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
function handleSelectionChange(rows: Supply[]) {
  selectedRows.value = rows
}

// Add new
function handleAdd() {
  router.push('/rk/supply/add')
}

// Edit
function handleEdit(row: Supply) {
  router.push(`/rk/supply/edit/${row.id}`)
}

// View detail
function handleView(row: Supply) {
  router.push(`/rk/supply/detail/${row.id}`)
}

// Delete
async function handleDelete(row?: Supply) {
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
    await supplyApi.delete(ids)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    // User cancelled
  }
}

// Extract resume
async function handleExtract(row: Supply) {
  try {
    await supplyApi.extract(row.id)
    ElMessage.success('已提交简历解析')
  } catch (e) {
    console.error('Failed to extract:', e)
  }
}

// Status map
const statusMap: Record<number, { label: string; type: string }> = {
  0: { label: '待解析', type: 'info' },
  1: { label: '解析中', type: 'warning' },
  2: { label: '已解析', type: 'success' },
  3: { label: '解析失败', type: 'danger' },
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="supply-list">
    <!-- Search form -->
    <div class="page-card search-form">
      <el-form :model="searchParams" inline>
        <el-form-item label="关键词">
          <el-input
            v-model="searchParams.keyWord"
            placeholder="姓名/手机号"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchParams.status" placeholder="全部" clearable>
            <el-option label="待解析" :value="0" />
            <el-option label="解析中" :value="1" />
            <el-option label="已解析" :value="2" />
            <el-option label="解析失败" :value="3" />
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
            v-permission="'rk:supply:add'"
            type="primary"
            @click="handleAdd"
          >
            <el-icon><Plus /></el-icon>
            新增
          </el-button>
          <el-button
            v-permission="'rk:supply:delete'"
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
          <el-tag :type="statusMap[row.status]?.type as any || 'info'" size="small">
            {{ statusMap[row.status]?.label || '未知' }}
          </el-tag>
        </template>

        <!-- Actions column -->
        <template #actions>
          <el-table-column label="操作" width="200" fixed="right" align="center">
            <template #default="{ row }">
              <el-button
                v-permission="'rk:supply:info'"
                type="primary"
                link
                size="small"
                @click="handleView(row)"
              >
                查看
              </el-button>
              <el-button
                v-permission="'rk:supply:update'"
                type="primary"
                link
                size="small"
                @click="handleEdit(row)"
              >
                编辑
              </el-button>
              <el-button
                v-permission="'rk:supply:extract'"
                type="warning"
                link
                size="small"
                @click="handleExtract(row)"
              >
                解析
              </el-button>
              <el-button
                v-permission="'rk:supply:delete'"
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
.supply-list {
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
}
</style>
