<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { DocumentTextOutline, SearchOutline, SyncOutline } from '@vicons/ionicons5'
import api from '@/api'
import { formatDate } from '@/utils/format'
import type { PostSummary } from '@/types'

const route = useRoute()
const router = useRouter()

const posts = ref<PostSummary[]>([])
const loading = ref(true)
const error = ref('')

// 搜索关键词存在地址栏里（/?q=xxx），这样能分享链接、能用浏览器后退
const query = computed(() => (typeof route.query.q === 'string' ? route.query.q : ''))
const isSearching = computed(() => query.value !== '')

// 输入框的内容，和地址栏解耦：输入时不立刻跳转，回车才提交
const keyword = ref(query.value)

async function load() {
  loading.value = true
  error.value = ''
  try {
    // 有关键词就走搜索接口，没有就是普通的最新文章列表
    const { data } = isSearching.value
      ? await api.get<PostSummary[]>('/api/search', { params: { q: query.value } })
      : await api.get<PostSummary[]>('/api/posts')
    posts.value = data
  } catch (err: any) {
    error.value = '加载失败: ' + err.message
  } finally {
    loading.value = false
  }
}

function submitSearch() {
  const q = keyword.value.trim()
  router.push({ path: '/', query: q ? { q } : {} })
}

function clearSearch() {
  keyword.value = ''
  router.push({ path: '/' })
}

onMounted(load)
// 前进/后退、或点「返回全部文章」都会改 query，onMounted 不会再触发，得监听
watch(query, (q) => {
  keyword.value = q
  load()
})
</script>

<template>
  <div class="home">
    <div class="search-bar">
      <SearchOutline class="svg-icon" />
      <input
        v-model="keyword"
        type="search"
        placeholder="搜索文章…"
        @keydown.enter="submitSearch"
      />
      <button v-if="keyword" class="clear-btn" @click="clearSearch">清除</button>
    </div>

    <h1 v-if="isSearching">
      <SearchOutline class="svg-icon" />
      搜索「{{ query }}」
      <span v-if="!loading" class="count">{{ posts.length }} 篇</span>
    </h1>
    <h1 v-else>
      <DocumentTextOutline class="svg-icon" />
      最新文章
    </h1>

    <div v-if="loading" class="loading">
      <SyncOutline class="svg-icon spin" />
      加载中...
    </div>
    <div v-else-if="error" class="error">{{ error }}</div>

    <div v-else-if="posts.length === 0" class="empty">
      <template v-if="isSearching">
        <p>没有找到包含「{{ query }}」的文章</p>
        <button class="clear-btn" @click="clearSearch">返回全部文章</button>
      </template>
      <p v-else>
        还没有文章，去 <code>/#/admin</code> 写第一篇吧
      </p>
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
  padding: 28px 0 64px;
}

/* 搜索框 */
.search-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 14px;
  margin-bottom: 28px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 8px;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.search-bar:focus-within {
  border-color: var(--brand);
  box-shadow: 0 0 0 3px var(--brand-soft);
}
.search-bar .svg-icon {
  color: var(--text-muted);
}
.search-bar input {
  flex: 1;
  min-width: 0;
  font: inherit;
  padding: 10px 0;
  border: none;
  outline: none;
  background: none;
  color: inherit;
}
.search-bar input::placeholder {
  color: #a8a8a8;
}
/* Chrome 会给 type=search 塞一个默认的清除按钮，和我们自己的重复了 */
.search-bar input::-webkit-search-cancel-button {
  appearance: none;
}

.clear-btn {
  flex-shrink: 0;
  font: inherit;
  font-size: 0.85rem;
  padding: 2px 12px;
  border: 1px solid var(--border);
  border-radius: 20px;
  background: none;
  color: var(--text-muted);
  cursor: pointer;
  white-space: nowrap;
  transition: border-color 0.2s, color 0.2s;
}
.clear-btn:hover {
  border-color: var(--brand);
  color: var(--brand);
}

h1 {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1.5rem;
  margin: 0 0 28px;
}
.count {
  font-size: 0.9rem;
  font-weight: normal;
  color: var(--text-muted);
}

.posts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 18px;
}
.post-card {
  display: flex;
  flex-direction: column;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 22px;
  text-decoration: none;
  color: inherit;
  transition: box-shadow 0.2s, transform 0.2s, border-color 0.2s;
}
.post-card:hover {
  border-color: rgba(66, 184, 131, 0.5);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.09);
  transform: translateY(-2px);
}
.post-card h2 {
  font-size: 1.12rem;
  line-height: 1.45;
  margin: 0 0 6px;
}
.date {
  color: var(--text-muted);
  font-size: 0.82rem;
  margin: 0 0 12px;
}
.summary {
  color: var(--text-muted);
  font-size: 0.9rem;
  line-height: 1.65;
  margin: 0 0 16px;
  /* 摘要最多两行，卡片高度才整齐 */
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: auto; /* 标签贴到卡片底部，同一行的卡片标签能对齐 */
}
.tag {
  background: var(--brand-soft);
  color: var(--brand);
  font-size: 0.78rem;
  padding: 2px 10px;
  border-radius: 20px;
}

.empty {
  color: var(--text-muted);
}
.empty p {
  margin: 0 0 14px;
}
.empty code {
  background: #f4f4f6;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.9em;
}
.error {
  color: var(--danger);
}
</style>
