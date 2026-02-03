<script setup lang="ts">
/**
 * Dictionary management page.
 */
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import CrudTable from '@/components/crud/CrudTable.vue'
import type { Column, Pagination } from '@/components/crud/CrudTable.vue'
import { dictApi, type DictType, type DictInfo } from '@/api/dict'

// === Dict Type State ===
const typeLoading = ref(false)
const typeData = ref<DictType[]>([])
const selectedType = ref<DictType | null>(null)
const typePagination = reactive({
  page: 1,
  size: 20,
  total: 0,
})
const typeSearchKeyword = ref('')

// === Dict Info State ===
const infoLoading = ref(false)
const infoData = ref<DictInfo[]>([])
const infoPagination = reactive({
  page: 1,
  size: 20,
  total: 0,
})

// Dialog state
const typeDialogVisible = ref(false)
const typeDialogTitle = ref('')
const typeFormData = reactive<Partial<DictType>>({})
const typeFormRef = ref()

const infoDialogVisible = ref(false)
const infoDialogTitle = ref('')
const infoFormData = reactive<Partial<DictInfo>>({})
const infoFormRef = ref()

// Table columns for info
const infoColumns: Column[] = [
  { prop: 'id', label: 'ID', width: 80 },
  { prop: 'name', label: '名称', minWidth: 150 },
  { prop: 'value', label: '值', minWidth: 150 },
  { prop: 'orderNum', label: '排序', width: 80 },
  { prop: 'remark', label: '备注', minWidth: 150 },
]

// === Type Methods ===
async function loadTypes() {
  typeLoading.value = true
  try {
    const params = {
      page: typePagination.page,
      size: typePagination.size,
      keyWord: typeSearchKeyword.value,
    }
    const { list, pagination } = await dictApi.getTypes(params)
    typeData.value = list || []
    typePagination.total = pagination?.total || 0
  } catch (e) {
    console.error('Failed to load dict types:', e)
  } finally {
    typeLoading.value = false
  }
}

function handleTypeSearch() {
  typePagination.page = 1
  loadTypes()
}

function handleTypeSelect(row: DictType) {
  selectedType.value = row
  infoPagination.page = 1
  loadInfos()
}

function handleAddType() {
  typeDialogTitle.value = '新增字典类型'
  Object.assign(typeFormData, {
    id: undefined,
    name: '',
    key: '',
    remark: '',
  })
  typeDialogVisible.value = true
}

function handleEditType(row: DictType) {
  typeDialogTitle.value = '编辑字典类型'
  Object.assign(typeFormData, { ...row })
  typeDialogVisible.value = true
}

async function handleSaveType() {
  try {
    await typeFormRef.value?.validate()
    if (typeFormData.id) {
      await dictApi.updateType(typeFormData as DictType)
      ElMessage.success('更新成功')
    } else {
      await dictApi.createType(typeFormData)
      ElMessage.success('创建成功')
    }
    typeDialogVisible.value = false
    loadTypes()
  } catch (e) {
    // Validation failed or API error
  }
}

async function handleDeleteType(row: DictType) {
  try {
    await ElMessageBox.confirm(
      '确定要删除该字典类型吗？相关字典项也会被删除！',
      '提示',
      { type: 'warning' }
    )
    await dictApi.deleteType(row.id)
    ElMessage.success('删除成功')
    if (selectedType.value?.id === row.id) {
      selectedType.value = null
      infoData.value = []
    }
    loadTypes()
  } catch (e) {
    // User cancelled
  }
}

// === Info Methods ===
async function loadInfos() {
  if (!selectedType.value) {
    infoData.value = []
    return
  }
  infoLoading.value = true
  try {
    const params = {
      page: infoPagination.page,
      size: infoPagination.size,
      typeId: selectedType.value.id,
    }
    const { list, pagination } = await dictApi.getInfoList(params)
    infoData.value = list || []
    infoPagination.total = pagination?.total || 0
  } catch (e) {
    console.error('Failed to load dict infos:', e)
  } finally {
    infoLoading.value = false
  }
}

function handleInfoPageChange(page: number) {
  infoPagination.page = page
  loadInfos()
}

function handleInfoSizeChange(size: number) {
  infoPagination.size = size
  infoPagination.page = 1
  loadInfos()
}

function handleAddInfo() {
  if (!selectedType.value) {
    ElMessage.warning('请先选择字典类型')
    return
  }
  infoDialogTitle.value = '新增字典项'
  Object.assign(infoFormData, {
    id: undefined,
    typeId: selectedType.value.id,
    name: '',
    value: '',
    orderNum: 0,
    remark: '',
  })
  infoDialogVisible.value = true
}

function handleEditInfo(row: DictInfo) {
  infoDialogTitle.value = '编辑字典项'
  Object.assign(infoFormData, { ...row })
  infoDialogVisible.value = true
}

async function handleSaveInfo() {
  try {
    await infoFormRef.value?.validate()
    if (infoFormData.id) {
      await dictApi.updateInfo(infoFormData as DictInfo)
      ElMessage.success('更新成功')
    } else {
      await dictApi.createInfo(infoFormData)
      ElMessage.success('创建成功')
    }
    infoDialogVisible.value = false
    loadInfos()
  } catch (e) {
    // Validation failed or API error
  }
}

