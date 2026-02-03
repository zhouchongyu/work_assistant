<template>
  <div class="login">
    <div class="login-form">
      <h2>登录</h2>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label>手机号:</label>
          <input v-model="phone" type="text" placeholder="请输入手机号" required />
        </div>
        <div class="form-group">
          <label>密码:</label>
          <input v-model="password" type="password" placeholder="请输入密码" required />
        </div>
        <button type="submit" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '@/api/http';

const router = useRouter();
const phone = ref('admin');
const password = ref('admin123');
const loading = ref(false);

const handleLogin = async () => {
  loading.value = true;
  
  try {
    const response = await apiClient.post('/auth/login', {
      phone: phone.value,
      password: password.value
    });
    
    if (response.code === 1000) {
      // 存储token
      localStorage.setItem('access_token', response.result.accessToken);
      localStorage.setItem('refresh_token', response.result.refreshToken);
      
      // 跳转到首页
      router.push('/');
    } else {
      alert(response.message || '登录失败');
    }
  } catch (error) {
    console.error('Login error:', error);
    alert('登录失败，请检查用户名和密码');
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f5f5;
}

.login-form {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  width: 400px;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
}

.form-group input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  box-sizing: border-box;
}

button {
  width: 100%;
  padding: 0.75rem;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>