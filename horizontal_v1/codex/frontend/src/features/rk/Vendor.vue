<template>
  <div class="page">
    <el-card>
      <template #header>新增供应商</template>
      <el-form :model="form" label-width="80px" class="form">
        <el-form-item label="名称">
          <el-input v-model="form.name" placeholder="供应商名称" />
        </el-form-item>
        <el-form-item label="编码">
          <el-input v-model="form.code" placeholder="编码/编号" />
        </el-form-item>
        <el-button type="primary" :loading="loading" @click="onSubmit">创建</el-button>
      </el-form>
      <el-alert
        v-if="lastCreated"
        type="success"
        show-icon
        :closable="false"
        title="创建成功"
        :description="`ID: ${lastCreated.id}，名称：${lastCreated.name}`"
        class="mt-2"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { addVendor, type VendorOut } from '@/service/api/rk_vendor'

const form = reactive({ name: '', code: '' })
const loading = ref(false)
const lastCreated = ref<VendorOut | null>(null)

const onSubmit = async () => {
  if (!form.name || !form.code) {
    ElMessage.warning('请填写名称和编码')
    return
  }
  loading.value = true
  try {
    lastCreated.value = await addVendor({ name: form.name, code: form.code })
    ElMessage.success('创建成功')
  } catch (e: any) {
    ElMessage.error(e.message || '创建失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.page {
  padding: 8px;
}
.form {
  max-width: 460px;
}
.mt-2 {
  margin-top: 12px;
}
</style>
