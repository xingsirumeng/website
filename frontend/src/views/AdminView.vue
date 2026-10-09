<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import {
  NButton,
  NCard,
  NConfigProvider,
  NEmpty,
  NForm,
  NFormItem,
  NIcon,
  NInput,
  NTag,
  createDiscreteApi,
  darkTheme,
} from 'naive-ui'
import {
  CheckmarkCircleOutline,
  CreateOutline,
  KeyOutline,
  TrashOutline,
} from '@vicons/ionicons5'
import { useRoute, useRouter } from 'vue-router'
import api, { TOKEN_KEY } from '@/api'
import { useAdmin } from '@/composables/useAdmin'
import AdminHeader from '@/components/AdminHeader.vue'
import VditorEditor from '@/components/VditorEditor.vue'
import { themeOverrides } from '@/theme'
import { formatDate } from '@/utils/format'
import { collapseImageUrls, expandImageUrls } from '@/utils/imagePath'
import type { PostDetail, PostSummary } from '@/types'

// 用 createDiscreteApi 而不是嵌 <n-message-provider>：
// 省一层组件嵌套，也不用把 AdminView 拆成两个文件。
// 主题同样传进去，否则弹出的提示是默认蓝色。
const { message, dialog } = createDiscreteApi(['message', 'dialog'], {
  // 弹窗和提示是独立挂载的，不在这棵组件树里，主题得单独传一份
  configProviderProps: { theme: darkTheme, themeOverrides },
})

const route = useRoute()
const router = useRouter()
// 前台的「管理」「清单」入口依赖这份状态，登录/退出时要同步
const { isAdmin, checkAdmin } = useAdmin()

// 页面三种状态：登录 / 文章列表 / 编辑器
const mode = ref<'login' | 'list' | 'edit'>('login')

const password = ref('')
// 列表接口不返回正文，所以这里是 PostSummary 而不是 PostDetail
const posts = ref<PostSummary[]>([])
const loading = ref(false)
const error = ref('')

// 正在编辑的文章 id，null 表示新建
const editingId = ref<number | null>(null)
const form = ref({ title: '', summary: '', tags: '', content: '', published: false })

// 正文默认用可视化编辑器；Vditor 万一加载不出来，随时能切回纯文本接着写
const plainMode = ref(false)

/* ---------- 草稿自动保存 ----------
   只写 localStorage，不碰服务器。自动往服务器存会和「你主动存的草稿」
   混在一起，分不清哪些是真正想留下的。 */
const DRAFT_KEY = 'blog_draft'
const draftSavedAt = ref('')
let draftTimer: number | undefined

function persistDraft() {
  if (mode.value !== 'edit') return
  try {
    localStorage.setItem(
      DRAFT_KEY,
      JSON.stringify({
        editingId: editingId.value,
        form: form.value,
        savedAt: Date.now(),
      }),
    )
    draftSavedAt.value = new Date().toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    // 隐私模式或存储配额满。自动保存失败不该打断写作，静默跳过
  }
}

function clearDraft() {
  window.clearTimeout(draftTimer)
  localStorage.removeItem(DRAFT_KEY)
  draftSavedAt.value = ''
}

// 停止输入 1.5 秒后落盘。不用定时轮询 —— 那样没有任何改动也会一直写
watch(
  form,
  () => {
    if (mode.value !== 'edit') return
    window.clearTimeout(draftTimer)
    draftTimer = window.setTimeout(persistDraft, 1500)
  },
  { deep: true },
)

// 进入编辑器时问一次要不要恢复
function offerDraftRestore() {
  const raw = localStorage.getItem(DRAFT_KEY)
  if (!raw) return

  let saved: any
  try {
    saved = JSON.parse(raw)
  } catch {
    clearDraft() // 存坏了，直接丢掉
    return
  }

  // 和当前表单内容一样就没必要问（比如刚保存完、或者本来就没改动）
  const same =
    saved?.form?.title === form.value.title && saved?.form?.content === form.value.content
  if (same) {
    clearDraft()
    return
  }

  dialog.warning({
    title: '恢复未保存的草稿？',
    content: `检测到 ${new Date(saved.savedAt).toLocaleString('zh-CN')} 自动保存的内容`,
    positiveText: '恢复',
    negativeText: '丢弃',
    onPositiveClick: () => {
      form.value = { ...saved.form }
      editingId.value = saved.editingId ?? null
    },
    onNegativeClick: clearDraft,
  })
}

