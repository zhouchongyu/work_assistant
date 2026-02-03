<template>
  <div class="home">
    <h2>欢迎使用工作助手系统</h2>
    <p>面向人力资源招聘场景的智能分析系统</p>
    
    <div class="dashboard">
      <div class="card">
        <h3>📊 招聘概况</h3>
        <p>供应商: 15</p>
        <p>客户: 8</p>
        <p>简历: 125</p>
        <p>需求: 42</p>
      </div>
      
      <div class="card">
        <h3>🤖 AI助手</h3>
        <p>智能分析简历与需求</p>
        <p>自动匹配候选人</p>
        <p>对话式查询系统</p>
      </div>
      
      <div class="card">
        <h3>⚙️ 系统功能</h3>
        <p>用户管理</p>
        <p>权限控制</p>
        <p>数据字典</p>
        <p>任务调度</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
</script>

<style scoped>
.home {
  text-align: center;
  padding: 2rem;
}

.dashboard {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-top: 2rem;
}

.card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  text-align: left;
}

.card h3 {
  margin-top: 0;
  color: #409eff;
}
</style>