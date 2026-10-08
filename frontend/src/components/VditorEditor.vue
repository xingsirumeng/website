<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import Vditor from 'vditor'
import 'vditor/dist/index.css'
import { API_BASE, TOKEN_KEY } from '@/api'

const props = defineProps<{ modelValue: string }>()
const emit = defineEmits<{ 'update:modelValue': [string] }>()

const host = ref<HTMLDivElement | null>(null)
let vditor: Vditor | null = null

// setValue 自己也会触发 input 回调，不加这个守卫会和外部 v-model 来回打架
let syncing = false

onMounted(() => {
  vditor = new Vditor(host.value!, {
    // 自托管资源，由 scripts/copy-vditor.mjs 拷到 public/vditor。
    // 默认指向 unpkg，国内不通时拉不到 Lute 解析器，编辑器会直接白屏。
    // 用 BASE_URL 拼是为了兼容 GitHub Pages 的子目录部署（base: './'）。
    cdn: `${import.meta.env.BASE_URL}vditor`,

    // ir = 即时渲染，边写边成型，体验接近 Typora
    mode: 'ir',
    height: 480,

    // 管理后台必须关：默认会把内容写进 localStorage，
    // 打开旧文章时会先渲染缓存，和外部传进来的正文打架
    cache: { enable: false },

    // 正文代码高亮会去拉 2.1MB 的 highlight.js，而且文章详情页用 marked 渲染、本来就没高亮，
    // 开着只会让「编辑器里花花绿绿、发布出去却是黑白的」前后不一致
    preview: { hljs: { enable: false } },

    // 博客用不到图表、数学公式、录音这些，裁掉减少工具栏干扰
    toolbar: [
      'headings', 'bold', 'italic', 'strike', '|',
      'list', 'ordered-list', 'check', '|',
      'quote', 'line', 'code', 'inline-code', '|',
      'link', 'upload', 'table', '|',
      'undo', 'redo',
    ],

    upload: {
      // 内置上传走原生 XHR，不认 axios 的 baseURL，必须拼绝对地址
      url: `${API_BASE}/api/admin/upload`,
      fieldName: 'file',
      accept: 'image/*',
      max: 5 * 1024 * 1024,
      // 默认的净化规则是 name.replace(/\W/g, '')，会把中文全部剥掉 ——
      // 「屏幕截图.png」会变成只剩「.png」。这里只去掉文件名里真正危险 / 无效的字符。
      filename: (name) => name.replace(/[\\/:*?"<>|\u0000-\u001f]/g, '').trim().slice(0, 60) || 'image',
      // 每次上传前现取令牌，避免登录态刷新后还带着旧的
      setHeaders: () => ({
        Authorization: `Bearer ${localStorage.getItem(TOKEN_KEY) ?? ''}`,
      }),
      // 把后端的 { url } 转成 Vditor 期望的结构，转完它会自动把图片插到光标处。
      // 后端给的是相对地址（环境无关），这里补上 API_BASE 再交给编辑器显示 ——
      // 编辑器不走 preview.transform，相对地址在线上后台会裂图。
      // 注意：不能再配 success 回调 —— 配了就会跳过这个自动插入，得自己 insertValue
      format: (files, responseText) => {
        const res = JSON.parse(responseText)
        const backendName = String(res.url).split('/').pop() || 'image.png'

        // ⚠️ succMap 的 key 不只是个名字 —— Vditor 会取它「最后一个点」后面的部分当文件类型，
        // 只有 .png/.jpg/.gif/.webp 这些开头才会插入 ![alt](url)，否则一律当成普通链接插成
        // [alt](url)，图片就只能点开看、不能直接显示。所以扩展名必须来自后端返回的文件名。
        const ext = backendName.slice(backendName.lastIndexOf('.'))

        // 原始文件名只用来做更好认的 alt 文本，扩展名以后端为准（后端按文件头校验过真实类型）
        const originalName = String(files?.[0]?.name ?? '').replace(/\.[^.]*$/, '')
        const key = originalName ? `${originalName}${ext}` : backendName

        return JSON.stringify({
          code: 0,
          msg: '',
          data: { errFiles: [], succMap: { [key]: `${API_BASE}${res.url}` } },
        })
      },
      error: (msg) => {
        console.error('[Vditor] 图片上传失败:', msg)
      },
    },

    after: () => {
      // 编辑器渲染完成后才能灌入初始内容
      syncing = true
      vditor?.setValue(props.modelValue ?? '')
      syncing = false
    },

    input: (markdown) => {
      if (!syncing) emit('update:modelValue', markdown)
    },
  })
})

onBeforeUnmount(() => {
  // 必须显式销毁：Vditor 会把图标脚本和事件监听挂在全局，不销毁会泄漏
  vditor?.destroy()
  vditor = null
})
</script>

<template>
  <div ref="host" class="vditor-host"></div>
</template>

<style scoped>
.vditor-host {
  /* 让编辑器边框和后台其它输入框的圆角一致 */
  border-radius: 6px;
  overflow: hidden;
}
</style>
