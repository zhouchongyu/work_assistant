<template>
  <div id="app">
    <header class="header">
      <h1>Work Assistant - 人力资源招聘智能分析系统</h1>
      <nav class="nav">
        <router-link to="/">首页</router-link>
        <router-link to="/rk">招聘管理</router-link>
        <router-link to="/chat">AI助手</router-link>
        <router-link v-if="!isLoggedIn" to="/login">登录</router-link>
        <a v-else @click="logout">退出</a>
      </nav>
    </header>
    
    <main class="main">
      <router-view />
    </main>
    
    <footer class="footer">
      <p>&copy; 2026 Work Assistant. All rights reserved.</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const isLoggedIn = ref(false);

onMounted(() => {
  // 检查登录状态
  const token = localStorage.getItem('access_token');
  isLoggedIn.value = !!token;
});

const logout = () => {
  localStorage.removeItem('access_token');
  isLoggedIn.value = false;
  router.push('/login');
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background-color: #409eff;
  color: white;
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav a {
  color: white;
  text-decoration: none;
  margin-right: 1rem;
  cursor: pointer;
}

.main {
  flex: 1;
  padding: 2rem;
}

.footer {
  background-color: #f5f5f5;
  text-align: center;
  padding: 1rem;
  margin-top: auto;
}
</style>