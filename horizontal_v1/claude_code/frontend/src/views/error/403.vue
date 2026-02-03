<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

function goBack() {
  router.back()
}

function goHome() {
  router.push('/')
}
</script>

<template>
  <div class="error-page">
    <div class="error-content">
      <h1 class="error-code">403</h1>
      <p class="error-message">抱歉，您没有权限访问此页面</p>
      <div class="error-actions">
        <el-button @click="goBack">返回上页</el-button>
        <el-button type="primary" @click="goHome">返回首页</el-button>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.error-page {
  width: 100%;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
}

.error-content {
  text-align: center;

  .error-code {
    font-size: 120px;
    font-weight: 700;
    color: #909399;
    line-height: 1;
    margin-bottom: 20px;
  }

  .error-message {
    font-size: 18px;
    color: #606266;
    margin-bottom: 40px;
  }

  .error-actions {
    .el-button {
      margin: 0 10px;
    }
  }
}
</style>
