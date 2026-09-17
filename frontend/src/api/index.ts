import axios from 'axios'

export const TOKEN_KEY = 'blog_token'

const api = axios.create({
  // 本地开发留空，交给 vite.config.ts 里的 /api 代理打到 localhost:8000；
  // 生产构建（GitHub Pages 上没有代理）必须用服务器绝对地址。
  baseURL: import.meta.env.DEV ? '' : 'https://139.196.32.236.nip.io',
  timeout: 10000,
})

// 有登录令牌就自动带上，省得每个调用处手写 header
api.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 令牌过期或无效时清掉本地缓存，由管理页自己回落到登录界面
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem(TOKEN_KEY)
    }
    return Promise.reject(error)
  },
)

export default api