// 标签在界面上是一个输入框，中英文逗号都支持
function splitTags(text: string): string[] {
  return text
    .split(/[,，]/)
    .map((tag) => tag.trim())
    .filter(Boolean)
}

async function login() {
  error.value = ''
  loading.value = true
  try {
    const { data } = await api.post<{ token: string }>('/api/auth/login', {
      password: password.value,
    })
    localStorage.setItem(TOKEN_KEY, data.token)
    // 强制重新确认：之前很可能是「没登录」的状态，现在登录了得同步给前台
    await checkAdmin(true)
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
  // 退出后前台不该再显示管理入口
  isAdmin.value = false
  posts.value = []
  error.value = ''
  mode.value = 'login'
}

async function loadPosts() {
  error.value = ''
  loading.value = true
  try {
    const { data } = await api.get<PostSummary[]>('/api/admin/posts')
    posts.value = data
    mode.value = 'list'
  } catch (err: any) {
    // 令牌过期或没登录就回落到登录界面（拦截器已经把本地令牌清掉了）
    if (err.response?.status === 401) {
      error.value = '请先登录'
      mode.value = 'login'
    } else {
      message.error('加载失败: ' + err.message)
    }
  } finally {
    loading.value = false
  }
}

// 键盘打开文章。不能写成 @keydown.enter 和 @keydown.space 两个绑定 ——
// 它们编译后都叫 onKeydown，会在同一个元素上撞成重复的键，vue-tsc 直接报错。
function onCardKeydown(event: KeyboardEvent, post: PostSummary) {
  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault()
    startEdit(post)
  }
}

function startCreate() {
  error.value = ''
  editingId.value = null
  form.value = { title: '', summary: '', tags: '', content: '', published: false }
  mode.value = 'edit'
  offerDraftRestore()
}

// 主动点「取消」就是放弃改动，本地自动保存也一起丢掉
function cancelEdit() {
  clearDraft()
  loadPosts()
}

// 列表接口不带正文，必须单独拉一次详情。
// 直接拿列表项回填会让 content 变成 undefined，保存时把正文整个覆盖掉。
async function startEdit(post: PostSummary) {
  // 整张卡片可点，手快会连点出两次请求，这里挡一下
  if (loading.value) return

  error.value = ''
  loading.value = true
  try {
    const { data } = await api.get<PostDetail>(`/api/admin/posts/${post.id}`)
    editingId.value = data.id
    form.value = {
      title: data.title,
      summary: data.summary,
      tags: data.tags.join(', '),
      // 库里存的是相对地址，编辑器里要显示绝对地址，否则线上会裂图
      content: expandImageUrls(data.content),
      published: data.published,
    }
    mode.value = 'edit'
    offerDraftRestore()
  } catch (err: any) {
    message.error('打开失败: ' + err.message)
  } finally {
    loading.value = false
  }
}

async function save(published: boolean) {
  if (!form.value.title.trim()) {
    message.warning('标题不能为空')
    return
  }

  loading.value = true
  const payload = {
    title: form.value.title.trim(),
    summary: form.value.summary.trim(),
    // 编辑器里是绝对地址，入库前收回相对地址，保证存的内容与环境无关
    content: collapseImageUrls(form.value.content),
    tags: splitTags(form.value.tags),
    published,
  }

  try {
    if (editingId.value === null) {
      await api.post('/api/admin/posts', payload)
    } else {
      await api.put(`/api/admin/posts/${editingId.value}`, payload)
    }
    // 已经存成功了，本地那份自动保存就没用了
    clearDraft()
    await loadPosts()
    message.success(published ? '已发布' : '已存为草稿')
  } catch (err: any) {
    message.error('保存失败: ' + err.message)
  } finally {
    loading.value = false
  }
}

