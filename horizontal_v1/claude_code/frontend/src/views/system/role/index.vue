<script setup lang="ts">
/**
 * System Role management page.
 */
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import CrudTable from '@/components/crud/CrudTable.vue'
import type { Column, Pagination } from '@/components/crud/CrudTable.vue'
import { roleApi, type SysRole, type RoleListParams } from '@/api/system/role'
import { menuApi, type SysMenu } from '@/api/system/menu'
import { departmentApi, type SysDepartment } from '@/api/system/department'

// Table columns
const columns: Column[] = [
  { prop: 'id', label: 'ID', width: 80 },
  { prop: 'name', label: '角色名称', minWidth: 150 },
  { prop: 'label', label: '标识', width: 150 },
  { prop: 'remark', label: '备注', minWidth: 200 },
  { prop: 'createTime', label: '创建时间', width: 180 },
]

// State
const loading = ref(false)
const tableData = ref<SysRole[]>([])
const selectedRows = ref<SysRole[]>([])
const pagination = reactive<Pagination>({
  page: 1,
  size: 20,
  total: 0,
})
const searchParams = reactive<RoleListParams>({
  keyWord: '',
})

// Dialog state
const dialogVisible = ref(false)
const dialogTitle = ref('')
const formData = reactive<Partial<SysRole>>({})
const formRef = ref()

// Menus and departments for permission
const menus = ref<SysMenu[]>([])
const departments = ref<SysDepartment[]>([])
const menuTreeRef = ref()
const deptTreeRef = ref()

// Load data
async function loadData() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      size: pagination.size,
      ...searchParams,
    }
    const { list, pagination: pager } = await roleApi.getList(params)
    tableData.value = list || []
    pagination.total = pager?.total || 0
  } catch (e) {
    console.error('Failed to load role list:', e)
  } finally {
    loading.value = false
  }
}

// Load menus and departments
async function loadOptions() {
  try {
    const [menuList, deptList] = await Promise.all([
      menuApi.getList(),
      departmentApi.getList(),
    ])
    menus.value = menuList || []
    departments.value = deptList || []
  } catch (e) {
    console.error('Failed to load options:', e)
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
function handleSelectionChange(rows: SysRole[]) {
  selectedRows.value = rows
}

// Add new
function handleAdd() {
  dialogTitle.value = '新增角色'
  Object.assign(formData, {
    id: undefined,
    name: '',
    label: '',
    remark: '',
    menuIds: [],
    departmentIds: [],
  })
  dialogVisible.value = true
}

// Edit
async function handleEdit(row: SysRole) {
  dialogTitle.value = '编辑角色'
  try {
    const detail = await roleApi.getDetail(row.id)
    Object.assign(formData, detail)
    dialogVisible.value = true
    // Set tree checked after dialog opened
    setTimeout(() => {
      menuTreeRef.value?.setCheckedKeys(formData.menuIds || [])
      deptTreeRef.value?.setCheckedKeys(formData.departmentIds || [])
    }, 100)
  } catch (e) {
    console.error('Failed to load role detail:', e)
  }
}

// Save
async function handleSave() {
  try {
    await formRef.value?.validate()
    // Get checked keys from trees
    const menuIds = menuTreeRef.value?.getCheckedKeys(false) || []
    const departmentIds = deptTreeRef.value?.getCheckedKeys(false) || []

    const data = {
      ...formData,
      menuIds,
      departmentIds,
    }

    if (formData.id) {
      await roleApi.update(data as SysRole)
      ElMessage.success('更新成功')
    } else {
      await roleApi.create(data)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (e) {
    // Validation failed or API error
  }
}

// Delete
async function handleDelete(row?: SysRole) {
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
    await roleApi.delete(ids)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    // User cancelled
  }
}

// Form rules
const formRules = {
  name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }],
  label: [{ required: true, message: '请输入角色标识', trigger: 'blur' }],
}

// Tree props
const treeProps = {
  children: 'children',
  label: 'name',
}

onMounted(() => {
  loadData()
  loadOptions()
})
</script>

<template>
  <div class="role-list">
    <!-- Search form -->
    <div class="page-card search-form">
      <el-form :model="searchParams" inline>
        <el-form-item label="关键词">
          <el-input
            v-model="searchParams.keyWord"
            placeholder="角色名称"
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
            v-permission="'base:sys:role:add'"
            type="primary"
            @click="handleAdd"
          >
            <el-icon><Plus /></el-icon>
            新增
          </el-button>
          <el-button
            v-permission="'base:sys:role:delete'"
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
          <el-table-column label="操作" width="150" fixed="right" align="center">
            <template #default="{ row }">
              <el-button
                v-permission="'base:sys:role:update'"
                type="primary"
                link
                size="small"
                @click="handleEdit(row)"
              >
                编辑
              </el-button>
              <el-button
                v-permission="'base:sys:role:delete'"
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
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="800px">
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="80px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="名称" prop="name">
              <el-input v-model="formData.name" placeholder="请输入角色名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="标识" prop="label">
              <el-input v-model="formData.label" placeholder="请输入角色标识" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="formData.remark" type="textarea" :rows="2" placeholder="请输入备注" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="菜单权限">
              <div class="tree-wrapper">
                <el-tree
                  ref="menuTreeRef"
                  :data="menus"
                  :props="treeProps"
                  show-checkbox
                  node-key="id"
                  default-expand-all
                />
              </div>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="数据权限">
              <div class="tree-wrapper">
                <el-tree
                  ref="deptTreeRef"
                  :data="departments"
                  :props="treeProps"
                  show-checkbox
                  node-key="id"
                  default-expand-all
                />
              </div>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style lang="scss" scoped>
.role-list {
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

  .tree-wrapper {
    max-height: 300px;
    overflow-y: auto;
    border: 1px solid #dcdfe6;
    border-radius: 4px;
    padding: 8px;
  }
}
</style>
