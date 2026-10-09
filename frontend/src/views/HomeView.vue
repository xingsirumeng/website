<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  AddOutline,
  ChevronDownOutline,
  CreateOutline,
  DocumentTextOutline,
  SearchOutline,
  SyncOutline,
} from '@vicons/ionicons5'
import api from '@/api'
import { useAdmin } from '@/composables/useAdmin'
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

/* ---------- 下面两个只有管理员看得到 ---------- */
const { isAdmin } = useAdmin()

// 用 query 参数让后台直接落到对应界面，省掉「进后台再找文章」两步
function editPost(id: number) {
  router.push({ path: '/admin', query: { edit: String(id) } })
}

function newPost() {
  router.push({ path: '/admin', query: { new: '1' } })
}

/* ---------- 首屏标题的打字机效果 ---------- */
const TITLE = 'xingsirumeng.blog'
const shown = ref(TITLE) // 先给完整标题：JS 没跑起来时也不该是一片空白
const typing = ref(false)
let typeTimer: number | undefined

function typeTitle() {
  // 系统里开了「减少动态效果」就别打字了，直接显示完整标题
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    shown.value = TITLE
    typing.value = false
    return
  }

  window.clearInterval(typeTimer)
  shown.value = ''
  typing.value = true
  let i = 0
  typeTimer = window.setInterval(() => {
    i += 1
    shown.value = TITLE.slice(0, i)
    if (i >= TITLE.length) {
      window.clearInterval(typeTimer)
      typing.value = false
    }
  }, 85)
}

onMounted(() => {
  load()
  typeTitle()
})

// 只清定时器就够了（离开页面时别再继续打字）
onBeforeUnmount(() => {
  window.clearInterval(typeTimer)
})

// 前进/后退、或点「返回全部文章」都会改 query，onMounted 不会再触发，得监听
watch(query, (q) => {
  keyword.value = q
  load()
})
</script>

<template>
  <div class="home">
    <!-- 首屏：整屏高度，中间只有站名，正文被推到折叠线以下。
         搜索时不显示 —— 否则搜索结果会被挤到屏幕外，得滚动才看得到 -->
    <section v-if="!isSearching" class="hero">
      <!-- 用 aria-label 给屏幕阅读器完整标题；动画部分对它是隐藏的，
           否则会被逐字念出来 -->
      <h1 class="hero-title" :aria-label="TITLE">
        <span class="typing-box">
          <!-- 一个看不见的完整标题，负责把宽度撑住 -->
          <span class="ghost" aria-hidden="true">{{ TITLE }}</span>
          <span class="live" aria-hidden="true">{{ shown }}<span v-if="typing" class="caret"></span></span>
        </span>
      </h1>
      <ChevronDownOutline class="svg-icon hero-hint" />
    </section>

    <section class="posts">
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

      <h2 v-if="isSearching">
        <SearchOutline class="svg-icon" />
        搜索「{{ query }}」
        <span v-if="!loading" class="count">{{ posts.length }} 篇</span>
      </h2>
      <h2 v-else>
        <DocumentTextOutline class="svg-icon" />
        最新文章
      </h2>

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
          <!-- 卡片本身是 <router-link>（渲染成 <a>），HTML 不允许链接嵌套，
               所以编辑入口用绝对定位的按钮浮在右上角。
               .prevent 和 .stop 缺一不可 —— 少任何一个都会连带触发卡片的跳转 -->
          <button
            v-if="isAdmin"
            class="card-edit"
            title="编辑这篇"
            @click.prevent.stop="editPost(post.id)"
          >
            <CreateOutline class="svg-icon" />
          </button>

          <h3>{{ post.title }}</h3>
          <p class="date">{{ formatDate(post.created_at) }}</p>
          <p class="summary">{{ post.summary || '（没有摘要）' }}</p>
          <div v-if="post.tags.length" class="tags">
            <span v-for="tag in post.tags" :key="tag" class="tag">{{ tag }}</span>
          </div>
        </router-link>
      </div>
    </section>

    <!-- 右下角悬浮的「写新文章」，只有管理员看得到。
         和「回到顶部」共用 .float-btn 那套样式，只有水平位置不同 -->
    <button v-if="isAdmin" class="float-btn fab" title="写新文章" @click="newPost">
      <AddOutline class="svg-icon" />
    </button>
  </div>
</template>

<style scoped>
.home {
  /* 首屏要贴着导航栏开始，所以上边距交给 .hero 自己撑 */
  padding: 0 0 64px;
}

