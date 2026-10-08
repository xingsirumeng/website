import { marked } from 'marked'
import { API_BASE } from '@/api'

// 文章详情页的 Markdown 渲染。
// 正文里图片存的是相对地址，渲染前补全成当前环境的绝对地址。
// 用 walkTokens 改 token 而不是重写 renderer：不用自己拼 img 标签，也就不用手动处理转义。
marked.use({
  walkTokens(token) {
    if (token.type === 'image' && token.href.startsWith('/images/')) {
      token.href = `${API_BASE}${token.href}`
    }
  },
})

export { marked }