function remove(post: PostSummary) {
  dialog.warning({
    title: '确认删除',
    content: `确定删除《${post.title}》吗？此操作不可撤销。`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      loading.value = true
      try {
        await api.delete(`/api/admin/posts/${post.id}`)
        await loadPosts()
        message.success('已删除')
      } catch (err: any) {
        message.error('删除失败: ' + err.message)
      } finally {
        loading.value = false
      }
    },
  })
}

onMounted(async () => {
  // 带着令牌进页面就直接拉列表；令牌过期会在 loadPosts 里回落到登录界面
  if (!localStorage.getItem(TOKEN_KEY)) return

  await loadPosts()
  // 没进到列表状态说明令牌失效了、落回了登录界面，深链就不用管了
  if (mode.value !== 'list') return

  // 首页那两个入口靠 query 参数直接落到对应界面，省掉「进后台再找文章」
  const editId = route.query.edit
  const isNew = route.query.new

  if (typeof editId === 'string') {
    const post = posts.value.find((p) => p.id === Number(editId))
    if (post) await startEdit(post)
  } else if (isNew === '1') {
    startCreate()
  }

  // 参数用完就清掉，否则刷新页面会莫名其妙又打开一次编辑器
  if (editId || isNew) router.replace({ path: '/admin' })
})
</script>

<template>
  <NConfigProvider :theme="darkTheme" :theme-overrides="themeOverrides">
    <div class="admin-shell">
      <AdminHeader :logged-in="mode !== 'login'" @logout="logout" />

      <!-- 登录 -->
      <div v-if="mode === 'login'" class="login">
        <NCard :bordered="false" class="login-card">
          <template #header>
            <span class="card-title">
              <NIcon :component="KeyOutline" />
              后台登录
            </span>
          </template>
          <NInput
            v-model:value="password"
            type="password"
            size="large"
            placeholder="请输入管理密码"
            show-password-on="click"
            @keydown.enter="login"
          />
          <p v-if="error" class="error">{{ error }}</p>
          <NButton
            type="primary"
            size="large"
            block
            :loading="loading"
            class="login-btn"
            @click="login"
          >
            登录
          </NButton>
        </NCard>
      </div>

      <!-- 文章列表 -->
      <div v-else-if="mode === 'list'">
        <div class="bar">
          <h1>文章管理</h1>
          <NButton type="primary" @click="startCreate">
            <template #icon>
              <NIcon :component="CreateOutline" />
            </template>
            写新文章
          </NButton>
        </div>

        <NEmpty v-if="posts.length === 0" description="还没有文章，点「写新文章」开始吧" />

        <div v-else class="post-list">
          <!-- 用普通 div 而不是 NCard：这只是个可点击的列表行，
               用不着卡片组件那套 header/footer 机制，而且能避免依赖它的内部类名。
               整行可点开编辑，加了 tabindex 和键盘处理，
               否则删掉「编辑」按钮后键盘用户就没法打开文章了 -->
          <div
            v-for="post in posts"
            :key="post.id"
            class="post-item"
            tabindex="0"
            @click="startEdit(post)"
            @keydown="onCardKeydown($event, post)"
          >
            <div class="info">
              <span class="title">{{ post.title }}</span>
              <NTag :type="post.published ? 'success' : 'default'" size="small" round>
                {{ post.published ? '已发布' : '草稿' }}
              </NTag>
              <span class="date">{{ formatDate(post.updated_at) }}</span>
            </div>
            <!-- .stop 必须加：不然点删除会冒泡到整行，一边弹确认框一边打开编辑器 -->
            <NButton
              class="del-btn"
              size="small"
              quaternary
              type="error"
              @click.stop="remove(post)"
            >
              <template #icon>
                <NIcon :component="TrashOutline" />
              </template>
              删除
            </NButton>
          </div>
        </div>
      </div>

      <!-- 编辑器 -->
      <div v-else class="editor">
        <h1>
          <NIcon :component="CreateOutline" />
          {{ editingId === null ? '写新文章' : '编辑文章' }}
        </h1>

        <NForm label-placement="top">
          <NFormItem label="标题">
            <NInput v-model:value="form.title" placeholder="文章标题" />
          </NFormItem>
          <NFormItem label="摘要">
            <NInput v-model:value="form.summary" placeholder="一句话概括，显示在列表页" />
          </NFormItem>
          <NFormItem label="标签">
            <NInput v-model:value="form.tags" placeholder="用逗号分隔，例如 Vue, FastAPI" />
          </NFormItem>
        </NForm>

        <div class="editor-head">
          <label>正文</label>
          <div class="mode-switch">
            <NButton
              size="small"
              :type="plainMode ? 'default' : 'primary'"
              @click="plainMode = false"
            >
              可视化
            </NButton>
            <NButton
              size="small"
              :type="plainMode ? 'primary' : 'default'"
              @click="plainMode = true"
            >
              纯文本
            </NButton>
          </div>
        </div>

        <!-- :key 很关键 —— 切换文章时强制重建编辑器，否则上一篇的内容会残留在里面。
             两个模式绑的是同一个 form.content，来回切内容不会丢 -->
        <VditorEditor v-if="!plainMode" :key="editingId ?? 'new'" v-model="form.content" />
        <NInput
          v-else
          v-model:value="form.content"
          type="textarea"
          :rows="18"
          placeholder="# 标题&#10;&#10;图片可直接粘贴或拖进来上传"
        />

        <div class="editor-actions">
          <NButton type="primary" :loading="loading" @click="save(true)">
            <template #icon>
              <NIcon :component="CheckmarkCircleOutline" />
            </template>
            {{ form.published ? '更新并发布' : '发布' }}
          </NButton>
          <NButton :loading="loading" @click="save(false)">存草稿</NButton>
          <NButton quaternary @click="cancelEdit">取消</NButton>
        </div>

        <p v-if="draftSavedAt" class="draft-hint">
          草稿已自动保存到本地 · {{ draftSavedAt }}
        </p>
      </div>
    </div>
  </NConfigProvider>
