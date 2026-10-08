<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { SyncOutline } from '@vicons/ionicons5'
import { marked } from '@/utils/markdown'
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
    <div v-if="loading" class="loading">
      <SyncOutline class="svg-icon spin" />
      加载中...
    </div>
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
  /* 版心收窄。列表页可以宽，但读文章时一行 60 多个字很累 ——
     这是这次排版调整里读者感知最强的一项 */
  max-width: var(--reading-width);
  margin: 0 auto;
  padding: 24px 0 72px;
}
h1 {
  font-size: 1.7rem;
  line-height: 1.4;
  margin: 0 0 10px;
}
.meta {
  color: var(--text-muted);
  font-size: 0.85rem;
  margin: 0 0 34px;
}
.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 44px;
  padding-top: 20px;
  border-top: 1px solid var(--border);
}
.tag {
  background: var(--brand-soft);
  color: var(--brand);
  font-size: 0.8rem;
  padding: 3px 12px;
  border-radius: 20px;
  text-decoration: none;
  transition: background 0.2s;
}
.tag:hover {
  background: rgba(66, 184, 131, 0.24);
}
.back {
  display: inline-block;
  margin-top: 28px;
  text-decoration: none;
}
.back:hover {
  text-decoration: underline;
}
.error {
  color: var(--danger);
}
</style>
