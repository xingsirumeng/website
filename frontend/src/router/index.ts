import { createRouter, createWebHashHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'

const router = createRouter({
  // hash 模式继续保留：GitHub Pages 上不需要额外的 404 回退配置
  history: createWebHashHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/post/:id',
      name: 'post',
      component: () => import('@/views/PostView.vue'),
    },
    {
      path: '/tags',
      name: 'tags',
      component: () => import('@/views/TagsView.vue'),
    },
    {
      path: '/archive',
      name: 'archive',
      component: () => import('@/views/ArchiveView.vue'),
    },
    {
      path: '/admin',
      name: 'admin',
      component: () => import('@/views/AdminView.vue'),
    },
  ],
})

export default router
