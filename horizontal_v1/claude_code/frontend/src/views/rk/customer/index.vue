<script setup lang="ts">
/**
 * Customer management page.
 */
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import CrudTable from '@/components/crud/CrudTable.vue'
import type { Column, Pagination } from '@/components/crud/CrudTable.vue'
import { customerApi, type Customer, type CustomerListParams } from '@/api/rk/customer'

const router = useRouter()

// Table columns
const columns: Column[] = [
  { prop: 'id', label: 'ID', width: 80 },
  { prop: 'name', label: '客户名称', minWidth: 180 },
  { prop: 'shortName', label: '简称', width: 120 },
  { prop: 'industry', label: '行业', width: 120 },
  { prop: 'scale', label: '规模', width: 100 },
  { prop: 'address', label: '地址', minWidth: 200 },
  { prop: 'website', label: '网站', minWidth: 150 },
  { prop: 'createTime', label: '创建时间', width: 180 },
]

// State
const loading = ref(false)
const tableData = ref<Customer[]>([])
const selectedRows = ref<Customer[]>([])
const pagination = reactive<Pagination>({
  page: 1,
  size: 20,
  total: 0,
})
const searchParams = reactive<CustomerListParams>({
  keyWord: '',
})

// Dialog state
const dialogVisible = ref(false)
const dialogTitle = ref('')
const formData = reactive<Partial<Customer>>({})
const formRef = ref()

// Load data
async function loadData() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      size: pagination.size,
      ...searchParams,
    }
    const { list, pagination: pager } = await customerApi.getList(params)
    tableData.value = list || []
    pagination.total = pager?.total || 0
  } catch (e) {
    console.error('Failed to load customer list:', e)
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
function handleSelectionChange(rows: Customer[]) {
  selectedRows.value = rows
}

// Add new
function handleAdd() {
  dialogTitle.value = '新增客户'
  Object.assign(formData, {
    id: undefined,
    name: '',
    shortName: '',
    industry: '',
    scale: '',
    address: '',
    website: '',
    remark: '',
  })
  dialogVisible.value = true
}

// Edit
function handleEdit(row: Customer) {
  dialogTitle.value = '编辑客户'
  Object.assign(formData, { ...row })
  dialogVisible.value = true
}

// View detail
function handleView(row: Customer) {
  router.push(`/rk/customer/detail/${row.id}`)
}

// Save
async function handleSave() {
  try {
    await formRef.value?.validate()
    if (formData.id) {
      await customerApi.update(formData as Customer)
      ElMessage.success('更新成功')
    } else {
      await customerApi.create(formData)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (e) {
    // Validation failed or API error
  }
}

// Delete
async function handleDelete(row?: Customer) {
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
    await customerApi.delete(ids)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    // User cancelled
  }
}

// Form rules
const formRules = {
  name: [{ required: true, message: '请输入客户名称', trigger: 'blur' }],
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="customer-list">
    <!-- Search form -->
    <div class="page-card search-form">
      <el-form :model="searchParams" inline>
        <el-form-item label="关键词">
          <el-input
            v-model="searchParams.keyWord"
            placeholder="客户名称/简称"
            clearable
            @keyup.enter="handleSearch"
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
            v-permission="'rk:customer:add'"
            type="primary"
            @click="handleAdd"
          >
            <el-icon><Plus /></el-icon>
            新增
          </el-button>
          <el-button
            v-permission="'rk:customer:delete'"
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
        <!-- Actions column -->
        <template #actions>
          <el-table-column label="操作" width="180" fixed="right" align="center">
            <template #default="{ row }">
              <el-button
                v-permission="'rk:customer:info'"
                type="primary"
                link
                size="small"
                @click="handleView(row)"
              >
                查看
              </el-button>
              <el-button
                v-permission="'rk:customer:update'"
                type="primary"
                link
                size="small"
                @click="handleEdit(row)"
              >
                编辑
              </el-button>
              <el-button
                v-permission="'rk:customer:delete'"
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

    <!-- Add/Edit Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="80px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入客户名称" />
        </el-form-item>
        <el-form-item label="简称" prop="shortName">
          <el-input v-model="formData.shortName" placeholder="请输入简称" />
        </el-form-item>
        <el-form-item label="行业" prop="industry">
          <el-input v-model="formData.industry" placeholder="请输入行业" />
        </el-form-item>
        <el-form-item label="规模" prop="scale">
          <el-input v-model="formData.scale" placeholder="请输入规模" />
        </el-form-item>
        <el-form-item label="地址" prop="address">
          <el-input v-model="formData.address" placeholder="请输入地址" />
        </el-form-item>
        <el-form-item label="网站" prop="website">
          <el-input v-model="formData.website" placeholder="请输入网站" />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="formData.remark" type="textarea" :rows="3" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style lang="scss" scoped>
.customer-list {
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
