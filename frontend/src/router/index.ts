import { createRouter, createWebHashHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'

const router = createRouter({
  // hash 模式继续保留：GitHub Pages 上不需要额外的 404 回退配置
  history: createWebHashHistory(),

  scrollBehavior(_to, _from, savedPosition) {
    // 浏览器前进/后退时恢复原来的位置（savedPosition），其余情况回到顶部。
    // 不配这个的话跳转不会动滚动条 —— 你在文章页滚到一半点了「标签」，
    // 新页面一打开就停在中间，看着像内容缺失
    return savedPosition ?? { top: 0 }
  },

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
      path: '/projects',
      name: 'projects',
      component: () => import('@/views/ProjectsView.vue'),
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
      // 后台是独立界面：不显示前台的导航栏，由 AdminView 自己画外壳
      meta: { bare: true },
    },
    {
      path: '/admin/projects',
      name: 'admin-projects',
      component: () => import('@/views/AdminProjectsView.vue'),
      // 同上：项目管理也是独立的后台界面
      meta: { bare: true },
    },
  ],
})

export default router
