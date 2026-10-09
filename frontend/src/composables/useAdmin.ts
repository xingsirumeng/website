import { ref } from 'vue'
import api, { TOKEN_KEY } from '@/api'

// 模块级的单例：多个组件（顶栏、首页、清单面板）共用同一份状态，
// 整个页面生命周期内只向后端确认一次身份
const isAdmin = ref(false)
let checked = false

/**
 * 管理员身份识别。
 *
 * 注意：这只是**界面层面**的判断，不是安全机制。
 * 真正拦住数据的是后端 —— 管理员才能看的内容必须来自 /api/admin/* 这类受保护的接口，
 * 靠「前端藏起来」是挡不住的，开发者工具里一改就出来了。
 */
export function useAdmin() {
  async function checkAdmin(force = false) {
    if (checked && !force) return
    checked = true

    // 本地压根没令牌，连请求都不用发
    if (!localStorage.getItem(TOKEN_KEY)) {
      isAdmin.value = false
      return
    }

    try {
      // 必须真的调一次接口确认。只看「本地有没有令牌」不行 ——
      // 令牌 12 小时就过期，过期后还以为自己是管理员，点什么都 401
      await api.get('/api/admin/me')
      isAdmin.value = true
    } catch {
      // 令牌无效（拦截器已经把它从本地清掉了），当普通访客处理
      isAdmin.value = false
    }
  }

  return { isAdmin, checkAdmin }
}
