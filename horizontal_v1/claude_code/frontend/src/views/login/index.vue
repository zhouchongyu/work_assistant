<script setup lang="ts">
/**
 * Login page.
 *
 * Features:
 * - Username/password login
 * - Captcha verification
 * - Remember me
 */
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { http } from '@/api/request'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// Form state
const formRef = ref()
const loading = ref(false)
const form = reactive({
  username: '',
  password: '',
  verifyCode: '',
  captchaId: '',
})

// Captcha
const captchaImg = ref('')
const captchaLoading = ref(false)

// Validation rules
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' },
  ],
  verifyCode: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
  ],
}

// Load captcha on mount
onMounted(() => {
  refreshCaptcha()
})

// Refresh captcha
async function refreshCaptcha() {
  captchaLoading.value = true
  try {
    const data = await http.get('/v1/open/captcha', {
      width: 120,
      height: 40,
      type: 'text',
    })
    captchaImg.value = data.data
    form.captchaId = data.id
  } catch (e) {
    console.error('Failed to load captcha:', e)
  } finally {
    captchaLoading.value = false
  }
}

// Handle login
async function handleLogin() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await userStore.login(
      form.username,
      form.password,
      form.captchaId,
      form.verifyCode
    )

    ElMessage.success('登录成功')

    // Redirect to previous page or home
    const redirect = route.query.redirect as string
    router.push(redirect || '/')
  } catch (e: any) {
    // Refresh captcha on error
    refreshCaptcha()
    form.verifyCode = ''
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h1 class="login-title">Work Assistant</h1>
        <p class="login-subtitle">工作助手管理系统</p>
      </div>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        class="login-form"
        @keyup.enter="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="用户名"
            prefix-icon="User"
            size="large"
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            prefix-icon="Lock"
            size="large"
            show-password
          />
        </el-form-item>

        <el-form-item prop="verifyCode">
          <div class="captcha-row">
            <el-input
              v-model="form.verifyCode"
              placeholder="验证码"
              prefix-icon="Key"
              size="large"
              class="captcha-input"
            />
            <div class="captcha-img" @click="refreshCaptcha">
              <el-image
                v-if="captchaImg"
                :src="captchaImg"
                fit="contain"
                :loading="captchaLoading ? 'lazy' : 'eager'"
              />
              <el-skeleton v-else :loading="captchaLoading" animated>
                <template #template>
                  <el-skeleton-item variant="image" style="width: 120px; height: 40px" />
                </template>
              </el-skeleton>
            </div>
          </div>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            class="login-btn"
            @click="handleLogin"
          >
            登 录
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.login-container {
  width: 100%;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 420px;
  padding: 40px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.login-header {
  text-align: center;
  margin-bottom: 40px;

  .login-title {
    font-size: 28px;
    font-weight: 600;
    color: #303133;
    margin-bottom: 8px;
  }

  .login-subtitle {
    font-size: 14px;
    color: #909399;
  }
}

.login-form {
  .captcha-row {
    display: flex;
    gap: 10px;

    .captcha-input {
      flex: 1;
    }

    .captcha-img {
      width: 120px;
      height: 40px;
      cursor: pointer;
      border: 1px solid #dcdfe6;
      border-radius: 4px;
      overflow: hidden;

      :deep(.el-image) {
        width: 100%;
        height: 100%;
      }
    }
  }

  .login-btn {
    width: 100%;
  }
}
</style>
