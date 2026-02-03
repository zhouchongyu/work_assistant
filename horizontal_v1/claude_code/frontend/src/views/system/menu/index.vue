<script setup lang="ts">
/**
 * System Menu management page.
 */
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { menuApi, type SysMenu, type MenuListParams } from '@/api/system/menu'

// State
const loading = ref(false)
const tableData = ref<SysMenu[]>([])
const expandAll = ref(true)
const searchParams = reactive<MenuListParams>({
  keyWord: '',
})

// Dialog state
const dialogVisible = ref(false)
const dialogTitle = ref('')
const formData = reactive<Partial<SysMenu>>({})
const formRef = ref()

// Load data
async function loadData() {
  loading.value = true
  try {
    const data = await menuApi.getList(searchParams)
    tableData.value = data || []
  } catch (e) {
    console.error('Failed to load menu list:', e)
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
  dialogTitle.value = '新增菜单'
  Object.assign(formData, {
    id: undefined,
    parentId: undefined,
    name: '',
    router: '',
    perms: '',
    type: 1,
    icon: '',
    orderNum: 0,
    viewPath: '',
    keepAlive: true,
    isShow: true,
  })
  dialogVisible.value = true
}

// Add child
function handleAddChild(row: SysMenu) {
  dialogTitle.value = '新增子菜单'
  Object.assign(formData, {
    id: undefined,
    parentId: row.id,
    name: '',
    router: '',
    perms: '',
    type: 1,
    icon: '',
    orderNum: 0,
    viewPath: '',
    keepAlive: true,
    isShow: true,
  })
  dialogVisible.value = true
}

// Edit
function handleEdit(row: SysMenu) {
  dialogTitle.value = '编辑菜单'
  Object.assign(formData, { ...row })
  dialogVisible.value = true
}

// Save
async function handleSave() {
  try {
    await formRef.value?.validate()
    if (formData.id) {
      await menuApi.update(formData as SysMenu)
      ElMessage.success('更新成功')
    } else {
      await menuApi.create(formData)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (e) {
    // Validation failed or API error
  }
}

// Delete
async function handleDelete(row: SysMenu) {
  try {
    await ElMessageBox.confirm(
      '确定要删除该菜单吗？',
      '提示',
      { type: 'warning' }
    )
    await menuApi.delete(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    // User cancelled
  }
}

// Form rules
const formRules = {
  name: [{ required: true, message: '请输入菜单名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择类型', trigger: 'change' }],
}

// Menu type options
const menuTypes = [
  { label: '目录', value: 0 },
  { label: '菜单', value: 1 },
  { label: '权限', value: 2 },
]

// Flatten menus for parent select
function flattenMenus(list: SysMenu[], level = 0): Array<SysMenu & { level: number }> {
  const result: Array<SysMenu & { level: number }> = []
  for (const item of list) {
    result.push({ ...item, level })
    if (item.children?.length) {
      result.push(...flattenMenus(item.children, level + 1))
    }
  }
  return result
}

const flatMenus = computed(() => flattenMenus(tableData.value))

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="menu-list">
    <!-- Search form -->
    <div class="page-card search-form">
      <el-form :model="searchParams" inline>
        <el-form-item label="关键词">
          <el-input
            v-model="searchParams.keyWord"
            placeholder="菜单名称"
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
            v-permission="'base:sys:menu:add'"
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
        <el-table-column prop="name" label="菜单名称" min-width="200" />
        <el-table-column prop="icon" label="图标" width="80" align="center">
          <template #default="{ row }">
            <el-icon v-if="row.icon"><component :is="row.icon" /></el-icon>
          </template>
        </el-table-column>
        <el-table-column prop="type" label="类型" width="80" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.type === 0" type="warning" size="small">目录</el-tag>
            <el-tag v-else-if="row.type === 1" size="small">菜单</el-tag>
            <el-tag v-else type="info" size="small">权限</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="router" label="路由" min-width="150" />
        <el-table-column prop="perms" label="权限标识" min-width="150" />
        <el-table-column prop="orderNum" label="排序" width="80" align="center" />
        <el-table-column prop="isShow" label="显示" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.isShow ? 'success' : 'info'" size="small">
              {{ row.isShow ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right" align="center">
          <template #default="{ row }">
            <el-button
              v-if="row.type !== 2"
              v-permission="'base:sys:menu:add'"
              type="success"
              link
              size="small"
              @click="handleAddChild(row)"
            >
              添加
            </el-button>
            <el-button
              v-permission="'base:sys:menu:update'"
              type="primary"
              link
              size="small"
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            <el-button
              v-permission="'base:sys:menu:delete'"
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
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px">
        <el-form-item label="上级菜单" prop="parentId">
          <el-select v-model="formData.parentId" placeholder="无（顶级菜单）" clearable>
            <el-option
              v-for="menu in flatMenus"
              :key="menu.id"
              :label="'　'.repeat(menu.level) + menu.name"
              :value="menu.id"
              :disabled="menu.id === formData.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="类型" prop="type">
          <el-radio-group v-model="formData.type">
            <el-radio v-for="t in menuTypes" :key="t.value" :value="t.value">
              {{ t.label }}
            </el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入菜单名称" />
        </el-form-item>
        <el-form-item v-if="formData.type !== 2" label="图标" prop="icon">
          <el-input v-model="formData.icon" placeholder="请输入图标名称" />
        </el-form-item>
        <el-form-item v-if="formData.type !== 2" label="路由" prop="router">
          <el-input v-model="formData.router" placeholder="请输入路由地址" />
        </el-form-item>
        <el-form-item v-if="formData.type === 2" label="权限标识" prop="perms">
          <el-input v-model="formData.perms" placeholder="如：base:sys:user:add" />
        </el-form-item>
        <el-form-item v-if="formData.type === 1" label="视图路径" prop="viewPath">
          <el-input v-model="formData.viewPath" placeholder="如：views/system/user/index" />
        </el-form-item>
        <el-form-item label="排序" prop="orderNum">
          <el-input-number v-model="formData.orderNum" :min="0" />
        </el-form-item>
        <el-form-item v-if="formData.type !== 2" label="显示" prop="isShow">
          <el-switch v-model="formData.isShow" />
        </el-form-item>
        <el-form-item v-if="formData.type === 1" label="缓存" prop="keepAlive">
          <el-switch v-model="formData.keepAlive" />
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
.menu-list {
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
