<script setup lang="ts">
import { watch } from 'vue'
import { useRoute } from 'vue-router'

/**
 * Live2D 看板娘（weblive2d）。
 *
 * 和那个 GitHub 仓库用的是同一套：往页面里插一个 CDN 脚本，
 * 它自己会往 <body> 里创建 #waifu 那套 DOM 和 canvas。
 *
 * 这里只做三件它自己不管的事：
 * 1. 只在首页加载（它不知道你用的是 hash 路由的 SPA，切页面不会刷新）
 * 2. 首屏渲染完、浏览器空闲了再注入（不和正文抢带宽）
 * 3. 触屏设备不加载 —— 它自带的判断只有 screen.width >= 768，
 *    但平板/触屏笔记本同样没有「鼠标跟随」的意义
 *
 * 关掉它用它自带的工具栏 quit 按钮，不另做一套。
 */
const route = useRoute()

const CSS_URL = 'https://registry.npmmirror.com/weblive2d/latest/files/waifu.css'
const JS_URL = 'https://registry.npmmirror.com/weblive2d/latest/files/js/autoload.js'

let scheduled = false
let injected = false

function inject() {
  if (injected) return
  injected = true
  // 只注入一次。SPA 里来回切首页不能重复插脚本，
  // 否则会初始化出好几个看板娘叠在一起
  if (document.getElementById('live2d-widget-script')) return

  const link = document.createElement('link')
  link.rel = 'stylesheet'
  link.href = CSS_URL
  document.head.appendChild(link)

  const script = document.createElement('script')
  script.id = 'live2d-widget-script'
  script.async = true
  script.src = JS_URL
  document.body.appendChild(script)
}

function scheduleInject() {
  if (scheduled) return
  // 触屏设备直接跳过。这个判断很便宜，所以每次切到首页重新检查也没关系
  if (!window.matchMedia('(pointer: fine)').matches) return
  scheduled = true

  // requestIdleCallback 会让出主线程，等浏览器闲下来再跑；
  // 浏览器不支持时（Safari 老版本）退回定时器
  const ric = (
    window as unknown as {
      requestIdleCallback?: (cb: () => void, opts?: { timeout: number }) => void
    }
  ).requestIdleCallback

  if (ric) ric(inject, { timeout: 4000 })
  else window.setTimeout(inject, 3000)
}

watch(
  () => route.path,
  (path) => {
    const onHome = path === '/'
    // 看板娘是往 body 里插的固定定位元素，切到别的路由它不会自己消失，
    // 得靠这个类把它藏起来（样式在 style.css 的 .hide-live2d）
    document.documentElement.classList.toggle('hide-live2d', !onHome)
    if (onHome) scheduleInject()
  },
  // immediate：首屏就判断一次，避免刚进来时错误地显示
  { immediate: true },
)
</script>

<template>
  <!-- 纯逻辑组件，不渲染任何东西 —— 看板娘的 DOM 由 CDN 脚本自己创建 -->
</template>
