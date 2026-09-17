<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/api'
import { formatDate } from '@/utils/format'
import type { PostSummary, TagCount } from '@/types'

const route = useRoute()
const router = useRouter()

const tags = ref<TagCount[]>([])
const posts = ref<PostSummary[]>([])
const loading = ref(true)
const error = ref('')

// 不要写成 route.query.tag as string —— LocationQueryValue 到 string 不是合法断言，vue-tsc 会报错
const activeTag = computed(() => (typeof route.query.tag === 'string' ? route.query.tag : ''))

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [tagRes, postRes] = await Promise.all([
      api.get<TagCount[]>('/api/tags'),
      api.get<PostSummary[]>('/api/posts', {
        params: activeTag.value ? { tag: activeTag.value } : {},
      }),
    ])
    tags.value = tagRes.data
    posts.value = postRes.data
  } catch (err: any) {
    error.value = '加载失败: ' + err.message
  } finally {
    loading.value = false
  }
}

function pick(name: string) {
  router.push({ path: '/tags', query: name ? { tag: name } : {} })
}

onMounted(load)
// 点标签是在同一个组件里换 query，onMounted 不会再触发，必须监听
watch(() => route.query.tag, load)
</script>

<template>
  <div class="tags-page">
    <h1>🏷️ 标签</h1>

    <div v-if="loading">⏳ 加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>

    <template v-else>
      <div class="tag-cloud">
        <button class="tag" :class="{ active: !activeTag }" @click="pick('')">
          全部
        </button>
        <button
          v-for="tag in tags"
          :key="tag.name"
          class="tag"
          :class="{ active: activeTag === tag.name }"
          @click="pick(tag.name)"
        >
          {{ tag.name }} <span class="count">{{ tag.count }}</span>
        </button>
      </div>

      <h2 v-if="activeTag">标签「{{ activeTag }}」下的文章（{{ posts.length }} 篇）</h2>
      <h2 v-else>全部文章（{{ posts.length }} 篇）</h2>

      <ul class="post-list">
        <li v-for="post in posts" :key="post.id">
          <router-link :to="`/post/${post.id}`">{{ post.title }}</router-link>
          <span class="date">{{ formatDate(post.created_at) }}</span>
        </li>
      </ul>
    </template>
  </div>
</template>

<style scoped>
.tags-page {
  padding: 20px 0;
}
h1 {
  font-size: 1.6rem;
  margin: 0 0 20px;
}
h2 {
  font-size: 1.05rem;
  font-weight: normal;
  color: #666;
  margin: 28px 0 12px;
}
.tag-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.tag {
  font: inherit;
  font-size: 0.9rem;
  background: #fff;
  color: #333;
  border: 1px solid #e5e4e7;
  border-radius: 20px;
  padding: 4px 14px;
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s, color 0.2s;
}
.tag:hover {
  border-color: #42b883;
}
.tag.active {
  background: #42b883;
  border-color: #42b883;
  color: #fff;
}
.count {
  opacity: 0.65;
  font-size: 0.85em;
}
.post-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.post-list li {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 16px;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
}
.post-list a {
  text-decoration: none;
}
.post-list a:hover {
  text-decoration: underline;
}
.date {
  color: #999;
  font-size: 0.85rem;
  white-space: nowrap;
}
.error {
  color: #e74c3c;
}
</style>
