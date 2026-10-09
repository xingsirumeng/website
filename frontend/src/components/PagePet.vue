<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'

/**
 * 角落里的柴犬小挂件。
 *
 * 性能上的核心约束：**空闲时不能有任何东西在跑**。
 * 所以这里没有 requestAnimationFrame 循环、没有 setInterval 定时眨眼 ——
 * 只有鼠标移动和点击两个事件会触发动作，手一停就彻底静止。
 * （持续跑的动画循环才是这类挂件的真正代价，它让 CPU 永远无法进入空闲，
 * 笔记本上直接反映为续航下降。）
 */
const root = ref<HTMLDivElement | null>(null)
const jumping = ref(false)

// 节流：mousemove 一秒能来上百次，眼睛跟着转不需要那么高的频率
let lastMove = 0
const THROTTLE_MS = 60

// 瞳孔最多偏这么多（SVG 用户单位）。
// 别超过眼睛的半径，否则高光会「跑出眼眶」看着很怪
const MAX_OFFSET = 2

function onMouseMove(event: MouseEvent) {
  const now = performance.now()
  if (now - lastMove < THROTTLE_MS) return
  lastMove = now

  const el = root.value
  if (!el) return

  const rect = el.getBoundingClientRect()
  const dx = event.clientX - (rect.left + rect.width / 2)
  const dy = event.clientY - (rect.top + rect.height / 2)
  // 归一化成单位方向再乘最大位移 —— 只用方向不用距离，
  // 否则鼠标离得越远瞳孔偏得越狠
  const distance = Math.hypot(dx, dy) || 1

  // 直接写 CSS 变量，不经过 Vue 的响应式：
  // 这里每秒更新十几次，走响应式等于让 Vue 白白重渲染十几次
  el.style.setProperty('--look-x', `${(dx / distance) * MAX_OFFSET}px`)
  el.style.setProperty('--look-y', `${(dy / distance) * MAX_OFFSET}px`)
}

// 鼠标移出窗口时把眼睛转回来
function resetLook() {
  const el = root.value
  if (!el) return
  el.style.setProperty('--look-x', '0px')
  el.style.setProperty('--look-y', '0px')
}

function jump() {
  // 上一次还没跳完就先不管，避免连点导致动画重置、看起来卡住
  if (jumping.value) return
  jumping.value = true
}

function onJumpEnd() {
  jumping.value = false
}

const onLeave = () => resetLook()

onMounted(() => {
  // passive 告诉浏览器这个监听器不会调 preventDefault，滚动时不必等它
  window.addEventListener('mousemove', onMouseMove, { passive: true })
  document.addEventListener('mouseleave', onLeave)
})

onBeforeUnmount(() => {
  window.removeEventListener('mousemove', onMouseMove)
  document.removeEventListener('mouseleave', onLeave)
})
</script>

<template>
  <!-- 纯装饰，对屏幕阅读器隐藏 -->
  <div
    ref="root"
    class="pet"
    :class="{ jumping }"
    aria-hidden="true"
    title="点一下"
    @click="jump"
    @animationend="onJumpEnd"
  >
    <svg class="pet-svg" viewBox="0 0 64 64">
      <!-- 耳朵（画在头后面，所以先写） -->
      <path class="fur" d="M15 26 L11 5 L29 18 Z" />
      <path class="fur" d="M49 26 L53 5 L35 18 Z" />
      <path class="inner-ear" d="M17 23 L15 11 L25 19 Z" />
      <path class="inner-ear" d="M47 23 L49 11 L39 19 Z" />

      <!-- 头 -->
      <ellipse class="fur" cx="32" cy="37" rx="22" ry="20" />

      <!-- 腮红 -->
      <circle class="blush" cx="15" cy="42" r="3.4" />
      <circle class="blush" cx="49" cy="42" r="3.4" />

      <!-- 口鼻：奶白色那块，柴犬最明显的特征之一 -->
      <ellipse class="muzzle" cx="32" cy="46" rx="12" ry="9.5" />

      <!-- 鼻子 -->
      <ellipse class="nose" cx="32" cy="42" rx="3.2" ry="2.3" />

      <!-- 嘴：柴犬标志性的「ω」形 -->
      <path class="mouth" d="M26.5 47.5 Q29.3 51 32 47.5 Q34.7 51 37.5 47.5" />

      <!-- 眼睛。深色眼 + 会动的高光点，比「白眼球 + 黑瞳孔」更像狗 -->
      <ellipse class="eye" cx="23" cy="33" rx="3.6" ry="4.2" />
      <ellipse class="eye" cx="41" cy="33" rx="3.6" ry="4.2" />
      <!-- 高光位置由 --look-x / --look-y 控制 -->
      <circle class="glint" cx="24" cy="31.8" r="1.3" />
      <circle class="glint" cx="42" cy="31.8" r="1.3" />
    </svg>
  </div>
</template>

<style scoped>
.pet {
  position: fixed;
  /* 左下角。右边那两个悬浮按钮（回到顶部、写新文章）都在右下角，
     放这边就完全不用考虑避让 */
  left: 28px;
  bottom: 28px;
  z-index: 40;
  /* 大小就改这两个数。SVG 是矢量的，放大不会糊 */
  width: 88px;
  height: 88px;
  cursor: pointer;
  /* 用 filter 而不是 box-shadow，因为 SVG 是不规则形状 */
  filter: drop-shadow(0 6px 14px rgba(0, 0, 0, 0.45));
  transition: transform 0.15s ease-out;
}
.pet:hover {
  transform: scale(1.06);
}

.pet-svg {
  width: 100%;
  height: 100%;
  display: block;
}

/* 柴犬的自然配色。这里没用品牌绿 ——
   它是一个角色，不是界面元素，画成绿狗会很怪 */
.fur {
  fill: #e0913f;
}
.inner-ear {
  fill: #c2703a;
}
.muzzle {
  fill: #fbf3e8;
}
.blush {
  fill: #ff8b7a;
  opacity: 0.55;
}
.nose {
  fill: #2a2018;
}
.eye {
  fill: #2a2018;
}
.mouth {
  fill: none;
  stroke: #2a2018;
  stroke-width: 1.6;
  stroke-linecap: round;
}

.glint {
  fill: #fff;
  /* 过渡让跟随看起来是「转过去」而不是「跳过去」。
     只有值变化时才跑，鼠标停下就完全静止 */
  transition: transform 0.12s ease-out;
  transform: translate(var(--look-x, 0px), var(--look-y, 0px));
}

/* 点击时跳一下 */
.pet.jumping {
  animation: pet-jump 0.5s ease;
}
@keyframes pet-jump {
  0%,
  100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-14px) rotate(-6deg);
  }
  60% {
    transform: translateY(-4px) rotate(4deg);
  }
}

/* 系统开了「减少动态效果」就只保留最必要的反馈 */
@media (prefers-reduced-motion: reduce) {
  .pet,
  .glint {
    transition: none;
  }
  .pet.jumping {
    animation: none;
  }
  .pet:hover {
    transform: none;
  }
}

/* 手机上藏起来 —— 小屏幕里它会盖住正文。
   pointer: coarse 是更准的判断：触屏设备没有「鼠标跟随」这回事，
   它在那里只是个挡住文字的装饰 */
@media (max-width: 640px), (pointer: coarse) {
  .pet {
    display: none;
  }
}
</style>
