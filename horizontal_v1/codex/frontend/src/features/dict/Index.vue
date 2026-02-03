<template>
  <div class="page">
    <div class="columns">
      <div class="card">
        <div class="card-header">
          <strong>字典类型</strong>
          <el-input v-model="typeQuery.keyWord" placeholder="搜索名称" clearable size="small" @change="loadTypes" />
        </div>
        <el-table :data="typeRows" v-loading="loadingTypes" @row-click="onSelectType" highlight-current-row>
          <el-table-column prop="id" label="ID" width="70" />
          <el-table-column prop="name" label="名称" />
          <el-table-column prop="key" label="Key" />
          <el-table-column prop="page" label="页面" width="120" />
        </el-table>
        <div class="pagination">
          <el-pagination
            layout="prev, pager, next, jumper, ->, total"
            :page-size="typeQuery.size"
            :current-page="typeQuery.page"
            :total="typeTotal"
            @current-change="(p:number)=>{typeQuery.page=p;loadTypes();}"
          />
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <strong>字典数据</strong>
          <div class="actions">
            <el-input
              v-model="infoQuery.keyWord"
              placeholder="搜索名称"
              clearable
              size="small"
              @change="loadInfos"
            />
            <el-button type="primary" size="small" :loading="loadingInfos" @click="loadInfos">刷新</el-button>
          </div>
        </div>
        <el-alert
          v-if="!infoQuery.typeId"
          title="请选择左侧字典类型后再查看数据"
          type="info"
          show-icon
          :closable="false"
          class="mb-2"
        />
        <el-table :data="infoRows" v-loading="loadingInfos" border stripe>
          <el-table-column prop="id" label="ID" width="70" />
          <el-table-column prop="name" label="名称" />
          <el-table-column prop="value" label="值" />
          <el-table-column prop="orderNum" label="排序" width="90" />
          <el-table-column prop="isShow" label="展示" width="80">
            <template #default="{ row }">
              <el-tag :type="row.isShow ? 'success' : 'info'">{{ row.isShow ? '是' : '否' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="isProcess" label="处理" width="80">
            <template #default="{ row }">
              <el-tag :type="row.isProcess ? 'success' : 'info'">{{ row.isProcess ? '是' : '否' }}</el-tag>
            </template>
          </el-table-column>
        </el-table>
        <div class="pagination">
          <el-pagination
            layout="prev, pager, next, jumper, ->, total"
            :page-size="infoQuery.size"
            :current-page="infoQuery.page"
            :total="infoTotal"
            @current-change="(p:number)=>{infoQuery.page=p;loadInfos();}"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { fetchDictInfos, fetchDictTypes, type DictInfoItem, type DictTypeItem } from '@/service/api/dict'

const loadingTypes = ref(false)
const loadingInfos = ref(false)
const typeRows = ref<DictTypeItem[]>([])
const infoRows = ref<DictInfoItem[]>([])
const typeTotal = ref(0)
const infoTotal = ref(0)
const typeQuery = reactive({ page: 1, size: 10, keyWord: '' })
const infoQuery = reactive<{ page: number; size: number; keyWord: string; typeId?: number }>({
  page: 1,
  size: 10,
  keyWord: '',
  typeId: undefined,
})

const loadTypes = async () => {
  loadingTypes.value = true
  try {
    const res = await fetchDictTypes({ ...typeQuery })
    typeRows.value = res.list
    typeTotal.value = res.pagination.total
  } catch (e: any) {
    ElMessage.error(e.message || '加载字典类型失败')
  } finally {
    loadingTypes.value = false
  }
}

const loadInfos = async () => {
  if (!infoQuery.typeId) return
  loadingInfos.value = true
  try {
    const res = await fetchDictInfos({ ...infoQuery })
    infoRows.value = res.list
    infoTotal.value = res.pagination.total
  } catch (e: any) {
    ElMessage.error(e.message || '加载字典数据失败')
  } finally {
    loadingInfos.value = false
  }
}

const onSelectType = (row: DictTypeItem) => {
  infoQuery.typeId = row.id
  infoQuery.page = 1
  infoQuery.keyWord = ''
  loadInfos()
}

onMounted(() => {
  loadTypes()
})
</script>

<style scoped>
.page {
  padding: 8px;
}
.columns {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 12px;
}
.card {
  background: #fff;
  border-radius: 8px;
  padding: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  min-height: 400px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}
.pagination {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
}
.actions {
  display: flex;
  gap: 8px;
  align-items: center;
}
.mb-2 {
  margin-bottom: 8px;
}
</style>
