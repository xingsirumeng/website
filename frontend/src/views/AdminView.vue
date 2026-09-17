<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api, { TOKEN_KEY } from '@/api'
import { formatDate } from '@/utils/format'
import type { PostDetail } from '@/types'

// 页面三种状态：登录 / 文章列表 / 编辑器
const mode = ref<'login' | 'list' | 'edit'>('login')

const password = ref('')
const posts = ref<PostDetail[]>([])
const loading = ref(false)
const error = ref('')
const notice = ref('')

// 正在编辑的文章 id，null 表示新建
const editingId = ref<number | null>(null)
const form = ref({ title: '', summary: '', tags: '', content: '', published: false })

// 标签在界面上是一个输入框，中英文逗号都支持
function splitTags(text: string): string[] {
  return text
    .split(/[,，]/)
    .map((tag) => tag.trim())
    .filter(Boolean)
}

function clearMessages() {
  error.value = ''
  notice.value = ''
}

async function login() {
  clearMessages()
  loading.value = true
  try {
    const { data } = await api.post<{ token: string }>('/api/auth/login', {
      password: password.value,
    })
    localStorage.setItem(TOKEN_KEY, data.token)
    password.value = ''
    await loadPosts()
  } catch (err: any) {
    error.value = err.response?.status === 401 ? '密码错误' : '登录失败: ' + err.message
  } finally {
    loading.value = false
  }
}

function logout() {
  localStorage.removeItem(TOKEN_KEY)
  posts.value = []
  clearMessages()
  mode.value = 'login'
}

async function loadPosts() {
  clearMessages()
  loading.value = true
  try {
    const { data } = await api.get<PostDetail[]>('/api/admin/posts')
    posts.value = data
    mode.value = 'list'
  } catch (err: any) {
    // 令牌过期或没登录就回落到登录界面（拦截器已经把本地令牌清掉了）
    if (err.response?.status === 401) {
      error.value = '请先登录'
      mode.value = 'login'
    } else {
      error.value = '加载失败: ' + err.message
    }
  } finally {
    loading.value = false
  }
}

function startCreate() {
  clearMessages()
  editingId.value = null
  form.value = { title: '', summary: '', tags: '', content: '', published: false }
  mode.value = 'edit'
}

function startEdit(post: PostDetail) {
  clearMessages()
  editingId.value = post.id
  form.value = {
    title: post.title,
    summary: post.summary,
    tags: post.tags.join(', '),
    content: post.content,
    published: post.published,
  }
  mode.value = 'edit'
}

async function save(published: boolean) {
  if (!form.value.title.trim()) {
    error.value = '标题不能为空'
    return
  }

  clearMessages()
  loading.value = true
  const payload = {
    title: form.value.title.trim(),
    summary: form.value.summary.trim(),
    content: form.value.content,
    tags: splitTags(form.value.tags),
    published,
  }

  try {
    if (editingId.value === null) {
      await api.post('/api/admin/posts', payload)
    } else {
      await api.put(`/api/admin/posts/${editingId.value}`, payload)
    }
    await loadPosts()
    notice.value = published ? '已发布 ✅' : '已存为草稿 ✅'
  } catch (err: any) {
    error.value = '保存失败: ' + err.message
  } finally {
    loading.value = false
  }
}

async function remove(post: PostDetail) {
  if (!window.confirm(`确定删除《${post.title}》吗？此操作不可撤销。`)) {
    return
  }

  clearMessages()
  loading.value = true
  try {
    await api.delete(`/api/admin/posts/${post.id}`)
    await loadPosts()
    notice.value = '已删除 ✅'
  } catch (err: any) {
    error.value = '删除失败: ' + err.message
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  // 带着令牌进页面就直接拉列表；令牌过期会在 loadPosts 里回落到登录界面
  if (localStorage.getItem(TOKEN_KEY)) {
    loadPosts()
  }
})
</script>

