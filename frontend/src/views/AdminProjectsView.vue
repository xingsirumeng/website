<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  NButton,
  NConfigProvider,
  NEmpty,
  NForm,
  NFormItem,
  NIcon,
  NInput,
  NInputNumber,
  NSwitch,
  NTag,
  createDiscreteApi,
  darkTheme,
} from 'naive-ui'
import {
  AddOutline,
  ArrowBackOutline,
  CheckmarkCircleOutline,
  CreateOutline,
  ImageOutline,
  TrashOutline,
} from '@vicons/ionicons5'
import api, { API_BASE } from '@/api'
import { useAdmin } from '@/composables/useAdmin'
import AdminHeader from '@/components/AdminHeader.vue'
import { themeOverrides } from '@/theme'
import type { Project } from '@/types'

const router = useRouter()
const { isAdmin, checkAdmin } = useAdmin()

const { message, dialog } = createDiscreteApi(['message', 'dialog'], {
  configProviderProps: { theme: darkTheme, themeOverrides },
})

const mode = ref<'list' | 'edit'>('list')
const projects = ref<Project[]>([])
const loading = ref(false)
const editingId = ref<number | null>(null)

// 表单里所有字段都是字符串或数字，和后端的 ProjectBase 一一对应
const blankForm = () => ({
  name: '',
  description: '',
  tech: '',
  demo_url: '',
  repo_url: '',
  cover: '',
  sort: 0,
  published: true,
})
const form = ref(blankForm())

// 选文件用的隐藏 input，由「上传封面」按钮触发
const fileInput = ref<HTMLInputElement | null>(null)

function logout() {
  // 这里不重复实现退出逻辑，交给文章管理页统一处理
  router.push('/admin')
}

async function load() {
  loading.value = true
  try {
    const { data } = await api.get<Project[]>('/api/admin/projects')
    projects.value = data
    mode.value = 'list'
  } catch (err: any) {
    if (err.response?.status === 401) {
      // 令牌失效，交给文章管理页去弹登录界面
      router.replace('/admin')
      return
    }
    message.error('加载失败: ' + err.message)
  } finally {
    loading.value = false
  }
}

function startCreate() {
  editingId.value = null
  form.value = blankForm()
  mode.value = 'edit'
}

function startEdit(project: Project) {
  editingId.value = project.id
  form.value = {
    name: project.name,
    description: project.description,
    tech: project.tech,
    demo_url: project.demo_url,
    repo_url: project.repo_url,
    cover: project.cover,
    sort: project.sort,
    published: project.published,
  }
  mode.value = 'edit'
}

async function save() {
  if (!form.value.name.trim()) {
    message.warning('名称不能为空')
    return
  }

  loading.value = true
  try {
    if (editingId.value === null) {
      await api.post('/api/admin/projects', form.value)
    } else {
      await api.put(`/api/admin/projects/${editingId.value}`, form.value)
    }
    await load()
    message.success('已保存')
  } catch (err: any) {
    // 后端的校验错误（链接缺协议之类）在 detail 里，直接透出来给人看
    const detail = err.response?.data?.detail
    message.error(typeof detail === 'string' ? detail : '保存失败: ' + err.message)
  } finally {
    loading.value = false
  }
}

function remove(project: Project) {
  dialog.warning({
    title: '确认删除',
    content: `确定删除「${project.name}」吗？此操作不可撤销。`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      loading.value = true
      try {
        await api.delete(`/api/admin/projects/${project.id}`)
        await load()
        message.success('已删除')
      } catch (err: any) {
        message.error('删除失败: ' + err.message)
      } finally {
        loading.value = false
      }
    },
  })
}

async function uploadCover(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  // 用完就清空，否则连续选同一张图不会触发 change
  input.value = ''
  if (!file) return

  const body = new FormData()
  body.append('file', file)
  try {
    const { data } = await api.post<{ url: string }>('/api/admin/upload', body)
    // 后端给的是相对地址，前台展示时会补成绝对地址
    form.value.cover = data.url
    message.success('封面上传成功')
  } catch (err: any) {
    message.error('上传失败: ' + err.message)
  }
}

onMounted(async () => {
  // 这个页面没有登录界面：没登录就退回文章管理页去登录
  await checkAdmin()
  if (!isAdmin.value) {
    router.replace('/admin')
    return
  }
  load()
})
</script>

