<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/api'

const message = ref('')
const loading = ref(true)

onMounted(async () => {
  try {
    const { data } = await api.get('/api/hello')
    message.value = data.message
  } catch (err: any) {
    message.value = '⚠️ 无法连接后端，请确认服务已启动'
    console.error(err.message)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="home">
    <div class="card">
      <h1>🚀 全栈项目启动成功</h1>
      <p v-if="loading">⏳ 连接中...</p>
      <p v-else class="message">{{ message }}</p>
    </div>
  </div>
</template>

<style scoped>
.home {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
}
.card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
  padding: 40px 60px;
  text-align: center;
}
.message {
  color: #42b883;
  font-size: 1.2rem;
  margin-top: 12px;
}
</style>
