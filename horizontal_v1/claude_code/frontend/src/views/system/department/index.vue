<script setup lang="ts">
/**
 * System Department management page.
 */
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { departmentApi, type SysDepartment, type DepartmentListParams } from '@/api/system/department'

// State
const loading = ref(false)
const tableData = ref<SysDepartment[]>([])
const expandAll = ref(true)
const searchParams = reactive<DepartmentListParams>({
  keyWord: '',
})

// Dialog state
const dialogVisible = ref(false)
const dialogTitle = ref('')
const formData = reactive<Partial<SysDepartment>>({})
const formRef = ref()

// Load data
async function loadData() {
  loading.value = true
  try {
    const data = await departmentApi.getList(searchParams)
    tableData.value = data || []
  } catch (e) {
    console.error('Failed to load department list:', e)
  } finally {
    loading.value = false
  }
}

// Search
function handleSearch() {
  loadData()
}

// Reset search
function handleReset() {
  searchParams.keyWord = ''
  handleSearch()
}

// Add new (top level)
function handleAdd() {
  dialogTitle.value = '新增部门'
  Object.assign(formData, {
    id: undefined,
    parentId: undefined,
    name: '',
    orderNum: 0,
  })
  dialogVisible.value = true
}

// Add child
function handleAddChild(row: SysDepartment) {
  dialogTitle.value = '新增子部门'
  Object.assign(formData, {
    id: undefined,
    parentId: row.id,
    name: '',
    orderNum: 0,
  })
  dialogVisible.value = true
}

// Edit
function handleEdit(row: SysDepartment) {
  dialogTitle.value = '编辑部门'
  Object.assign(formData, { ...row })
  dialogVisible.value = true
}

// Save
async function handleSave() {
  try {
    await formRef.value?.validate()
    if (formData.id) {
      await departmentApi.update(formData as SysDepartment)
      ElMessage.success('更新成功')
    } else {
      await departmentApi.create(formData)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (e) {
    // Validation failed or API error
  }
}

// Delete
async function handleDelete(row: SysDepartment) {
  try {
    await ElMessageBox.confirm(
      '确定要删除该部门吗？',
      '提示',
      { type: 'warning' }
    )
    await departmentApi.delete(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    // User cancelled
  }
}

// Form rules
const formRules = {
  name: [{ required: true, message: '请输入部门名称', trigger: 'blur' }],
}

// Flatten departments for parent select
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

const flatDepartments = computed(() => flattenDepartments(tableData.value))

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="department-list">
    <!-- Search form -->
    <div class="page-card search-form">
      <el-form :model="searchParams" inline>
        <el-form-item label="关键词">
          <el-input
            v-model="searchParams.keyWord"
            placeholder="部门名称"
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
            v-permission="'base:sys:department:add'"
            type="primary"
            @click="handleAdd"
          >
            <el-icon><Plus /></el-icon>
            新增
          </el-button>
          <el-button @click="expandAll = !expandAll">
            {{ expandAll ? '收起' : '展开' }}
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
      <el-table
        v-loading="loading"
        :data="tableData"
        row-key="id"
        :default-expand-all="expandAll"
        border
      >
        <el-table-column prop="name" label="部门名称" min-width="200" />
        <el-table-column prop="orderNum" label="排序" width="100" align="center" />
        <el-table-column prop="createTime" label="创建时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right" align="center">
          <template #default="{ row }">
            <el-button
              v-permission="'base:sys:department:add'"
              type="success"
              link
              size="small"
              @click="handleAddChild(row)"
            >
              添加
            </el-button>
            <el-button
              v-permission="'base:sys:department:update'"
              type="primary"
              link
              size="small"
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            <el-button
              v-permission="'base:sys:department:delete'"
              type="danger"
              link
              size="small"
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- Add/Edit Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="80px">
        <el-form-item label="上级部门" prop="parentId">
          <el-select v-model="formData.parentId" placeholder="无（顶级部门）" clearable>
            <el-option
              v-for="dept in flatDepartments"
              :key="dept.id"
              :label="'　'.repeat(dept.level) + dept.name"
              :value="dept.id"
              :disabled="dept.id === formData.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入部门名称" />
        </el-form-item>
        <el-form-item label="排序" prop="orderNum">
          <el-input-number v-model="formData.orderNum" :min="0" />
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
.department-list {
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
