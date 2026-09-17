<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { marked } from 'marked'
import api from '@/api'
import { formatDate } from '@/utils/format'
import type { PostDetail } from '@/types'

const route = useRoute()

const post = ref<PostDetail | null>(null)
const loading = ref(true)
const error = ref('')

// async: false 让 marked.parse 的返回类型确定为 string，而不是 string | Promise<string>
const html = computed(() =>
  post.value ? marked.parse(post.value.content, { async: false }) : '',
)

onMounted(async () => {
  try {
    const { data } = await api.get<PostDetail>(`/api/posts/${route.params.id}`)
    post.value = data
  } catch (err: any) {
    error.value = '加载失败: ' + err.message
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="post">
    <div v-if="loading">⏳ 加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>

    <article v-else-if="post">
      <h1>{{ post.title }}</h1>
      <p class="meta">
        {{ formatDate(post.created_at) }}
        <span v-if="post.updated_at !== post.created_at">
          （更新于 {{ formatDate(post.updated_at) }}）
        </span>
      </p>

      <div class="markdown-body" v-html="html"></div>

      <div v-if="post.tags.length" class="tags">
        <router-link
          v-for="tag in post.tags"
          :key="tag"
          :to="{ path: '/tags', query: { tag } }"
          class="tag"
        >
          {{ tag }}
        </router-link>
      </div>

      <router-link to="/" class="back">← 返回列表</router-link>
    </article>
  </div>
</template>

<style scoped>
.post {
  padding: 20px 0;
}
h1 {
  font-size: 1.8rem;
  margin: 0 0 8px;
}
.meta {
  color: #999;
  font-size: 0.85rem;
  margin: 0 0 28px;
}
.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 32px;
  padding-top: 20px;
  border-top: 1px solid #e5e4e7;
}
.tag {
  background: rgba(66, 184, 131, 0.12);
  color: #42b883;
  font-size: 0.8rem;
  padding: 3px 12px;
  border-radius: 20px;
  text-decoration: none;
}
.tag:hover {
  background: rgba(66, 184, 131, 0.24);
}
.back {
  display: inline-block;
  margin-top: 24px;
  text-decoration: none;
}
.error {
  color: #e74c3c;
}
</style>
