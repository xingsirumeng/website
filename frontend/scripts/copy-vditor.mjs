// 把 Vditor 需要自托管的资源从 node_modules 拷到 public/vditor。
//
// 为什么要自托管：Vditor 初始化时要去 CDN 拉 Lute 解析器、语言包和图标，
// 默认地址是 unpkg（走 Cloudflare），国内访问不稳定。拉不到 Lute 编辑器直接不可用
// （报 `Lute is not defined`），这不是"少了点功能"而是彻底白屏。
//
// 为什么只拷一部分：整个包 24MB，其中 MathJax 6.5M、Mermaid 3.5M、KaTeX 1.5M、
// highlight.js 2.1M 都是数学公式和图表，博客用不到，而且它们是按需懒加载的。
// 全拷会让 GitHub Pages 的部署体积翻好几倍，所以只搬真正需要的子集（约 3.9MB）。
//
// 由 package.json 的 predev / prebuild 自动触发，产物在 public/vditor（已 gitignore），
// 这样升级 vditor 版本后资源不会过期。
import { cp, mkdir, rm } from 'node:fs/promises'
import { existsSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))
const src = resolve(here, '../node_modules/vditor/dist')
const dest = resolve(here, '../public/vditor/dist')

// lute = Markdown 解析内核，i18n = 语言包，icons = 工具栏图标，这三个是初始化必载
const WANTED = ['js/lute', 'js/i18n', 'js/icons', 'images', 'css']

if (!existsSync(src)) {
  console.error('[copy-vditor] 找不到 node_modules/vditor/dist，请先运行 npm install')
  process.exit(1)
}

await rm(dest, { recursive: true, force: true })
for (const item of WANTED) {
  await mkdir(dirname(resolve(dest, item)), { recursive: true })
  await cp(resolve(src, item), resolve(dest, item), { recursive: true })
}

console.log(`[copy-vditor] 已拷贝 ${WANTED.join(', ')} -> public/vditor`)
