<template>
  <div class="page">
    <el-card>
      <template #header>客户联系人</template>
      <div class="toolbar">
        <el-input-number v-model="customerId" :min="1" placeholder="客户ID" />
        <el-button type="primary" :loading="loading" @click="load">加载</el-button>
      </div>
      <el-table :data="rows" v-loading="loading" border stripe>
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="name" label="姓名" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="phone" label="电话" />
        <el-table-column prop="default" label="默认" width="90">
          <template #default="{ row }">
            <el-tag :type="row.default ? 'success' : 'info'">{{ row.default ? '是' : '否' }}</el-tag>
          </template>
        </el-table-column>
      </el-table>

      <el-divider />
      <el-form :model="form" label-width="90px" class="form">
        <el-form-item label="客户ID">
          <el-input-number v-model="form.customerId" :min="1" />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item label="默认联系人">
          <el-switch v-model="form.default" />
        </el-form-item>
        <el-button type="primary" :loading="saving" @click="save">新增联系人</el-button>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { addCustomerContact, listCustomerContacts, type CustomerContact } from '@/service/api/rk_customer'

const customerId = ref<number | null>(null)
const rows = ref<CustomerContact[]>([])
const loading = ref(false)
const saving = ref(false)
const form = reactive({ customerId: null as number | null, name: '', email: '', phone: '', default: false })

const load = async () => {
  if (!customerId.value) {
    ElMessage.warning('请输入客户ID')
    return
  }
  loading.value = true
  try {
    rows.value = await listCustomerContacts(customerId.value)
  } catch (e: any) {
    ElMessage.error(e.message || '加载联系人失败')
  } finally {
    loading.value = false
  }
}

const save = async () => {
  if (!form.customerId || !form.name) {
    ElMessage.warning('请填写客户ID和姓名')
    return
  }
  saving.value = true
  try {
    await addCustomerContact({
      customerId: form.customerId,
      name: form.name,
      email: form.email,
      phone: form.phone,
      default: form.default,
    })
    ElMessage.success('新增成功')
    customerId.value = form.customerId
    load()
  } catch (e: any) {
    ElMessage.error(e.message || '保存失败')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.page {
  padding: 8px;
}
.toolbar {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 12px;
}
.form {
  max-width: 520px;
}
</style>
