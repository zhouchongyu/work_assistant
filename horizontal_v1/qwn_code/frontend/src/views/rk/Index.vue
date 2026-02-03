<template>
  <div class="rk-index">
    <h2>招聘管理</h2>
    <div class="content">
      <p>供应商、客户、简历、需求管理</p>
      <div class="actions">
        <button @click="goToSupply">简历管理</button>
        <button @click="goToDemand">需求管理</button>
        <button @click="goToVendor">供应商管理</button>
        <button @click="goToCustomer">客户管理</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';

const router = useRouter();

const goToSupply = () => {
  router.push('/rk/supply');
};

const goToDemand = () => {
  router.push('/rk/demand');
};

const goToVendor = () => {
  router.push('/rk/vendor');
};

const goToCustomer = () => {
  router.push('/rk/customer');
};
</script>

<style scoped>
.rk-index {
  padding: 2rem;
}

.actions {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

button {
  padding: 0.5rem 1rem;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>