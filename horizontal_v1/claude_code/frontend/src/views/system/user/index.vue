<script setup lang="ts">
/**
 * System User management page.
 */
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import CrudTable from '@/components/crud/CrudTable.vue'
import type { Column, Pagination } from '@/components/crud/CrudTable.vue'
import { userApi, type SysUser, type UserListParams } from '@/api/system/user'
import { roleApi, type SysRole } from '@/api/system/role'
import { departmentApi, type SysDepartment } from '@/api/system/department'

// Table columns
const columns: Column[] = [
  { prop: 'id', label: 'ID', width: 80 },
  { prop: 'username', label: '用户名', width: 120 },
  { prop: 'nickName', label: '昵称', width: 120 },
  { prop: 'departmentName', label: '部门', width: 120 },
  { prop: 'email', label: '邮箱', minWidth: 180 },
  { prop: 'phone', label: '手机号', width: 130 },
  { prop: 'status', label: '状态', width: 100, slot: 'status' },
  { prop: 'createTime', label: '创建时间', width: 180 },
]

// State
const loading = ref(false)
const tableData = ref<SysUser[]>([])
const selectedRows = ref<SysUser[]>([])
const pagination = reactive<Pagination>({
  page: 1,
  size: 20,
  total: 0,
})
const searchParams = reactive<UserListParams>({
  keyWord: '',
  status: undefined,
  departmentId: undefined,
})

// Dialog state
const dialogVisible = ref(false)
const dialogTitle = ref('')
const formData = reactive<Partial<SysUser> & { password?: string }>({})
const formRef = ref()

// Roles and departments for select
const roles = ref<SysRole[]>([])
const departments = ref<SysDepartment[]>([])

// Load data
async function loadData() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      size: pagination.size,
      ...searchParams,
    }
    const { list, pagination: pager } = await userApi.getList(params)
    tableData.value = list || []
    pagination.total = pager?.total || 0
  } catch (e) {
    console.error('Failed to load user list:', e)
  } finally {
    loading.value = false
  }
}

// Load roles and departments
async function loadOptions() {
  try {
    const [roleList, deptList] = await Promise.all([
      roleApi.getAll(),
      departmentApi.getList(),
    ])
    roles.value = roleList || []
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
  searchParams.status = undefined
  searchParams.departmentId = undefined
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
function handleSelectionChange(rows: SysUser[]) {
  selectedRows.value = rows
}

// Add new
function handleAdd() {
  dialogTitle.value = '新增用户'
  Object.assign(formData, {
    id: undefined,
    username: '',
    nickName: '',
    password: '',
    email: '',
    phone: '',
    status: 1,
    departmentId: undefined,
    roleIds: [],
    remark: '',
  })
  dialogVisible.value = true
}

// Edit
async function handleEdit(row: SysUser) {
  dialogTitle.value = '编辑用户'
  try {
    const detail = await userApi.getDetail(row.id)
    Object.assign(formData, { ...detail, password: '' })
    dialogVisible.value = true
  } catch (e) {
    console.error('Failed to load user detail:', e)
  }
}

// Save
async function handleSave() {
  try {
    await formRef.value?.validate()
    if (formData.id) {
      // Update - don't send password if empty
      const data = { ...formData }
      if (!data.password) {
        delete data.password
      }
      await userApi.update(data as SysUser)
      ElMessage.success('更新成功')
    } else {
      // Create - password required
      if (!formData.password) {
        ElMessage.warning('请输入密码')
        return
      }
      await userApi.create(formData as SysUser & { password: string })
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (e) {
    // Validation failed or API error
  }
}

// Delete
async function handleDelete(row?: SysUser) {
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
    await userApi.delete(ids)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    // User cancelled
  }
}

// Reset password
async function handleResetPassword(row: SysUser) {
  try {
    const { value } = await ElMessageBox.prompt('请输入新密码', '重置密码', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPattern: /^.{6,}$/,
      inputErrorMessage: '密码长度不能少于6位',
    })
    await userApi.resetPassword(row.id, value)
    ElMessage.success('密码重置成功')
  } catch (e) {
    // User cancelled
  }
}

// Toggle status
async function handleToggleStatus(row: SysUser) {
  const newStatus = row.status === 1 ? 0 : 1
  try {
    await userApi.updateStatus(row.id, newStatus)
    row.status = newStatus
    ElMessage.success('状态更新成功')
  } catch (e) {
    console.error('Failed to update status:', e)
  }
}

// Form rules
const formRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  nickName: [{ required: true, message: '请输入昵称', trigger: 'blur' }],
}

// Flatten department tree for select
function flattenDepartments(list: SysDepartment[], level = 0): Array<SysDepartment & { level: number }> {
  const result: Array<SysDepartment & { level: number }> = []
  for (const item of list) {
    result.push({ ...item, level })
    if (item.children?.length) {
      result.push(...flattenDepartments(item.children, level + 1))
    }
  }
  return result
}

onMounted(() => {
  loadData()
  loadOptions()
})
</script>

<template>
  <div class="user-list">
    <!-- Search form -->
    <div class="page-card search-form">
      <el-form :model="searchParams" inline>
        <el-form-item label="关键词">
          <el-input
            v-model="searchParams.keyWord"
            placeholder="用户名/昵称/手机号"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchParams.status" placeholder="全部" clearable>
            <el-option label="启用" :value="1" />
            <el-option label="禁用" :value="0" />
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
            v-permission="'base:sys:user:add'"
            type="primary"
            @click="handleAdd"
          >
            <el-icon><Plus /></el-icon>
            新增
          </el-button>
          <el-button
            v-permission="'base:sys:user:delete'"
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
          <el-switch
            v-permission="'base:sys:user:update'"
            :model-value="row.status === 1"
            @change="handleToggleStatus(row)"
          />
        </template>

        <!-- Actions column -->
        <template #actions>
          <el-table-column label="操作" width="200" fixed="right" align="center">
            <template #default="{ row }">
              <el-button
                v-permission="'base:sys:user:update'"
                type="primary"
                link
                size="small"
                @click="handleEdit(row)"
              >
                编辑
              </el-button>
              <el-button
                v-permission="'base:sys:user:update'"
                type="warning"
                link
                size="small"
                @click="handleResetPassword(row)"
              >
                重置密码
              </el-button>
              <el-button
                v-permission="'base:sys:user:delete'"
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
        <el-form-item label="用户名" prop="username">
          <el-input v-model="formData.username" placeholder="请输入用户名" :disabled="!!formData.id" />
        </el-form-item>
        <el-form-item label="昵称" prop="nickName">
          <el-input v-model="formData.nickName" placeholder="请输入昵称" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="formData.password"
            type="password"
            :placeholder="formData.id ? '留空则不修改' : '请输入密码'"
            show-password
          />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="formData.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="formData.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="部门" prop="departmentId">
          <el-select v-model="formData.departmentId" placeholder="请选择部门" clearable>
            <el-option
              v-for="dept in flattenDepartments(departments)"
              :key="dept.id"
              :label="'　'.repeat(dept.level) + dept.name"
              :value="dept.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="角色" prop="roleIds">
          <el-select v-model="formData.roleIds" multiple placeholder="请选择角色">
            <el-option
              v-for="role in roles"
              :key="role.id"
              :label="role.name"
              :value="role.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="formData.status">
            <el-radio :value="1">启用</el-radio>
            <el-radio :value="0">禁用</el-radio>
          </el-radio-group>
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
.user-list {
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
