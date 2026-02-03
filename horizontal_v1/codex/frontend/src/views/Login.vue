<template>
  <div class="login">
    <el-card class="login-card">
      <h2>登录</h2>
      <el-form :model="form" @submit.prevent="onSubmit">
        <el-form-item label="用户名">
          <el-input v-model="form.username" autocomplete="username" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input type="password" v-model="form.password" autocomplete="current-password" />
        </el-form-item>
        <el-form-item label="验证码">
          <div class="captcha-row">
            <el-input v-model="form.verifyCode" autocomplete="one-time-code" maxlength="4" />
            <img :src="captcha?.data" alt="captcha" class="captcha" @click="loadCaptcha" />
          </div>
        </el-form-item>
        <el-button type="primary" class="w-full" :loading="loading" @click="onSubmit">登录</el-button>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { login, fetchCaptcha, fetchMe } from '@/service/api/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const auth = useAuthStore()
const form = reactive({ username: '', password: '', verifyCode: '' })
const captcha = ref<{ captchaId: string; data: string } | null>(null)
const loading = ref(false)

const loadCaptcha = async () => {
  try {
    captcha.value = await fetchCaptcha()
  } catch (e: any) {
    ElMessage.error(e.message || '获取验证码失败')
  }
}

onMounted(() => {
  loadCaptcha()
})

const onSubmit = async () => {
  if (loading.value) return
  try {
    loading.value = true
    if (!captcha.value) {
      await loadCaptcha()
    }
    const tokenPair = await login({
      username: form.username,
      password: form.password,
      captchaId: captcha.value?.captchaId || '',
      verifyCode: form.verifyCode,
    })
    auth.setToken(tokenPair.token, tokenPair.refreshToken, tokenPair.expire)
    const profile = await fetchMe()
    auth.setUser({
      id: profile.id,
      username: profile.username,
      name: profile.name,
      nickName: profile.nickName,
    })
    router.push('/')
  } catch (e: any) {
    ElMessage.error(e.message || '登录失败')
    await loadCaptcha()
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login {
  display: grid;
  place-items: center;
  min-height: 100vh;
  background: #f5f7fa;
}
.login-card {
  width: 360px;
}
.w-full {
  width: 100%;
}
.captcha-row {
  display: flex;
  gap: 12px;
  align-items: center;
}
.captcha {
  height: 40px;
  cursor: pointer;
  border-radius: 4px;
  border: 1px solid #e5e7eb;
}
</style>