/* ---------- 首屏 ---------- */
.hero {
  /* 标题字号抽成变量：箭头的上移量要按它来算，
     写死像素的话换个屏幕尺寸两边就对不齐了 */
  --hero-title-size: clamp(1.9rem, 5.5vw, 3.4rem);
  /* 首屏内容整体上移的量。视觉重心略高于正中比死居中更舒服。
     想调就改这个倍数（2 → 3 就再往上挪一个标题的高度） */
  --hero-lift: calc(2 * var(--hero-title-size));

  /* 占满整屏高度，把正文推到折叠线以下 —— 必须滚动才能看到。
     要减掉导航栏：它在文档流里占了顶部一条，不减的话首屏会超出一屏，
     正文的顶边会从折叠线下面露出来一截 */
  min-height: calc(100vh - var(--nav-height));
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  /* 给下面那个绝对定位的箭头做参照 */
  position: relative;
}
.hero-title {
  margin: 0;
  font-size: var(--hero-title-size);
  font-weight: 600;
  letter-spacing: -0.02em;
  color: var(--text-strong);
  /* 底是照片，加一圈暗色光晕把标题从背景里托出来 */
  text-shadow: 0 2px 28px rgba(0, 0, 0, 0.85), 0 1px 4px rgba(0, 0, 0, 0.7);
  /* 从正中往上挪 */
  transform: translateY(calc(-1 * var(--hero-lift)));
}
/* 打字机效果的容器。宽度由里面那个隐藏的完整标题决定 ——
   不这么做的话，标题是居中的，每多一个字整行就重新居中，
   已经出现的字会左右乱跳，看起来是在从中间往两边撑开 */
.typing-box {
  position: relative;
  display: inline-block;
}
.ghost {
  visibility: hidden;
}
.live {
  position: absolute;
  top: 0;
  left: 0;
  white-space: nowrap;
}
/* 打字光标 */
.caret {
  display: inline-block;
  width: 0.055em;
  height: 0.92em;
  margin-left: 0.06em;
  vertical-align: -0.08em;
  background: currentColor;
  animation: caret-blink 1s step-end infinite;
}
@keyframes caret-blink {
  50% {
    opacity: 0;
  }
}
/* 滚动提示。整屏只有一行标题时，访客很容易以为页面就这么多内容。
   绝对定位脱离文档流 —— 否则它会和标题一起被居中，把标题顶偏 */
.hero-hint {
  position: absolute;
  /* 跟着标题一起上移，两者始终保持同样的间距 */
  bottom: calc(40px + var(--hero-lift));
  left: 50%;
  transform: translateX(-50%);
  width: 1.7em;
  height: 1.7em;
  color: var(--text-muted);
  animation: hero-bounce 2s ease-in-out infinite;
}
/* 动画用独立的 translate 属性而不是 transform：
   transform 已经被上面拿去居中了，动画里再写一次会把居中覆盖掉，箭头会跳到左边 */
@keyframes hero-bounce {
  0%,
  100% {
    translate: 0 0;
    opacity: 0.55;
  }
  50% {
    translate: 0 7px;
    opacity: 1;
  }
}
/* 尊重系统里「减少动态效果」的设置 */
@media (prefers-reduced-motion: reduce) {
  .hero-hint,
  .caret {
    animation: none;
  }
}

.posts {
  padding-top: 4px;
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
  color: #7c7d8a;
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

h2 {
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
  /* 给右上角那个绝对定位的编辑按钮做参照 */
  position: relative;
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

/* 卡片右上角的编辑入口。平时藏起来，鼠标悬停卡片时才浮现，
   免得访客（和平时浏览的自己）被一堆管理图标干扰 */
.card-edit {
  position: absolute;
  top: 10px;
  right: 10px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  padding: 0;
  border: none;
  border-radius: 7px;
  background: rgba(255, 255, 255, 0.12);
  color: var(--text-muted);
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.2s, background 0.2s, color 0.2s;
}
.post-card:hover .card-edit,
.card-edit:focus-visible {
  opacity: 1;
}
.card-edit:hover {
  background: var(--brand);
  color: #fff;
}

/* 「写新文章」的样式在 style.css 的 .float-btn 里（和「回到顶部」共用同一套），
   这里只负责它的水平位置：排在回到顶部的左边。
   88 = 28(右边的按钮距边) + 48(它的宽度) + 12(间距) */
.fab {
  right: 88px;
}
.post-card:hover {
  border-color: rgba(66, 184, 131, 0.5);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.09);
  transform: translateY(-2px);
}
.post-card h3 {
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
  background: rgba(255, 255, 255, 0.08);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.9em;
}
.error {
  color: var(--danger);
}
</style>
