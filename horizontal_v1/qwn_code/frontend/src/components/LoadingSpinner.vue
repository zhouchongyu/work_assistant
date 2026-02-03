<!-- frontend/src/components/LoadingSpinner.vue -->
<template>
  <div v-if="loading" class="loading-spinner">
    <div class="spinner"></div>
    <p v-if="message">{{ message }}</p>
  </div>
</template>

<script setup lang="ts">
interface Props {
  loading: boolean;
  message?: string;
}

withDefaults(defineProps<Props>(), {
  loading: false,
  message: '加载中...'
});
</script>

<style scoped>
.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.spinner {
  width: 3rem;
  height: 3rem;
  border: 0.25rem solid rgba(0, 0, 0, 0.1);
  border-top-color: #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>