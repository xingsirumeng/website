<script setup lang="ts">
import { NButton, NIcon } from 'naive-ui'
import {
  CubeOutline,
  DocumentTextOutline,
  EyeOutline,
  LogOutOutline,
  SettingsOutline,
} from '@vicons/ionicons5'

// 抽成组件是因为文章管理和项目管理各有一个页面，顶栏完全一样
defineProps<{ loggedIn: boolean }>()
const emit = defineEmits<{ logout: [] }>()
</script>

<template>
  <header class="admin-header">
    <span class="brand">
      <NIcon :component="SettingsOutline" />
      后台管理
    </span>

    <!-- 板块切换。登录后才显示 —— 没登录时点了也只会被踢回登录界面 -->
    <nav v-if="loggedIn" class="sections">
      <router-link to="/admin">
        <NIcon :component="DocumentTextOutline" />
        文章
      </router-link>
      <router-link to="/admin/projects">
        <NIcon :component="CubeOutline" />
        项目
      </router-link>
    </nav>

    <div class="header-actions">
      <router-link to="/" class="site-link">
        <NIcon :component="EyeOutline" />
        查看博客
      </router-link>
      <NButton v-if="loggedIn" size="small" quaternary @click="emit('logout')">
        <template #icon>
          <NIcon :component="LogOutOutline" />
        </template>
        退出
      </NButton>
    </div>
  </header>
</template>

<style scoped>
/* 通栏深色顶栏，和前台导航同一个色系，但内容是后台自己的 */
.admin-header {
  position: sticky;
  top: 0;
  z-index: 10;
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 12px 24px;
  background: var(--dark);
  color: #fff;
  box-shadow: 0 1px 10px rgba(0, 0, 0, 0.15);
}

.brand {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1rem;
  letter-spacing: 0.5px;
}
.admin-header :deep(.n-icon) {
  vertical-align: -0.18em;
}
/* 品牌图标用品牌绿，其余图标跟随文字色 */
.brand :deep(.n-icon) {
  color: var(--brand);
}

.sections {
  display: flex;
  gap: 4px;
}
.sections a {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 5px 14px;
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
  text-decoration: none;
  transition: background 0.2s, color 0.2s;
}
.sections a:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}
/* 必须用 exact-active 而不是 router-link-active：
   /admin 是 /admin/projects 的前缀，用后者的话两个标签会同时高亮 */
.sections a.router-link-exact-active {
  background: var(--brand);
  color: #fff;
}

/* margin-left: auto 把右侧这组推到最右边 */
.header-actions {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 14px;
}
.site-link {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  color: rgba(255, 255, 255, 0.82);
  font-size: 0.9rem;
  text-decoration: none;
  transition: color 0.2s;
}
.site-link:hover {
  color: #fff;
}
/* 顶栏里的 NButton 默认是深灰字，在深色底上看不清，得改浅 */
.admin-header :deep(.n-button) {
  color: rgba(255, 255, 255, 0.82);
}
.admin-header :deep(.n-button:hover) {
  color: #fff;
}

@media (max-width: 640px) {
  .admin-header {
    flex-wrap: wrap;
    gap: 10px;
  }
  .brand {
    font-size: 0.92rem;
  }
}
</style>
