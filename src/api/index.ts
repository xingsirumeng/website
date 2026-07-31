import axios from 'axios'

const api = axios.create({
  baseURL: '/',           // Vite 代理转发到后端
  timeout: 10000,
})

export default api