async function handleDeleteInfo(row: DictInfo) {
  try {
    await ElMessageBox.confirm(
      '确定要删除该字典项吗？',
      '提示',
      { type: 'warning' }
    )
    await dictApi.deleteInfo(row.id)
    ElMessage.success('删除成功')
    loadInfos()
  } catch (e) {
    // User cancelled
  }
}

// Form rules
const typeFormRules = {
  name: [{ required: true, message: '请输入类型名称', trigger: 'blur' }],
  key: [{ required: true, message: '请输入类型标识', trigger: 'blur' }],
}

const infoFormRules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  value: [{ required: true, message: '请输入值', trigger: 'blur' }],
}

onMounted(() => {
  loadTypes()
})
</script>

<template>
  <div class="dict-list">
    <el-row :gutter="16">
      <!-- Left: Dict Types -->
      <el-col :span="8">
        <div class="page-card">
          <div class="card-header">
            <span class="title">字典类型</span>
            <el-button
              v-permission="'dict:type:add'"
              type="primary"
              size="small"
              @click="handleAddType"
            >
              <el-icon><Plus /></el-icon>
              新增
            </el-button>
          </div>

          <el-input
            v-model="typeSearchKeyword"
            placeholder="搜索类型名称"
            clearable
            class="search-input"
            @keyup.enter="handleTypeSearch"
          >
            <template #append>
              <el-button @click="handleTypeSearch">
                <el-icon><Search /></el-icon>
              </el-button>
            </template>
          </el-input>

          <el-table
            v-loading="typeLoading"
            :data="typeData"
            highlight-current-row
            style="width: 100%"
            @current-change="handleTypeSelect"
          >
            <el-table-column prop="name" label="名称" min-width="100" />
            <el-table-column prop="key" label="标识" min-width="100" />
            <el-table-column label="操作" width="100" align="center">
              <template #default="{ row }">
                <el-button
                  v-permission="'dict:type:update'"
                  type="primary"
                  link
                  size="small"
                  @click.stop="handleEditType(row)"
                >
                  编辑
                </el-button>
                <el-button
                  v-permission="'dict:type:delete'"
                  type="danger"
                  link
                  size="small"
                  @click.stop="handleDeleteType(row)"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-col>

      <!-- Right: Dict Items -->
      <el-col :span="16">
        <div class="page-card">
          <div class="card-header">
            <span class="title">
              字典项
              <template v-if="selectedType">
                - {{ selectedType.name }}（{{ selectedType.key }}）
              </template>
            </span>
            <el-button
              v-permission="'dict:info:add'"
              type="primary"
              size="small"
              :disabled="!selectedType"
              @click="handleAddInfo"
            >
              <el-icon><Plus /></el-icon>
              新增
            </el-button>
          </div>

          <CrudTable
            :data="infoData"
            :columns="infoColumns"
            :loading="infoLoading"
            :pagination="infoPagination"
            @page-change="handleInfoPageChange"
            @size-change="handleInfoSizeChange"
          >
            <template #actions>
              <el-table-column label="操作" width="120" fixed="right" align="center">
                <template #default="{ row }">
                  <el-button
                    v-permission="'dict:info:update'"
                    type="primary"
                    link
                    size="small"
                    @click="handleEditInfo(row)"
                  >
                    编辑
                  </el-button>
                  <el-button
                    v-permission="'dict:info:delete'"
                    type="danger"
                    link
                    size="small"
                    @click="handleDeleteInfo(row)"
                  >
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </template>
          </CrudTable>
        </div>
      </el-col>
    </el-row>

    <!-- Type Dialog -->
    <el-dialog v-model="typeDialogVisible" :title="typeDialogTitle" width="500px">
      <el-form ref="typeFormRef" :model="typeFormData" :rules="typeFormRules" label-width="80px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="typeFormData.name" placeholder="请输入类型名称" />
        </el-form-item>
        <el-form-item label="标识" prop="key">
          <el-input v-model="typeFormData.key" placeholder="请输入类型标识（如：gender）" />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="typeFormData.remark" type="textarea" :rows="3" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="typeDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveType">确定</el-button>
      </template>
    </el-dialog>

    <!-- Info Dialog -->
    <el-dialog v-model="infoDialogVisible" :title="infoDialogTitle" width="500px">
      <el-form ref="infoFormRef" :model="infoFormData" :rules="infoFormRules" label-width="80px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="infoFormData.name" placeholder="请输入名称" />
        </el-form-item>
        <el-form-item label="值" prop="value">
          <el-input v-model="infoFormData.value" placeholder="请输入值" />
        </el-form-item>
        <el-form-item label="排序" prop="orderNum">
          <el-input-number v-model="infoFormData.orderNum" :min="0" />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="infoFormData.remark" type="textarea" :rows="3" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="infoDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveInfo">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style lang="scss" scoped>
.dict-list {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;

    .title {
      font-size: 16px;
      font-weight: 500;
    }
  }

  .search-input {
    margin-bottom: 16px;
  }
}
</style>