</template>

<style scoped>
.admin-shell {
  min-height: 100vh;
  background: var(--bg);
}

/* 内容区居中限宽。
   用直接子选择器挑 div：顶栏是 <header>，内容区是 <div>，正好分得开 ——
   这样就不用再包一层 div，省得把里面上百行的缩进全改一遍 */
.admin-shell > div {
  max-width: 820px;
  margin: 0 auto;
  padding: 28px 20px 64px;
}
h1 {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1.4rem;
  margin: 0 0 20px;
}
.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 登录 */
.login-card {
  max-width: 380px;
  margin: 40px auto 0;
}
.login-btn {
  margin-top: 18px;
}
.error {
  color: var(--danger);
  font-size: 0.88rem;
  margin: 10px 0 0;
}

/* 列表 */
.bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 18px;
}
.bar h1 {
  margin: 0;
}
.post-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.post-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 9px 16px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 8px;
  cursor: pointer;
  transition: box-shadow 0.2s, border-color 0.2s;
}
.post-item:hover {
  border-color: rgba(66, 184, 131, 0.55);
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.07);
}
.post-item:focus-visible {
  outline: 2px solid var(--brand);
  outline-offset: 2px;
}
/* 标题被挤压时才省略，删除按钮永远保持完整 */
.info {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}
.info .title {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.info .date {
  flex-shrink: 0;
  color: var(--text-muted);
  font-size: 0.82rem;
}
.del-btn {
  flex-shrink: 0;
}

/* 编辑器 */
.editor-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 20px 0 8px;
}
.editor-head label {
  font-size: 0.88rem;
  color: var(--text-muted);
}
.mode-switch {
  display: flex;
  gap: 6px;
}
.editor-actions {
  display: flex;
  gap: 10px;
  margin-top: 24px;
}
/* 自动保存的提示。做得不显眼 —— 它是用来让人安心的，不是抢注意力的 */
.draft-hint {
  margin: 12px 0 0;
  font-size: 0.82rem;
  color: var(--text-muted);
}
</style>
