<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/api'
import { formatDate } from '@/utils/format'
import type { PostSummary } from '@/types'

const posts = ref<PostSummary[]>([])
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const { data } = await api.get<PostSummary[]>('/api/posts')
    posts.value = data
  } catch (err: any) {
    error.value = '加载失败: ' + err.message
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="home">
    <h1>📝 最新文章</h1>

    <div v-if="loading">⏳ 加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="posts.length === 0" class="empty">
      还没有文章，去 <code>/#/admin</code> 写第一篇吧
    </div>

    <div v-else class="posts-grid">
      <router-link
        v-for="post in posts"
        :key="post.id"
        :to="`/post/${post.id}`"
        class="post-card"
      >
        <h2>{{ post.title }}</h2>
        <p class="date">{{ formatDate(post.created_at) }}</p>
        <p class="summary">{{ post.summary || '（没有摘要）' }}</p>
        <div v-if="post.tags.length" class="tags">
          <span v-for="tag in post.tags" :key="tag" class="tag">{{ tag }}</span>
        </div>
      </router-link>
    </div>
  </div>
</template>

<style scoped>
.home {
  padding: 20px 0;
}
h1 {
  font-size: 1.6rem;
  margin: 0 0 24px;
}
.posts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}
.post-card {
  display: block;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.08);
  padding: 20px;
  text-decoration: none;
  color: inherit;
  transition: box-shadow 0.2s, transform 0.2s;
}
.post-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}
.post-card h2 {
  font-size: 1.15rem;
  margin: 0 0 6px;
}
.date {
  color: #999;
  font-size: 0.85rem;
  margin: 0 0 10px;
}
.summary {
  color: #666;
  font-size: 0.9rem;
  margin: 0;
}
.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 14px;
}
.tag {
  background: rgba(66, 184, 131, 0.12);
  color: #42b883;
  font-size: 0.78rem;
  padding: 2px 10px;
  border-radius: 20px;
}
.empty {
  color: #666;
}
.empty code {
  background: #f4f4f6;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.9em;
}
.error {
  color: #e74c3c;
}
</style>
