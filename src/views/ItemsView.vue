<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/api'

interface Item {
  id: number
  name: string
  price: number
  description: string
}

const items = ref<Item[]>([])
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const { data } = await api.get('/api/items')
    items.value = data
  } catch (err: any) {
    error.value = '加载失败: ' + err.message
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="items-page">
    <h1>📦 物品列表</h1>

    <div v-if="loading">⏳ 加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>

    <div v-else class="items-grid">
      <div v-for="item in items" :key="item.id" class="item-card">
        <h3>{{ item.name }}</h3>
        <p class="price">¥{{ item.price }}</p>
        <p class="desc">{{ item.description }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.items-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}
.items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
}
.item-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 6px rgba(0,0,0,0.08);
  padding: 20px;
}
.price {
  color: #42b883;
  font-size: 1.2rem;
  font-weight: bold;
}
.desc {
  color: #666;
  font-size: 0.9rem;
}
.error {
  color: #e74c3c;
}
</style>