<template>
  <NConfigProvider :theme="darkTheme" :theme-overrides="themeOverrides">
    <div class="admin-shell">
      <AdminHeader :logged-in="true" @logout="logout" />

      <div>
        <!-- 列表 -->
        <template v-if="mode === 'list'">
          <div class="bar">
            <h1>项目管理</h1>
            <NButton type="primary" @click="startCreate">
              <template #icon>
                <NIcon :component="AddOutline" />
              </template>
              新建项目
            </NButton>
          </div>

          <NEmpty v-if="projects.length === 0" description="还没有项目，点「新建项目」开始吧" />

          <div v-else class="project-list">
            <div
              v-for="project in projects"
              :key="project.id"
              class="project-item"
              tabindex="0"
              @click="startEdit(project)"
              @keydown="(e: KeyboardEvent) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault()
                  startEdit(project)
                }
              }"
            >
              <img
                v-if="project.cover"
                class="thumb"
                :src="project.cover.startsWith('/images/') ? API_BASE + project.cover : project.cover"
                :alt="project.name"
                loading="lazy"
              />
              <div v-else class="thumb placeholder">
                <NIcon :component="ImageOutline" />
              </div>

              <div class="info">
                <span class="name">{{ project.name }}</span>
                <NTag :type="project.published ? 'success' : 'default'" size="small" round>
                  {{ project.published ? '已展示' : '未展示' }}
                </NTag>
                <span v-if="project.sort" class="sort">排序 {{ project.sort }}</span>
              </div>

              <NButton class="del-btn" size="small" quaternary type="error" @click.stop="remove(project)">
                <template #icon>
                  <NIcon :component="TrashOutline" />
                </template>
                删除
              </NButton>
            </div>
          </div>
        </template>

        <!-- 编辑器 -->
        <template v-else>
          <h1>
            <NIcon :component="CreateOutline" />
            {{ editingId === null ? '新建项目' : '编辑项目' }}
          </h1>

          <NForm label-placement="top">
            <NFormItem label="名称">
              <NInput v-model:value="form.name" placeholder="项目名" />
            </NFormItem>

            <NFormItem label="描述">
              <NInput
                v-model:value="form.description"
                type="textarea"
                :rows="4"
                placeholder="一两句话说明这个项目是做什么的。支持换行"
              />
            </NFormItem>

            <NFormItem label="技术栈">
              <NInput v-model:value="form.tech" placeholder="用逗号分隔，例如 Vue, FastAPI, SQLite" />
            </NFormItem>

            <NFormItem label="在线演示地址">
              <NInput v-model:value="form.demo_url" placeholder="https://…（留空则不显示按钮）" />
            </NFormItem>

            <NFormItem label="源码地址">
              <NInput v-model:value="form.repo_url" placeholder="https://github.com/…（留空则不显示）" />
            </NFormItem>

            <NFormItem label="封面图">
              <div class="cover-field">
                <NInput v-model:value="form.cover" placeholder="留空则不显示封面" />
                <NButton @click="fileInput?.click()">
                  <template #icon>
                    <NIcon :component="ImageOutline" />
                  </template>
                  上传
                </NButton>
                <input
                  ref="fileInput"
                  type="file"
                  accept="image/*"
                  class="hidden-file"
                  @change="uploadCover"
                />
              </div>
            </NFormItem>

            <div v-if="form.cover" class="cover-preview">
              <img
                :src="form.cover.startsWith('/images/') ? API_BASE + form.cover : form.cover"
                alt="封面预览"
              />
            </div>

            <NFormItem label="排序">
              <NInputNumber v-model:value="form.sort" :min="-999" :max="999" />
              <span class="hint">数字越大越靠前，用来把重要的项目顶上去</span>
            </NFormItem>

            <NFormItem label="在项目页展示">
              <NSwitch v-model:value="form.published" />
            </NFormItem>
          </NForm>

          <div class="actions">
            <NButton type="primary" :loading="loading" @click="save">
              <template #icon>
                <NIcon :component="CheckmarkCircleOutline" />
              </template>
              保存
            </NButton>
            <NButton quaternary @click="load">
              <template #icon>
                <NIcon :component="ArrowBackOutline" />
              </template>
              取消
            </NButton>
          </div>
        </template>
      </div>
    </div>
  </NConfigProvider>
</template>

<style scoped>
.admin-shell {
  min-height: 100vh;
  background: var(--bg);
}

/* 直接子选择器挑 div：顶栏是 <header>，内容区是 <div>，正好分得开 */
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

.project-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.project-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 10px 16px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 8px;
  cursor: pointer;
  transition: box-shadow 0.2s, border-color 0.2s;
}
.project-item:hover {
  border-color: rgba(66, 184, 131, 0.55);
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.07);
}
.project-item:focus-visible {
  outline: 2px solid var(--brand);
  outline-offset: 2px;
}

.thumb {
  width: 64px;
  height: 40px;
  flex-shrink: 0;
  object-fit: cover;
  border-radius: 5px;
  background: rgba(255, 255, 255, 0.06);
}
.thumb.placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
}

.info {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}
.name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.sort {
  flex-shrink: 0;
  color: var(--text-muted);
  font-size: 0.8rem;
}
.del-btn {
  margin-left: auto;
  flex-shrink: 0;
}

/* 封面那一行：输入框占满，按钮固定在右边 */
.cover-field {
  display: flex;
  gap: 8px;
  width: 100%;
}
.cover-field :deep(.n-input) {
  flex: 1;
}
/* 隐藏的文件选择框，靠「上传」按钮间接触发 */
.hidden-file {
  display: none;
}
.cover-preview {
  margin: -12px 0 18px;
}
.cover-preview img {
  width: 100%;
  max-width: 320px;
  aspect-ratio: 16 / 9;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid var(--border);
}

.hint {
  margin-left: 12px;
  color: var(--text-muted);
  font-size: 0.82rem;
}

.actions {
  display: flex;
  gap: 10px;
  margin-top: 24px;
}
</style>
