<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { CalendarOutline, HomeOutline, PricetagOutline } from '@vicons/ionicons5'

const route = useRoute()
// 带 bare 标记的路由（目前只有后台）自己管布局，不要前台这层壳
const bare = computed(() => route.meta.bare === true)
</script>

<template>
  <div id="app">
    <nav v-if="!bare" class="navbar">
      <router-link to="/">
        <HomeOutline class="svg-icon" />
        首页
      </router-link>
      <router-link to="/tags">
        <PricetagOutline class="svg-icon" />
        标签
      </router-link>
      <router-link to="/archive">
        <CalendarOutline class="svg-icon" />
        归档
      </router-link>
    </nav>
    <main :class="{ 'main-bare': bare }">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.navbar {
  /* 吸顶：文章读长了想切页面不用滚回顶部 */
  position: sticky;
  top: 0;
  z-index: 10;
  display: flex;
  gap: 6px;
  justify-content: center;
  padding: 12px 20px;
  background: #1a1a2e;
  box-shadow: 0 1px 10px rgba(0, 0, 0, 0.15);
}
.navbar a {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: rgba(255, 255, 255, 0.82);
  text-decoration: none;
  font-size: 0.95rem;
  padding: 6px 16px;
  border-radius: 6px;
  transition: background 0.2s, color 0.2s;
}
.navbar a:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}
.navbar a.router-link-active {
  background: #42b883;
  color: #fff;
}
main {
  /* 列表 / 标签 / 归档页需要宽度，所以这里保持宽容器；
     文章正文由 PostView 自己收窄到 --reading-width */
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 20px;
}
/* 后台自己管布局：去掉前台的居中容器和内边距，
   否则它那条通栏的顶栏会被限制在 1000px 里 */
main.main-bare {
  max-width: none;
  padding: 0;
}
</style>
