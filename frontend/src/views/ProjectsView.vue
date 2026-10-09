<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  CubeOutline,
  LogoGithub,
  OpenOutline,
  SyncOutline,
} from '@vicons/ionicons5'
import api, { API_BASE } from '@/api'
import type { Project } from '@/types'

const projects = ref<Project[]>([])
const loading = ref(true)
const error = ref('')

// 封面可能是本站的相对地址（后台上传后拿到的），要按当前环境补成绝对地址。
// 外链原样返回
function coverUrl(cover: string): string {
  return cover.startsWith('/images/') ? `${API_BASE}${cover}` : cover
}

// 技术栈存的是逗号分隔的字符串，展示时拆成一个个小标签。
// 中英文逗号都认，手滑打了中文逗号也不会变成一个整体
function techList(tech: string): string[] {
  return tech
    .split(/[,，]/)
    .map((t) => t.trim())
    .filter(Boolean)
}

onMounted(async () => {
  try {
    const { data } = await api.get<Project[]>('/api/projects')
    projects.value = data
  } catch (err: any) {
    error.value = '加载失败: ' + err.message
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="projects">
    <h1>
      <CubeOutline class="svg-icon" />
      项目
    </h1>

    <div v-if="loading" class="loading">
      <SyncOutline class="svg-icon spin" />
      加载中...
    </div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <p v-else-if="projects.length === 0" class="empty">还没有项目</p>

    <div v-else class="grid">
      <article v-for="project in projects" :key="project.id" class="card">
        <img
          v-if="project.cover"
          class="cover"
          :src="coverUrl(project.cover)"
          :alt="project.name"
          loading="lazy"
        />

        <div class="body">
          <h2>{{ project.name }}</h2>

          <div v-if="project.tech" class="tech">
            <span v-for="t in techList(project.tech)" :key="t" class="chip">{{ t }}</span>
          </div>

          <p v-if="project.description" class="desc">{{ project.description }}</p>

          <div v-if="project.demo_url || project.repo_url" class="links">
            <a
              v-if="project.demo_url"
              class="link"
              :href="project.demo_url"
              target="_blank"
              rel="noopener noreferrer"
            >
              <OpenOutline class="svg-icon" />
              在线演示
            </a>
            <a
              v-if="project.repo_url"
              class="link"
              :href="project.repo_url"
              target="_blank"
              rel="noopener noreferrer"
            >
              <LogoGithub class="svg-icon" />
              源码
            </a>
          </div>
        </div>
      </article>
    </div>
  </div>
</template>

<style scoped>
.projects {
  padding: 28px 0 64px;
}
h1 {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1.5rem;
  margin: 0 0 28px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 18px;
}

.card {
  display: flex;
  flex-direction: column;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 10px;
  overflow: hidden; /* 封面图要跟着圆角裁掉 */
  transition: box-shadow 0.2s, transform 0.2s, border-color 0.2s;
}
.card:hover {
  border-color: rgba(66, 184, 131, 0.5);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.09);
  transform: translateY(-2px);
}

.cover {
  display: block;
  width: 100%;
  /* 固定比例，避免不同尺寸的封面把卡片撑得高矮不齐 */
  aspect-ratio: 16 / 9;
  object-fit: cover;
  /* 底是深色的，图还没加载出来时先给一块底色，别闪白 */
  background: rgba(255, 255, 255, 0.05);
}

.body {
  display: flex;
  flex-direction: column;
  flex: 1;
  padding: 20px 22px 22px;
}
h2 {
  font-size: 1.15rem;
  line-height: 1.4;
  margin: 0 0 10px;
}

.tech {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 12px;
}
.chip {
  background: var(--brand-soft);
  color: var(--brand);
  font-size: 0.76rem;
  padding: 2px 10px;
  border-radius: 20px;
}

.desc {
  /* 项目描述允许换行，但不是 Markdown —— 纯文本 + 保留换行就够 */
  white-space: pre-wrap;
  color: var(--text-muted);
  font-size: 0.9rem;
  line-height: 1.65;
  margin: 0 0 18px;
  overflow-wrap: anywhere;
}

.links {
  /* 贴到卡片底部，同一行的卡片按钮能对齐 */
  margin-top: auto;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.link {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 0.85rem;
  padding: 5px 14px;
  border: 1px solid var(--border);
  border-radius: 6px;
  color: var(--text);
  text-decoration: none;
  transition: background 0.2s, border-color 0.2s, color 0.2s;
}
.link:hover {
  background: var(--brand);
  border-color: var(--brand);
  color: #fff;
}

.empty {
  color: var(--text-muted);
}
.error {
  color: var(--danger);
}
@media (prefers-reduced-motion: reduce) {
  .card:hover {
    transform: none;
  }
}
</style>
