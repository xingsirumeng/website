<script setup lang="ts">
import {
  computed,
  defineAsyncComponent,
  onMounted,
  onBeforeUnmount,
  ref,
  watch,
} from 'vue'
import { useRoute } from 'vue-router'
import {
  ArrowUpOutline,
  CalendarOutline,
  CubeOutline,
  HomeOutline,
  ListOutline,
  PricetagOutline,
  SettingsOutline,
} from '@vicons/ionicons5'
import wallpaperMorning from '@/assets/wallpaper1.jpg'
import wallpaperDusk from '@/assets/wallpaper2.jpg'
import wallpaperNight from '@/assets/wallpaper3.jpg'
import { useAdmin } from '@/composables/useAdmin'

const route = useRoute()

const { isAdmin, checkAdmin } = useAdmin()
const todoOpen = ref(false)
// 清单面板懒加载：普通访客永远不下载它，管理员不点开也不下载
const TodoPanel = defineAsyncComponent(() => import('@/components/TodoPanel.vue'))
// 桌宠是纯装饰，同样懒加载 —— 谁也不该为了角落里一个小挂件等首屏
const PagePet = defineAsyncComponent(() => import('@/components/PagePet.vue'))
// 带 bare 标记的路由（目前只有后台）自己管布局，不要前台这层壳
const bare = computed(() => route.meta.bare === true)

// 按当前时段挑壁纸。想改分界点就改这里的数字。
function currentWallpaper(): string {
  const hour = new Date().getHours()
  if (hour >= 5 && hour < 16) return wallpaperMorning // 早上（下午也用它）
  if (hour >= 16 && hour < 19) return wallpaperDusk // 傍晚
  return wallpaperNight // 晚上和凌晨
}

function applyWallpaper() {
  // 后台不铺壁纸：它是干活的地方，花哨背景只会干扰读写
  const value = bare.value ? 'none' : `url(${currentWallpaper()})`
  document.documentElement.style.setProperty('--site-bg', value)
}

/* ---------- 返回顶部 ---------- */
const showTop = ref(false)

function onScroll() {
  // 滚过一屏左右才出现 —— 没滚多少时它只会挡视线
  showTop.value = window.scrollY > 400
}

function scrollToTop() {
  // 系统里开了「减少动态效果」就别平滑滚动，直接跳
  const smooth = !window.matchMedia('(prefers-reduced-motion: reduce)').matches
  window.scrollTo({ top: 0, behavior: smooth ? 'smooth' : 'auto' })
}

onMounted(() => {
  applyWallpaper()
  // 本地有令牌才会真的发请求，访客直接跳过
  checkAdmin()
  // 页面一直开着、跨过时段边界时（比如傍晚待到天黑）自动换图
  window.setInterval(applyWallpaper, 5 * 60 * 1000)
  window.addEventListener('scroll', onScroll, { passive: true })
})

onBeforeUnmount(() => window.removeEventListener('scroll', onScroll))

// 从后台切回前台时要重新铺上
watch(bare, applyWallpaper)
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
      <router-link to="/projects">
        <CubeOutline class="svg-icon" />
        项目
      </router-link>

      <!-- 下面两个只有管理员看得到。注意：这只是「界面」——
           真正的保护在后端，清单数据走受鉴权的 /api/admin/todos -->
      <router-link v-if="isAdmin" to="/admin">
        <SettingsOutline class="svg-icon" />
        管理
      </router-link>
      <button v-if="isAdmin" class="nav-btn" @click="todoOpen = !todoOpen">
        <ListOutline class="svg-icon" />
        清单
      </button>
    </nav>

    <TodoPanel v-if="isAdmin" :open="todoOpen" @close="todoOpen = false" />

    <!-- 回到顶部。管理员在首页还多一个「写新文章」的悬浮按钮，
         那个在 HomeView 里，位置往上让开了这里。
         用 class 切换而不是 v-if：v-if 是直接插进 DOM 的，
         元素一出现就是最终状态，淡入动画根本不会跑 -->
    <button
      v-if="!bare"
      class="float-btn to-top"
      :class="{ faded: !showTop }"
      title="回到顶部"
      @click="scrollToTop"
    >
      <ArrowUpOutline class="svg-icon" />
    </button>

    <!-- 角落里的桌宠。同样不显示在后台 —— 那是干活的地方 -->
    <PagePet v-if="!bare" />
    <main :class="{ 'main-bare': bare }">
      <!-- mode="out-in"：旧页面先淡出，新页面再淡入。
           不加的话两个页面会同时存在，高度叠加，滚动条会跳 -->
      <router-view v-slot="{ Component }">
        <Transition name="page" mode="out-in">
          <component :is="Component" />
        </Transition>
      </router-view>
    </main>
  </div>
</template>

<style scoped>
.navbar {
  /* 完全透明的普通文档流元素，跟着页面一起滚 —— 壁纸在这里保持原样，没有任何遮罩。
     这里不能同时又是 sticky：吸顶 + 全透明的话，滚动时正文会从导航底下穿过去，
     文字叠文字根本认不出。两者只能选一个。 */
  display: flex;
  gap: 6px;
  /* 按钮排到右上角 */
  justify-content: flex-end;
  align-items: center;
  /* 管理员比访客多「管理」「清单」两个入口，窄屏上要能换行 */
  flex-wrap: wrap;
  padding: 14px 24px;
  min-height: var(--nav-height);
  box-sizing: border-box;
  background: transparent;
}
.navbar a,
.navbar .nav-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--text);
  text-decoration: none;
  /* button 默认不继承字体，得显式写 */
  font: inherit;
  font-size: 0.95rem;
  padding: 6px 16px;
  /* button 的默认边框和底色要去掉，才能和链接长得一样 */
  border: none;
  background: none;
  border-radius: 6px;
  cursor: pointer;
  /* 底是照片，加一点阴影让文字从背景里浮出来 */
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.75);
  transition: background 0.2s, color 0.2s;
}
.navbar a:hover,
.navbar .nav-btn:hover {
  background: rgba(255, 255, 255, 0.14);
}
.navbar a.router-link-active {
  background: var(--brand);
  color: #fff;
  text-shadow: none;
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

/* 回到顶部的样式在 style.css 的 .float-btn 里（和「写新文章」共用同一套），
   这里只负责它自己的水平位置：贴着右下角 */
.to-top {
  right: 28px;
}
</style>