<template>
  <div class="admin">
    <!-- 登录 -->
    <div v-if="mode === 'login'" class="login">
      <h1>🔑 后台登录</h1>
      <form @submit.prevent="login">
        <input
          v-model="password"
          type="password"
          placeholder="请输入管理密码"
          autocomplete="current-password"
        />
        <button type="submit" :disabled="loading">登录</button>
      </form>
      <p v-if="error" class="error">{{ error }}</p>
    </div>

    <!-- 文章列表 -->
    <div v-else-if="mode === 'list'">
      <div class="bar">
        <h1>📋 文章管理</h1>
        <div class="bar-actions">
          <button @click="startCreate">✏️ 写新文章</button>
          <button class="ghost" @click="logout">退出登录</button>
        </div>
      </div>

      <p v-if="error" class="error">{{ error }}</p>
      <p v-if="notice" class="notice">{{ notice }}</p>

      <p v-if="posts.length === 0" class="empty">还没有文章，点「写新文章」开始吧</p>
      <ul v-else class="post-list">
        <li v-for="post in posts" :key="post.id">
          <div class="info">
            <span class="title">{{ post.title }}</span>
            <span class="badge" :class="post.published ? 'live' : 'draft'">
              {{ post.published ? '已发布' : '草稿' }}
            </span>
            <span class="date">{{ formatDate(post.updated_at) }}</span>
          </div>
          <div class="row-actions">
            <button class="ghost" @click="startEdit(post)">编辑</button>
            <button class="ghost danger" @click="remove(post)">删除</button>
          </div>
        </li>
      </ul>
    </div>

    <!-- 编辑器 -->
    <div v-else class="editor">
      <h1>{{ editingId === null ? '✏️ 写新文章' : '✏️ 编辑文章' }}</h1>

      <p v-if="error" class="error">{{ error }}</p>

      <label>标题</label>
      <input v-model="form.title" type="text" placeholder="文章标题" />

      <label>摘要</label>
      <input v-model="form.summary" type="text" placeholder="一句话概括，显示在列表页" />

      <label>标签（用逗号分隔）</label>
      <input v-model="form.tags" type="text" placeholder="Vue, FastAPI" />

      <label>正文（Markdown，图片用外链）</label>
      <textarea
        v-model="form.content"
        rows="18"
        placeholder="# 标题&#10;&#10;正文支持 Markdown，图片写 ![](https://图片地址)"
      ></textarea>

      <div class="editor-actions">
        <button :disabled="loading" @click="save(true)">
          {{ form.published ? '更新并发布' : '发布' }}
        </button>
        <button class="ghost" :disabled="loading" @click="save(false)">存草稿</button>
        <button class="ghost" :disabled="loading" @click="loadPosts">取消</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin {
  padding: 20px 0;
  max-width: 760px;
  margin: 0 auto;
}
h1 {
  font-size: 1.5rem;
  margin: 0 0 20px;
}

/* 登录 */
.login form {
  display: flex;
  gap: 10px;
}
.login input {
  flex: 1;
}

/* 通用控件 */
input,
textarea {
  font: inherit;
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #e5e4e7;
  border-radius: 6px;
  background: #fff;
  color: inherit;
}
input:focus,
textarea:focus {
  outline: 2px solid rgba(66, 184, 131, 0.4);
  border-color: #42b883;
}
textarea {
  resize: vertical;
  font-family: ui-monospace, Consolas, monospace;
  font-size: 0.92rem;
  line-height: 1.6;
}
button {
  font: inherit;
  padding: 8px 18px;
  border: 1px solid #42b883;
  border-radius: 6px;
  background: #42b883;
  color: #fff;
  cursor: pointer;
  white-space: nowrap;
  transition: opacity 0.2s;
}
button:hover:not(:disabled) {
  opacity: 0.88;
}
button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
button.ghost {
  background: #fff;
  color: #333;
  border-color: #d5d5d9;
}
button.danger {
  color: #e74c3c;
  border-color: #f0c4bf;
}

/* 列表 */
.bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}
.bar h1 {
  margin: 0;
}
.bar-actions {
  display: flex;
  gap: 8px;
}
.post-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.post-list li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding: 12px 16px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  margin-bottom: 8px;
}
.info {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}
.title {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.badge {
  flex-shrink: 0;
  font-size: 0.75rem;
  padding: 1px 8px;
  border-radius: 20px;
}
.badge.live {
  background: rgba(66, 184, 131, 0.14);
  color: #2f8f66;
}
.badge.draft {
  background: #eee;
  color: #888;
}
.date {
  flex-shrink: 0;
  color: #999;
  font-size: 0.82rem;
}
.row-actions {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}
.row-actions button {
  padding: 4px 12px;
  font-size: 0.88rem;
}

/* 编辑器 */
.editor label {
  display: block;
  font-size: 0.88rem;
  color: #666;
  margin: 16px 0 6px;
}
.editor-actions {
  display: flex;
  gap: 10px;
  margin-top: 24px;
}

.error {
  color: #e74c3c;
}
.notice {
  color: #2f8f66;
}
.empty {
  color: #666;
}
</style>
