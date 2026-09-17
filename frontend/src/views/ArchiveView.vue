<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import api from '@/api'
import { formatDate, formatMonth } from '@/utils/format'
import type { PostSummary } from '@/types'

const posts = ref<PostSummary[]>([])
const loading = ref(true)
const error = ref('')

// 后端已按时间倒序返回，Map 保持插入顺序，所以分组天然是新的月份在前
const groups = computed(() => {
  const map = new Map<string, PostSummary[]>()
  for (const post of posts.value) {
    const key = post.created_at.slice(0, 7)
    const list = map.get(key) ?? []
    list.push(post)
    map.set(key, list)
  }
  return [...map.entries()].map(([key, list]) => ({
    key,
    label: formatMonth(key),
    posts: list,
  }))
})

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
  <div class="archive">
    <h1>📅 归档</h1>

    <div v-if="loading">⏳ 加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="groups.length === 0" class="empty">还没有文章</div>

    <div v-else class="timeline">
      <p class="total">共 {{ posts.length }} 篇</p>
      <section v-for="group in groups" :key="group.key" class="month">
        <h2>{{ group.label }}（{{ group.posts.length }} 篇）</h2>
        <ul>
          <li v-for="post in group.posts" :key="post.id">
            <span class="date">{{ formatDate(post.created_at) }}</span>
            <router-link :to="`/post/${post.id}`">{{ post.title }}</router-link>
          </li>
        </ul>
      </section>
    </div>
  </div>
</template>

<style scoped>
.archive {
  padding: 20px 0;
}
h1 {
  font-size: 1.6rem;
  margin: 0 0 8px;
}
.total {
  color: #999;
  font-size: 0.9rem;
  margin: 0 0 24px;
}
.timeline {
  border-left: 2px solid #e5e4e7;
  padding-left: 24px;
}
.month h2 {
  font-size: 1.05rem;
  color: #42b883;
  margin: 0 0 10px;
}
.month + .month h2 {
  margin-top: 32px;
}
.month ul {
  list-style: none;
  padding: 0;
  margin: 0;
}
.month li {
  display: flex;
  gap: 16px;
  align-items: baseline;
  padding: 6px 0;
}
.date {
  color: #999;
  font-size: 0.85rem;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}
.month a {
  text-decoration: none;
}
.month a:hover {
  text-decoration: underline;
}
.empty {
  color: #666;
}
.error {
  color: #e74c3c;
}
</style>
