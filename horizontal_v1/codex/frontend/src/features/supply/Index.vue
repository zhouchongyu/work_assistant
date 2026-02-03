<template>
  <div class="page">
    <el-card class="mb">
      <template #header>上传简历到 SharePoint</template>
      <div class="flex">
        <el-input-number v-model="uploadForm.vendorId" :min="1" placeholder="供应商ID" />
        <el-upload
          :http-request="onUpload"
          :show-file-list="false"
          accept=".pdf,.doc,.docx,.txt"
          :limit="1"
        >
          <el-button type="primary" :loading="uploading">选择文件并上传</el-button>
        </el-upload>
      </div>
      <el-alert
        v-if="uploadResult"
        type="success"
        show-icon
        :closable="false"
        class="mt"
        :title="`上传成功，Supply ID: ${uploadResult.supplyId}`"
        :description="uploadResult.url"
      />
    </el-card>

    <el-card class="mb">
      <template #header>需求文本分析</template>
      <el-form :model="demandForm" label-width="120px" class="form">
        <el-form-item label="Demand ID">
          <el-input-number v-model="demandForm.demandId" :min="1" />
        </el-form-item>
        <el-form-item label="版本号">
          <el-input-number v-model="demandForm.version" :min="1" />
        </el-form-item>
        <el-form-item label="需求文本">
          <el-input type="textarea" v-model="demandForm.demandTxt" :rows="4" />
        </el-form-item>
        <el-button type="primary" :loading="demandLoading" @click="submitDemand">提交分析</el-button>
      </el-form>
    </el-card>

    <el-card class="mb">
      <template #header>Match Start</template>
      <el-form :model="matchForm" label-width="120px" class="form">
        <el-form-item label="Demand ID">
          <el-input-number v-model="matchForm.demandId" :min="1" />
        </el-form-item>
        <el-form-item label="Supply IDs（逗号分隔）">
          <el-input v-model="matchForm.supplyIdsText" placeholder="如 1,2,3" />
        </el-form-item>
        <el-button type="primary" :loading="matchLoading" @click="submitMatch">开始匹配</el-button>
      </el-form>
    </el-card>

    <el-card>
      <template #header>Case 状态变更</template>
      <el-form :model="caseForm" label-width="120px" class="form">
        <el-form-item label="Case ID">
          <el-input-number v-model="caseForm.caseId" :min="1" />
        </el-form-item>
        <el-form-item label="当前状态">
          <el-input v-model="caseForm.beforeStatus" />
        </el-form-item>
        <el-form-item label="目标状态">
          <el-input v-model="caseForm.afterStatus" />
        </el-form-item>
        <div class="actions">
          <el-button @click="checkCase" :loading="caseLoading">校验可变更</el-button>
          <el-button type="primary" @click="changeCase" :loading="caseLoading">执行变更</el-button>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/store/auth'
import {
  uploadSupply,
  updateDemandTxt,
  matchStart,
  caseChangeStatusCheck,
  caseChangeStatus,
  type UploadResponse,
} from '@/service/api/supply'

const auth = useAuthStore()

const uploadForm = reactive({ vendorId: null as number | null })
const uploading = ref(false)
const uploadResult = ref<UploadResponse | null>(null)

const onUpload = async (options: any) => {
  if (!uploadForm.vendorId) {
    ElMessage.warning('请填写供应商ID')
    return
  }
  const file: File = options.file
  const form = new FormData()
  form.append('file', file)
  form.append('vendor_id', String(uploadForm.vendorId))
  form.append('user_id', String(auth.user?.id || 0))
  uploading.value = true
  try {
    uploadResult.value = await uploadSupply(form)
    ElMessage.success('上传成功，已触发解析')
    options.onSuccess?.(uploadResult.value, file)
  } catch (e: any) {
    ElMessage.error(e.message || '上传失败')
    options.onError?.(e)
  } finally {
    uploading.value = false
  }
}

const demandForm = reactive({ demandId: null as number | null, demandTxt: '', version: 1 })
const demandLoading = ref(false)
const submitDemand = async () => {
  if (!demandForm.demandId || !demandForm.demandTxt) {
    ElMessage.warning('请填写需求ID和文本')
    return
  }
  demandLoading.value = true
  try {
    await updateDemandTxt({
      demandId: demandForm.demandId,
      demandTxt: demandForm.demandTxt,
      version: demandForm.version,
    })
    ElMessage.success('已提交分析')
  } catch (e: any) {
    ElMessage.error(e.message || '提交失败')
  } finally {
    demandLoading.value = false
  }
}

const matchForm = reactive({ demandId: null as number | null, supplyIdsText: '' })
const matchLoading = ref(false)
const submitMatch = async () => {
  if (!matchForm.demandId || !matchForm.supplyIdsText.trim()) {
    ElMessage.warning('请填写 Demand ID 和 Supply ID 列表')
    return
  }
  const supplyIds = matchForm.supplyIdsText
    .split(',')
    .map((s) => Number(s.trim()))
    .filter((n) => !!n)
  matchLoading.value = true
  try {
    await matchStart({
      demandId: matchForm.demandId,
      supplyIds,
      roleList: [],
      flagData: [],
    })
    ElMessage.success('已提交匹配任务')
  } catch (e: any) {
    ElMessage.error(e.message || '提交失败')
  } finally {
    matchLoading.value = false
  }
}

const caseForm = reactive({ caseId: null as number | null, beforeStatus: '', afterStatus: '' })
const caseLoading = ref(false)
const checkCase = async () => {
  if (!caseForm.beforeStatus || !caseForm.afterStatus) {
    ElMessage.warning('请填写状态')
    return
  }
  caseLoading.value = true
  try {
    await caseChangeStatusCheck({
      caseId: caseForm.caseId,
      beforeStatus: caseForm.beforeStatus,
      afterStatus: caseForm.afterStatus,
    })
    ElMessage.success('校验通过')
  } catch (e: any) {
    ElMessage.error(e.message || '校验失败')
  } finally {
    caseLoading.value = false
  }
}

const changeCase = async () => {
  if (!caseForm.caseId || !caseForm.beforeStatus || !caseForm.afterStatus) {
    ElMessage.warning('请填写 Case ID 与状态')
    return
  }
  caseLoading.value = true
  try {
    await caseChangeStatus({
      caseId: caseForm.caseId,
      beforeStatus: caseForm.beforeStatus,
      afterStatus: caseForm.afterStatus,
      userId: auth.user?.id,
    })
    ElMessage.success('状态变更已提交')
  } catch (e: any) {
    ElMessage.error(e.message || '变更失败')
  } finally {
    caseLoading.value = false
  }
}
</script>

<style scoped>
.page {
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.flex {
  display: flex;
  gap: 12px;
  align-items: center;
}
.form {
  max-width: 640px;
}
.mb {
  margin-bottom: 12px;
}
.mt {
  margin-top: 12px;
}
.actions {
  display: flex;
  gap: 12px;
}
</style>
