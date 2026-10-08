import { API_BASE } from '@/api'

/**
 * 正文里图片存的是相对地址（`/images/xxx.png`）—— 环境无关，
 * 所以本地开发上传的图本地就能看到，发布后又指向正确域名。
 *
 * 但送进编辑器之前必须补全成绝对地址：编辑器（ir / wysiwyg 模式）由 Lute 直接渲染
 * contenteditable，**不走** Vditor 的 preview.transform 钩子（那个只服务于静态的
 * Vditor.preview API）。线上后台在 github.io，相对地址会被解析成
 * github.io/images/... 而裂图。
 */
export function expandImageUrls(markdown: string): string {
  if (!API_BASE) return markdown
  return markdown.replace(/\]\(\/images\//g, `](${API_BASE}/images/`)
}

/** 提交前把绝对地址收回相对地址，保证入库的永远是环境无关的形态 */
export function collapseImageUrls(markdown: string): string {
  if (!API_BASE) return markdown
  return markdown.split(`${API_BASE}/images/`).join('/images/')
}
